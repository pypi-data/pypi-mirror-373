import os
import shutil
from cptool_py.UI import confirm
from cptool_py.error import fatal_error_message

def copy_template(template_path: str, destination_path: str, force: bool) -> bool:
    # Ensure the template file exists:
    if not os.path.isfile(template_path):
        fatal_error_message(f'Template file at {template_path} does not exist!')

    # Ensure the destination folder exists and has a valid file name:
    destination_folder, destination_file = os.path.split(destination_path)
    if destination_folder != '' and not os.path.isdir(destination_folder):
        fatal_error_message(f'Can\'t find folder: {destination_folder}')
    if not destination_file:
        fatal_error_message(f'File name is empty: {destination_path}')

    # Make sure we can overwrite existing file, if it exists:
    if os.path.isfile(destination_path) and not force:
        if not confirm(f'Overwrite existing file: {destination_path}?'):
            return False
    
    try:
        # Copy the template file to the destination file:
        _ = shutil.copyfile(template_path, destination_path) # Ignore file permissions
    except PermissionError:
        fatal_error_message(f'Insufficient permissions to copy to {destination_path}')

    return True

def make_folder(folder_path: str, force: bool) -> bool:
    try:
        os.makedirs(folder_path, exist_ok=force) # What about permission errors?
    except OSError:
        fatal_error_message(f'Folder {folder_path} already exists.')

    return True

