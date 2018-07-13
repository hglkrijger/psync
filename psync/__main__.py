import os
import sys
import argparse
import logging

from psync.cleaner import clean
from psync.syncer import new_session, load_session

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
                        metavar='secrets.ini',
                        action='store',
                        help='create a new session with the specified secrets.ini')

    parser.add_argument('--load-session',
                        nargs=1,
                        metavar='secrets.ini|app_id',
                        action='store',
                        help='load an existing session from the default session file')

    parser.add_argument('--pretend',
                        action='store_true',
                        default=False,
                        help='dry run only')

    args = parser.parse_args()

    if args.clean is not None:
        clean(args.clean[0], args.pretend)

    if args.new_session is not None:
        new_session(args.new_session[0], args.pretend)

    if args.load_session is not None:
        load_session(args.load_session[0])


if __name__ == "__main__":
    main()
