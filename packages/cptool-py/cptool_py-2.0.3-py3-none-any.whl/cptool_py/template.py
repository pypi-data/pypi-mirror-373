import os
import platformdirs
from argparse import Namespace
from cptool_py.formatting import format_extension

def get_template_path(args: Namespace) -> str:
    extension: str = args.extension
    template_folder: str = args.template_folder
    return os.path.join(template_folder, 'template.' + format_extension(extension))

def get_default_template_folder() -> str:
    return platformdirs.user_data_dir(appname='cp-tool', appauthor='smntic')

