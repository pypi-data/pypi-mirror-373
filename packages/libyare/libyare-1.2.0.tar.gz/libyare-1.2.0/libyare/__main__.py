#!/usr/bin/python3

from .__init__ import __doc__ as description, __version__ as version
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from sys import argv, exit

class arg: pass

def libyare(argv):
    "library for YARE (Yet Another Regular Expression)"

    # get arguments
    if len(argv) == 1:
        argv.append('-h')
    parser = ArgumentParser(prog="libyare", formatter_class=RawDescriptionHelpFormatter, description=description)
    parser.add_argument("-V", "--version", action="version", version=f"libyare {version}")
    parser.parse_args(argv[1:], arg)
        
def main():
    try:
        libyare(argv)
    except KeyboardInterrupt:
        print()

if __name__ == "__main__":
    main()
