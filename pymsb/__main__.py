import sys


def main(args=None):
    """Entry point for PyMSB GUI"""

    if args is None:
        args = sys.argv[1:]

    print("This is the PyMSB entry point.  It should do something interesting.")

if __name__ == "__main__":
    main()