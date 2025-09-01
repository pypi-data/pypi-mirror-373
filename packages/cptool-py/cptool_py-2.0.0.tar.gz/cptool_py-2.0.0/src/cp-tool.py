#!/usr/bin/env python

from args import parse_args
from commands import handle_args

def main() -> None:
    args = parse_args()
    handle_args(args)

if __name__ == '__main__':
    main()

