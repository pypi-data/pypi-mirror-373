import asyncio
import json
import logging
import inspect
import functools
from typing import Dict, Any, Callable, Optional, List
import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException
from pydantic import BaseModel

# Set up logging
logger = logging.getLogger(__name__)

class ServerToClientMessage(BaseModel):
    call_id: str
    function_name: str
    args: dict
    
class ClientToServerMessage(BaseModel):
    call_id: str
    success: bool
    result: dict


class RemoteFunctionRouter:
    """Router for organizing remote functions, similar to FastAPI router"""
    
    def __init__(self, prefix: str = "", tags: List[str] = None):
        self.prefix = prefix
        self.tags = tags or []
        self.functions: Dict[str, Callable] = {}
    
    def function(self, name: str = None, *, tags: List[str] = None):
        """Decorator to register a function with this router
        
        Usage:
            router = RemoteFunctionRouter()
            
            @router.function()  # Uses function name
            def my_function():
                pass
                
            @router.function("custom_name")  # Uses custom name
            def my_function():
                pass
                
            @router.function(tags=["math", "utils"])  # With tags
            def my_function():
                pass
        """
        def decorator(func: Callable) -> Callable:
            function_name = name if name is not None else func.__name__
            
            # Apply prefix if configured
            if self.prefix:
                full_name = f"{self.prefix}.{function_name}"
            else:
                full_name = function_name
            
            # Store function with metadata
            self.functions[full_name] = func
            
            # Add tags metadata to function
            if hasattr(func, '_remote_tags'):
                func._remote_tags.extend(tags or [])
                func._remote_tags.extend(self.tags)
            else:
                func._remote_tags = (tags or []) + self.tags
            
            logger.debug(f"Registered function '{full_name}' with router")
            return func
        return decorator
    
    def get_functions(self) -> Dict[str, Callable]:
        """Get all functions registered with this router"""
        return self.functions.copy()


