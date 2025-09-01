import os
from argparse import Namespace
from cptool_py.template import get_template_path
from cptool_py.fileio import copy_template, make_folder
from cptool_py.formatting import format_name, format_extension
from cptool_py.error import warning_message, fatal_error_message

def handle_args(args: Namespace) -> None:
    extension: str = format_extension(args.extension)
    template_path = get_template_path(args)

    if 'name_list' in args:
        args.name_list = [format_name(name) for name in args.name_list]
    if 'name' in args:
        args.name = format_name(args.name)

    if args.command == 'template':
        template_command(args.name_list, args.force, extension, template_path)
    elif args.command == 'problem':
        problem_command(args.name, args.force, extension, template_path)
    elif args.command == 'contest':
        contest_command(args.name, args.name_list, args.force, extension, template_path)

def template_command(name_list: list[str], force: bool, extension: str, template_path: str) -> None:
    failed = 0
    for name in name_list:
        if not copy_template(template_path, name + '.' + extension, force):
            failed += 1
    if failed > 0:
        warning_message(f'Failed to create {failed} file{"s" if failed > 1 else ""}.')

def problem_command(problem_name: str, force: bool, extension: str, template_path: str) -> None:
    contest_command(problem_name, [problem_name], force, extension, template_path)

def contest_command(contest_name: str, name_list: list[str], force: bool, extension: str, template_path: str) -> None:
    if not make_folder(contest_name, force):
        fatal_error_message('Failed to create contest folder. No files were created.')
    template_command([os.path.join(contest_name, name) for name in name_list], force, extension, template_path)

