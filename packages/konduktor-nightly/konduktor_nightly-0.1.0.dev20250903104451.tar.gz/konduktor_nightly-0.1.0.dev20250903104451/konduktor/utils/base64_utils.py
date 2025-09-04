"""
Utility for (un)zip and encode/decoding k8s secrets in base64
"""

import base64
import os
import shutil
import tempfile
import zipfile
from typing import List


def zip_base64encode(files: List[str]) -> str:
    """Zips files and encodes them in base64.

    Args:
        files: List of file paths to zip. Can include files and directories.

    Returns:
        Base64 encoded string of the zipped files.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Copy all files/directories to temp dir preserving structure
        for file_path in files:
            src_path = os.path.expanduser(file_path)
            if not os.path.exists(src_path):
                continue
            dst_path = os.path.join(temp_dir, os.path.basename(file_path))

            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)

        # Create zip file
        zip_path = os.path.join(temp_dir, 'archive.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for item in os.listdir(temp_dir):
                if item == 'archive.zip':
                    continue
                item_path = os.path.join(temp_dir, item)
                if os.path.isfile(item_path):
                    zipf.write(item_path, item)
                else:
                    for root, _, files in os.walk(item_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            zipf.write(file_path, arcname)

        # Read and encode zip file
        with open(zip_path, 'rb') as f:
            zip_str = f.read()
            secret_value = base64.b64encode(zip_str).decode('utf-8')
            # print("encoding")
            # print(type(secret_value))
            # print(len(secret_value))
            # print(secret_value[-20:])
            return secret_value


def base64decode_unzip(secret_value: str, output_path: str) -> str:
    """Decodes a base64 encoded string and unzips the files.

    Args:
        secret_value: Base64 encoded string of the zipped files.
        output_path: Path where to extract the unzipped files.

    Returns:
        Path to the unzipped files.
    """
    # TODO(asaiacai): this is messy I know...
    # Decode base64 string
    # print("decoding")
    # print(type(secret_value))
    # print(len(secret_value))
    # print(secret_value[-20:])
    decoded_data = base64.b64decode(secret_value)

    # Write decoded data to temporary zip file
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, 'archive.zip')

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.writestr('data.zip', decoded_data)

        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(path=output_path)

        with zipfile.ZipFile(os.path.join(output_path, 'data.zip'), 'r') as zipf:
            zipf.extractall(path=output_path)

    return output_path
