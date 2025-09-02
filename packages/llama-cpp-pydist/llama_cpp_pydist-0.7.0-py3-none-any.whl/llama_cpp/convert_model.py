import subprocess
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

LLAMA_CPP_SUBMODULE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "vendor_llama_cpp_pydist", "llama.cpp"))
CONVERSION_SCRIPT_PATH = os.path.join(LLAMA_CPP_SUBMODULE_PATH, "convert_hf_to_gguf.py")

def convert_hf_to_gguf(model_path_or_name: str, output_dir: str, output_filename: str = None, outtype: str = "f16", use_temp_dir: bool = False):
    """
    Converts a Hugging Face model (potentially using safetensors) to GGUF format.

    This function calls the convert_hf_to_gguf.py script from the llama.cpp submodule.
    Make sure you have the necessary conversion libraries installed. You can use
    `from llama_cpp.install_conversion_libs import install_conversion_libs; install_conversion_libs()`

    Args:
        model_path_or_name (str): The path to the local Hugging Face model directory or the model name
                                  from Hugging Face Hub (e.g., "meta-llama/Llama-2-7b-hf").
        output_dir (str): The directory where the GGUF file will be saved.
        output_filename (str, optional): The desired name for the output GGUF file.
                                         If None, a name will be derived from the model name.
        outtype (str, optional): The quantization type for the output GGUF file (e.g., "f16", "q8_0").
                                 Defaults to "f16".
        use_temp_dir (bool, optional): If True, a temporary directory will be used for intermediate files.
                                       Defaults to False.

    Returns:
        tuple[bool, str]: A tuple containing:
                            - bool: True if conversion was successful, False otherwise.
                            - str: Path to the generated GGUF file if successful, else an error message.
    """
    if not os.path.exists(CONVERSION_SCRIPT_PATH):
        error_msg = f"Conversion script not found at {CONVERSION_SCRIPT_PATH}"
        logging.error(error_msg)
        return False, error_msg

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        logging.info(f"Created output directory: {output_dir}")

    if output_filename is None:
        # Derive a filename if not provided
        sanitized_model_name = model_path_or_name.split('/')[-1].replace('-', '_')
        output_filename = f"{sanitized_model_name}_{outtype}.gguf"
    
    output_gguf_path = os.path.join(output_dir, output_filename)

    command = [
        sys.executable, # Use the current Python interpreter
        CONVERSION_SCRIPT_PATH,
        model_path_or_name,
        "--outfile", output_gguf_path,
        "--outtype", outtype
    ]
    if use_temp_dir:
        command.append("--tmpdir") # The script might create a temp dir itself or expect one

    logging.info(f"Starting GGUF conversion for model: {model_path_or_name}")
    logging.info(f"Output GGUF: {output_gguf_path}")
    logging.info(f"Conversion command: {' '.join(command)}")

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=LLAMA_CPP_SUBMODULE_PATH)
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            logging.info(f"Successfully converted model to GGUF: {output_gguf_path}")
            logging.info("Conversion script stdout:")
            for line in stdout.splitlines():
                logging.info(line)
            if stderr:
                logging.warning("Conversion script stderr (though process succeeded):")
                for line in stderr.splitlines():
                    logging.warning(line)
            return True, output_gguf_path
        else:
            error_msg = f"GGUF conversion failed with return code {process.returncode}."
            logging.error(error_msg)
            logging.error("Conversion script stdout:")
            for line in stdout.splitlines():
                logging.error(line)
            logging.error("Conversion script stderr:")
            for line in stderr.splitlines():
                logging.error(line)
            return False, f"{error_msg}\\nStderr:\\n{stderr}"

    except FileNotFoundError:
        error_msg = f"Error: The Python interpreter '{sys.executable}' or the script '{CONVERSION_SCRIPT_PATH}' was not found."
        logging.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"An unexpected error occurred during GGUF conversion: {e}"
        logging.error(error_msg)
        return False, error_msg

if __name__ == '__main__':
    # Example Usage (for testing this script directly)
    # Make sure you have a model downloaded, e.g., using:
    # git lfs install
    # git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0 /tmp/TinyLlama-1.1B-Chat-v1.0
    
    # Test with a local path
    # model_to_convert = "/tmp/TinyLlama-1.1B-Chat-v1.0" # Replace with your model path
    # output_directory = "./converted_models"
    
    # Or test with a Hugging Face model name (requires internet and will download)
    model_to_convert = "TinyLlama/TinyLlama-1.1B-Chat-v1.0" # A small model for quick testing
    output_directory = os.path.join(os.path.dirname(__file__), "..", "tests", "converted_models_output")


    logging.info("Attempting to install conversion libraries first...")
    try:
        from llama_cpp.install_conversion_libs import install_conversion_libs
        if install_conversion_libs():
            logging.info("Conversion libraries installed/verified successfully.")
        else:
            logging.warning("Failed to install/verify conversion libraries. Conversion might fail.")
    except ImportError:
        logging.warning("Could not import install_conversion_libs. Make sure it's in the llama_cpp package.")
        logging.warning("Proceeding with conversion attempt, but it may fail if dependencies are missing.")


    success, result_path_or_msg = convert_hf_to_gguf(
        model_path_or_name=model_to_convert,
        output_dir=output_directory,
        outtype="q8_0" # Example: 8-bit quantization
    )

    if success:
        print(f"Test conversion successful! GGUF file at: {result_path_or_msg}")
    else:
        print(f"Test conversion failed: {result_path_or_msg}")
