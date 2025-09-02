"""
CUA Client Reset Command

This module provides the reset functionality for the CUA client,
which runs the PowerShell reset script on Windows systems.
"""

import platform
import subprocess
import sys

# ---------------------------------------------------------------------------
# Console-encoding safety: make sure prints do not crash on non-UTF-8 codepages
# ---------------------------------------------------------------------------
if hasattr(sys.stdout, "reconfigure"):
    try:
        # Force UTF-8 with graceful replacement to avoid UnicodeEncodeError on cp1252
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        # If reconfigure is not supported or fails, we continue and later
        # replace problematic characters in the messages.
        pass

# Helper: privilege-safe print that strips emoji if encoding unsupported
_encode_test = ("✅").encode(sys.stdout.encoding or "ascii", errors="ignore").decode(sys.stdout.encoding or "ascii", errors="ignore")
_USE_EMOJI = "✅" in _encode_test  # emojis survive encoding roundtrip?

def _msg(txt: str, fallback: str):
    """Print *txt* if console supports it, otherwise *fallback*."""
    if _USE_EMOJI:
        print(txt)
    else:
        print(fallback)

try:
    from importlib import resources
except ImportError:
    # Fallback for Python < 3.9
    import importlib_resources as resources


def reset_cli():
    """CLI entry point for the cua-client-reset command"""
    try:
        # Check if we're on Windows
        if platform.system() != "Windows":
            _msg("❌ The reset script is only available on Windows systems.",
                 "ERROR: The reset script is only available on Windows systems.")
            _msg("💡 This command runs PowerShell scripts designed for Windows environments.",
                 "INFO: This command runs PowerShell scripts designed for Windows environments.")
            sys.exit(1)
        
        # Find the PowerShell script using importlib.resources
        try:
            script_files = resources.files('cua_client.windows')
            script_path = script_files / 'reset_cua_client.ps1'
            
            # Convert to actual file path and execute
            with resources.as_file(script_path) as script_file:
                _msg("🔄 Running CUA Client Reset Script...", "Running CUA Client Reset Script...")
                print(f"Script location: {script_file}")
                
                # Execute PowerShell script
                cmd = [
                    "PowerShell.exe",
                    "-ExecutionPolicy", "Bypass",
                    "-File", str(script_file)
                ]
                
                _msg("🚀 Executing command", "Executing command")
                print(" ", ' '.join(cmd))
                result = subprocess.run(cmd, capture_output=False, text=True)
                
                if result.returncode == 0:
                    _msg("✅ Reset script completed successfully!", "Reset script completed successfully.")
                else:
                    _msg("❌ Reset script failed with exit code:", "Reset script failed with exit code:")
                    print(f" {result.returncode}")
                    sys.exit(result.returncode)
                    
        except Exception as e:
            _msg("❌ Error locating or running reset script:", "Error locating or running reset script:")
            print(f" {e}")
            _msg("💡 Make sure the cua-client package is properly installed.", "INFO: Make sure the cua-client package is properly installed.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        _msg("\n⚠️ Reset script interrupted by user", "Reset script interrupted by user")
        sys.exit(1)
    except Exception as e:
        _msg("❌ Unexpected error:", "Unexpected error:")
        print(f" {e}")
        sys.exit(1)


if __name__ == "__main__":
    reset_cli() 