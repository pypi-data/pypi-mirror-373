# Llama CPP

This is a Python package for Llama CPP ( https://github.com/ggml-org/llama.cpp ).

## Installation

You can install the pre-built wheel from the releases page or build it from source.

```bash
pip install llama-cpp-pydist
```

## Usage

This section provides a basic overview of how to use the `llama_cpp_pydist` library.

### Deploying Windows Binaries

If you are on Windows, the package attempts to automatically deploy pre-compiled binaries. You can also manually trigger this process.

```python
from llama_cpp import deploy_windows_binary

# Specify the target directory for the binaries
# This is typically within your Python environment's site-packages
# or a custom location if you prefer.
target_dir = "./my_llama_cpp_binaries" 

if deploy_windows_binary(target_dir):
    print(f"Windows binaries deployed successfully to {target_dir}")
else:
    print(f"Failed to deploy Windows binaries or no binaries were found for your system.")

# Once deployed, you would typically add the directory containing llama.dll (or similar)
# to your system's PATH or ensure your application can find it.
# For example, if llama.dll is in target_dir/bin:
# import os
# os.environ["PATH"] += os.pathsep + os.path.join(target_dir, "bin")
```

## Conversion Library Installation

To perform Hugging Face to GGUF model conversions, you need to install additional Python libraries. You can install them via pip:

```bash
pip install transformers numpy torch safetensors sentencepiece
```

Alternatively, you can install them programmatically in Python:

```python
from llama_cpp.install_conversion_libs import install_conversion_libs

if install_conversion_libs():
    print("Conversion libraries installed successfully.")
else:
    print("Failed to install conversion libraries.")
```

### Converting Hugging Face Models to GGUF

This package provides a utility to convert Hugging Face models (including those using Safetensors) into the GGUF format, which is used by `llama.cpp`. This process leverages the conversion scripts from the underlying `llama.cpp` submodule.

**1. Install Conversion Libraries:**

Before converting models, ensure you have the necessary Python libraries. You can install them using a helper function:

```python
from llama_cpp import install_conversion_libs

if install_conversion_libs():
    print("Conversion libraries installed successfully.")
else:
    print("Failed to install conversion libraries. Please check the output for errors.")
```

**2. Convert the Model:**

Once the dependencies are installed, you can use the `convert_hf_to_gguf` function:

```python
from llama_cpp import convert_hf_to_gguf

# Specify the Hugging Face model name or local path
model_name_or_path = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # Example: A small model from Hugging Face Hub
# Or, a local path: model_name_or_path = "/path/to/your/hf_model_directory"

output_directory = "./converted_gguf_models" # Directory to save the GGUF file
output_filename = "tinyllama_1.1b_chat_q8_0.gguf" # Optional: specify a filename
quantization_type = "q8_0"  # Example: 8-bit quantization. Common types: "f16", "q4_0", "q4_K_M", "q5_K_M", "q8_0"

print(f"Starting conversion for model: {model_name_or_path}")
success, result_message = convert_hf_to_gguf(
    model_path_or_name=model_name_or_path,
    output_dir=output_directory,
    output_filename=output_filename, # Can be None to auto-generate
    outtype=quantization_type
)

if success:
    print(f"Model converted successfully! GGUF file saved at: {result_message}")
else:
    print(f"Model conversion failed: {result_message}")

# The `result_message` will contain the path to the GGUF file on success,
# or an error message on failure.
```

This function will download the model from Hugging Face Hub if a model name is provided and it's not already cached locally by Hugging Face `transformers`. It then invokes the `convert_hf_to_gguf.py` script from `llama.cpp`.

For more detailed examples and advanced usage, please refer to the documentation of the underlying `llama.cpp` project and explore the examples provided there.

## Building and Development

For instructions on how to build the package from source, update the `llama.cpp` submodule, or other development-related tasks, please see [BUILDING.md](./BUILDING.md).
