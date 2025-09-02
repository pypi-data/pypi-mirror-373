# CUA Client

**Computer Use Automation (CUA) Client** - A Python package for remote function execution and computer automation tasks via WebSocket connections.

## Features

- **Remote Function Execution**: Connect to remote servers and execute functions over WebSocket
- **Computer Use Automation**: Automate mouse, keyboard, and screen interactions
- **Flexible Configuration**: Environment-based configuration with validation
- **Async Support**: Built with asyncio for high-performance concurrent operations
- **Extensible**: Easy to add custom functions and routers

## Installation

```bash
pip install cua-client
```

## Quick Start

### 1. Set Environment Variables

```bash
export REMOTE_FUNCTION_URL="ws://your-server.com/ws"
export AGENT_ID="123"
export SECRET_KEY="your-secret-key"
```

### 2. Run the Client

```bash
# As a command-line tool
cua-client

# Or programmatically
python -m cua_client.main
```

### 3. Programmatic Usage

```python
import asyncio
from cua_client import RemoteFunctionClient, RemoteFunctionRouter

# Create a custom router
my_router = RemoteFunctionRouter(tags=["custom"])

@my_router.function("greet")
def greet(name: str) -> str:
    return f"Hello, {name}!"

# Set up the client
async def main():
    client = RemoteFunctionClient(
        remote_function_url="ws://your-server.com/ws",
        agent_id=123,
        secret_key="your-secret-key"
    )
    
    # Add your custom router
    client.include_router(my_router)
    
    # Run the client
    await client.run()

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

The client requires three environment variables:

- `REMOTE_FUNCTION_URL`: WebSocket server URL (e.g., `ws://localhost:8000/ws`)
- `AGENT_ID`: Unique identifier for the client agent (integer)
- `SECRET_KEY`: Authentication secret key

## Built-in Functions

### Computer Use Functions

The client comes with built-in computer automation capabilities:

- **Screen capture**: Take screenshots and analyze screen content
- **Mouse control**: Click, drag, and move mouse cursor
- **Keyboard input**: Type text and send key combinations
- **Window management**: Focus windows and manage applications

### Basic Functions

- `print`: Simple message printing function for testing

## Advanced Usage

### Custom Function Registration

```python
from cua_client import RemoteFunctionClient

client = RemoteFunctionClient(url, agent_id, secret_key)

# Register a single function
def my_function(param: str) -> str:
    return f"Processed: {param}"

client.register_function("my_func", my_function)

# Or use a router for organized function groups
router = RemoteFunctionRouter(tags=["data"])

@router.function("process_data")
def process_data(data: dict) -> dict:
    # Your processing logic here
    return {"result": "processed", "original": data}

client.include_router(router)
```

### Error Handling

```python
try:
    await client.run()
except ConnectionError:
    print("Failed to connect to server")
except KeyboardInterrupt:
    print("Client stopped by user")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Security Considerations

- Always use secure WebSocket connections (`wss://`) in production
- Keep your `SECRET_KEY` confidential and rotate it regularly
- Validate all inputs in your custom functions
- Run the client with minimal required permissions

## Dependencies

- `pydantic>=1.8.0`: Data validation and configuration
- `websockets>=10.0`: WebSocket client implementation
- `pynput>=1.7.0`: Mouse and keyboard control
- `Pillow>=8.0.0`: Image processing for screenshots
- `pyautogui>=0.9.50`: GUI automation utilities

## Development

### Installation for Development

```bash
# Clone the repository
git clone https://github.com/168x/cua-client.git
cd cua-client

# Install in development mode
pip install -e .[dev]
```

### Building and Publishing

Use the provided script to build and publish the package:

```bash
# Make the script executable
chmod +x publish.sh

# Run the interactive publish script
./publish.sh
```

The script will:
- Show current version and suggest increments
- Update version in all necessary files
- Build the package
- Validate the build
- Optionally publish to PyPI or Test PyPI

See `PUBLISH_USAGE.md` for detailed usage instructions.

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
flake8 src/
mypy src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- Report bugs: [GitHub Issues](https://github.com/168x/cua-client/issues)
- Documentation: [GitHub README](https://github.com/168x/cua-client#readme)
- Discussions: [GitHub Discussions](https://github.com/168x/cua-client/discussions)

## Changelog

### v0.1.0

- Initial release
- Basic remote function execution
- Computer use automation features
- WebSocket-based communication
- Environment-based configuration 