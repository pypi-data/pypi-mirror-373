import os
import zipfile

# Path to the directory where binaries are stored within the module
_BINARIES_DIR = os.path.join(os.path.dirname(__file__), 'binaries')

def deploy_windows_binary(target_directory):
    """
    Deploys the Windows binary (if available) from the package to the specified target directory.

    Args:
        target_directory (str): The directory where the Windows binary should be unzipped.

    Returns:
        bool: True if deployment was successful or if no binary was found (no action needed),
              False if an error occurred during deployment.

    Raises:
        FileNotFoundError: If the target_directory does not exist and cannot be created.
        PermissionError: If there are permission issues writing to the target_directory.
    """
    if not os.path.exists(_BINARIES_DIR):
        print("Binaries directory not found in module. No Windows binary to deploy.")
        return True  # No action needed

    binary_zip_files = [f for f in os.listdir(_BINARIES_DIR) if f.startswith('llama-') and f.endswith('-win-cpu-x64.zip')]

    if not binary_zip_files:
        print("No Windows binary zip file found in the module binaries directory.")
        return True  # No action needed

    if len(binary_zip_files) > 1:
        print(f"Warning: Multiple Windows binary zip files found: {binary_zip_files}. Using the first one: {binary_zip_files[0]}")

    binary_zip_path = os.path.join(_BINARIES_DIR, binary_zip_files[0])

    if not os.path.exists(target_directory):
        try:
            os.makedirs(target_directory, exist_ok=True)
            print(f"Created target directory: {target_directory}")
        except OSError as e:
            print(f"Error: Could not create target directory {target_directory}: {e}")
            raise FileNotFoundError(f"Could not create target directory: {target_directory}") from e

    print(f"Deploying Windows binary from {binary_zip_path} to {target_directory}...")

    try:
        with zipfile.ZipFile(binary_zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_directory)
        print(f"Successfully unzipped Windows binary to {target_directory}")
        return True
    except zipfile.BadZipFile:
        print(f"Error: The file {binary_zip_path} is not a valid zip file or is corrupted.")
        return False
    except PermissionError as e:
        print(f"Error: Permission denied when trying to extract to {target_directory}. {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred during unzipping: {e}")
        return False