class RemoteFunctionClient:
    def __init__(self, server_url: str, agent_id: int, secret_key: str, reconnect_interval: float = 3.0):
        self.server_url = server_url
        self.agent_id = agent_id
        self.secret_key = secret_key
        self.reconnect_interval = reconnect_interval
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.functions: Dict[str, Callable] = {}
        self._running = False
        self._should_reconnect = True
        
    def register_function(self, function_name: str, function: Callable):
        """Register a function that can be called by the server"""
        self.functions[function_name] = function
        logger.info(f"Registered function: {function_name}")
    
    def include_router(self, router: RemoteFunctionRouter):
        """Include all functions from a router, similar to FastAPI's app.include_router()
        
        Usage:
            router = RemoteFunctionRouter(prefix="math")
            client.include_router(router)
        """
        router_functions = router.get_functions()
        for function_name, function in router_functions.items():
            self.register_function(function_name, function)
        
        logger.info(f"Included router with {len(router_functions)} functions")
    
    def remote_function(self, name: Optional[str] = None):
        """Instance method decorator to register a function for remote calls
        
        Usage:
            @client.remote_function()  # Uses function name
            def my_function():
                pass
                
            @client.remote_function("custom_name")  # Uses custom name
            def my_function():
                pass
        """
        def decorator(func: Callable) -> Callable:
            function_name = name if name is not None else func.__name__
            self.register_function(function_name, func)
            return func
        return decorator
    
    def get_registered_function_names(self) -> List[str]:
        """Get list of all registered function names"""
        return list(self.functions.keys())
    
    async def _execute_function(self, function: Callable, /, **kwargs) -> Any:
        """Execute a registered function, supporting both async and sync callables.
        
        - If the function is async, await it directly.
        - If the function is sync (potentially blocking), run it in a thread executor.
        """
        try:
            if inspect.iscoroutinefunction(function):
                return await function(**kwargs)
            loop = asyncio.get_running_loop()
            bound_call = functools.partial(function, **kwargs)
            return await loop.run_in_executor(None, bound_call)
        except Exception:
            # Let caller wrap into error payload; preserve original exception text
            raise
    
    async def connect(self):
        """Connect to the WebSocket server"""
        url = f"{self.server_url}/ws/function_calls/{self.agent_id}"
        try:
            if self.websocket:
                await self.websocket.close()
                self.websocket = None
            
            # Add custom header with VM secret key for authentication
            headers = {
                "X-Secret-Key": self.secret_key
            }
            
            # Increase max_size to 200MB (default is 1MB) to allow large frames
            self.websocket = await websockets.connect(
                url,
                additional_headers=headers,
                max_size=200 * 1024 * 1024  # 200MB
            )
            logger.info(f"Connected to server at {url}")
            return True
        except Exception as e:
            logger.debug(f"Failed to connect to server: {e}")
            self.websocket = None
            return False
    
    async def handle_function_call(self, message: Dict[str, Any]):
        """Handle incoming function call from server"""
        try:
            # Parse the message
            server_message = ServerToClientMessage(**message)
            
            logger.debug(f"Received function call: {server_message.function_name} with call_id: {server_message.call_id}")
            
            success = False
            # Execute the function
            if server_message.function_name in self.functions:
                try:
                    # Call the registered function (off-loading if blocking)
                    result = await self._execute_function(
                        self.functions[server_message.function_name], **server_message.args
                    )
                    # If result is not a dict, wrap it
                    if not isinstance(result, dict):
                        result = {"result": result}
                    success = True
                except Exception as func_error:
                    logger.error(f"Error executing function {server_message.function_name}: {func_error}")
                    result = {"error": str(func_error)}
            else:
                logger.error(f"Unknown function: {server_message.function_name}")
                result = {"error": f"Unknown function: {server_message.function_name}"}
            
            # Send result back to server
            response = ClientToServerMessage(
                call_id=server_message.call_id,
                success=success,
                result=result
            )
            
            if self.websocket:
                await self.websocket.send(response.model_dump_json())
                logger.debug(f"Sent result for call_id: {server_message.call_id}")
            
        except Exception as e:
            logger.error(f"Error handling function call: {e}")
    
    async def listen(self):
        """Listen for incoming messages from server"""
        try:
            while self._running and self.websocket:
                try:
                    message_str = await self.websocket.recv()
                    logger.debug(f"Received raw message: {message_str[:500]}")
                    
                    try:
                        message = json.loads(message_str)
                        await self.handle_function_call(message)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON message: {e}")
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        
                except ConnectionClosed:
                    logger.info("Connection closed by server")
                    return False  # Signal that connection was lost
                except WebSocketException as e:
                    logger.warning(f"WebSocket error: {e}")
                    return False  # Signal that connection was lost
                except Exception as e:
                    logger.error(f"Error in listen loop: {e}")
                    return False  # Signal that connection was lost
                    
        except Exception as e:
            logger.error(f"Error in listen method: {e}")
            return False
        
        return True  # Normal exit
    
    async def run(self):
        """Main run method - connect and listen for messages with automatic reconnection"""
        try:
            self._running = True
            self._should_reconnect = True
            
            logger.info(f"Starting RemoteFunctionClient for agent {self.agent_id}")
            
            while self._running and self._should_reconnect:
                # Attempt to connect
                logger.info("Attempting to connect to server...")
                connected = await self.connect()
                
                if not connected:
                    if self._running and self._should_reconnect:
                        logger.warning(f"Connection failed, retrying in {self.reconnect_interval} seconds...")
                        await asyncio.sleep(self.reconnect_interval)
                    continue
                
                logger.info("Connected successfully, starting to listen for messages...")
                
                # Listen for messages
                listen_result = await self.listen()
                
                # If listen returned False, connection was lost
                if not listen_result and self._running and self._should_reconnect:
                    logger.warning(f"Connection lost, reconnecting in {self.reconnect_interval} seconds...")
                    await asyncio.sleep(self.reconnect_interval)
                elif listen_result:
                    # Normal exit from listen (should_reconnect or _running became False)
                    logger.info("Listen loop exited normally")
                    break
                    
        except KeyboardInterrupt:
            logger.info("Client interrupted by user")
            self._should_reconnect = False
        except Exception as e:
            logger.error(f"Client error: {e}")
        finally:
            await self.close()
    
    async def close(self):
        """Close the WebSocket connection and stop reconnection attempts"""
        logger.info("Shutting down RemoteFunctionClient...")
        self._running = False
        self._should_reconnect = False
        
        if self.websocket:
            try:
                await self.websocket.close()
                logger.info("WebSocket connection closed")
            except Exception as e:
                logger.debug(f"Error closing WebSocket: {e}")
            finally:
                self.websocket = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        # For context manager, we don't want automatic reconnection
        # Just connect once
        self._should_reconnect = False
        success = await self.connect()
        if not success:
            raise ConnectionError("Failed to connect to server")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()