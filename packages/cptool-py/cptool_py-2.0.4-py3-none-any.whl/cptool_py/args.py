import argparse
from cptool_py.formatting import generate_alpha_indices, generate_numeric_indices
from cptool_py.template import get_default_template_folder

def parse_args() -> argparse.Namespace:
    # Main parser
    parser = argparse.ArgumentParser(
        prog='cp-tool',
        description='CLI for creating competitive programming problem files',
    )
    parser.add_argument('-f', '--force', help='whether to force any fileio operations (e.g. overwrite existing files)', action='store_true')
    parser.add_argument('-ex', '--extension', help='file extension for the template files', type=str, nargs='?', default='.cpp')
    parser.add_argument('-tf', '--template-folder', help=f'path to a folder containing template files. defaults to {get_default_template_folder()}', type=str, nargs='?', default=get_default_template_folder())

    # Command subparsers
    commands_subparsers = parser.add_subparsers(title='available commands', required=True)

    # Template parser
    template_parser = commands_subparsers.add_parser('template')
    template_parser.add_argument('name_list', help='problem names', type=str, nargs='+')
    template_parser.set_defaults(command='template')

    # Problem parser
    problem_parser = commands_subparsers.add_parser('problem')
    problem_parser.add_argument('name', help='problem name', type=str)
    problem_parser.set_defaults(command='problem')

    # Contest parser
    contest_parser = commands_subparsers.add_parser('contest')
    contest_parser.add_argument('name', help='name of the contest', type=str)
    contest_parser.set_defaults(command='contest')

    # Contest -> Modes subparsers
    modes_subparsers = contest_parser.add_subparsers(title='name list modes', required=True)
    built_in_parser_parent = argparse.ArgumentParser(add_help=False)
    built_in_parser_parent.add_argument('count', help='number of problems in the contest', type=int)

    # Contest -> Modes -> Alpha parser
    alpha_parser = modes_subparsers.add_parser(
        'alpha',
        help='name the problems by alphabetic indexing. i.e., A, B, C, ...',
        parents=[built_in_parser_parent]
    )
    alpha_parser.set_defaults(name_list_mode='alpha')

    # Contest -> Modes -> Numeric parser
    numeric_parser = modes_subparsers.add_parser(
        'numeric',
        help='name the problems by numeric indexing. i.e., 1, 2, 3, ...',
        parents=[built_in_parser_parent]
    )
    numeric_parser.set_defaults(name_list_mode='numeric')

    # Contest -> Modes -> Custom names parser
    custom_parser = modes_subparsers.add_parser(
        'custom',
        help='custom problem names. e.g. A, B, C, D1, D2'
    )
    custom_parser.add_argument('name_list', help='problem names', type=str, nargs='+')

    args = parser.parse_args()

    # Any post-parse processing:
    if 'name_list_mode' in args:
        parse_name_list_mode(args)

    return args

def parse_name_list_mode(args: argparse.Namespace) -> None:
    if args.name_list_mode == 'alpha':
        args.name_list = generate_alpha_indices(args.count)
    elif args.name_list_mode == 'numeric':
        args.name_list = generate_numeric_indices(args.count)

