import sys
import subprocess

# Detect pip internal API for programmatic installation
try:
    from pip._internal.cli.main import main as pip_main
except ImportError:
    try:
        from pip import main as pip_main
    except ImportError:
        pip_main = None

# List of required python libraries and their versions for HF to GGUF conversion
REQUIRED_CONVERSION_LIBRARIES = [
    "transformers",
    "numpy",
    "torch",
    "safetensors",
    "sentencepiece",
]

def install_conversion_libs():
    """
    Installs all python libraries required to invoke the HF to GGUF conversion script.

    Returns:
        bool: True if all installations succeed, False otherwise.
    """
    success = True
    for package in REQUIRED_CONVERSION_LIBRARIES:
        try:
            print(f"Installing {package}...")
            if pip_main:
                ret = pip_main(["install", package])
                if ret != 0:
                    raise RuntimeError(f"pip installation failed with exit code {ret}")
            else:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except Exception as e:
            print(f"Failed to install {package}: {e}")
            success = False
    return success
