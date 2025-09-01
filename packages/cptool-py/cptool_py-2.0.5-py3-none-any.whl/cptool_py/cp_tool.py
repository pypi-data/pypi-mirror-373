#!/usr/bin/env python

from cptool_py.args import parse_args
from cptool_py.commands import handle_args

def main() -> None:
    args = parse_args()
    handle_args(args)

if __name__ == '__main__':
    main()

