import os
import sys
import argparse
import logging

from psync.cleaner import clean
from psync.syncer import new_session

logger = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"),
                    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s")


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description='Import, clean and sync images with PiWiGo.')
    parser.add_argument('--clean',
                        nargs=1,
                        metavar='folder',
                        action='store',
                        help='clean directory and filenames')

    parser.add_argument('--new-session',
                        nargs=1,
                        metavar='secrets',
                        action='store',
                        help='create a new session with the specified secrets.ini')

    parser.add_argument('--pretend',
                        action='store_true',
                        default=False,
                        help='dry run only')

    args = parser.parse_args()

    if args.clean is not None and len(args.clean) > 0:
        clean(args.clean[0], args.pretend)

    if args.new_session is not None and len(args.new_session) > 0:
        new_session(args.new_session[0], args.pretend)


if __name__ == "__main__":
    main()
