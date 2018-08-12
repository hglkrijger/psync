import os
import sys
import argparse
import logging

from psync.cleaner import clean
from psync.syncer import Sync

logger = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"),
                    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s")


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description='Import, clean and sync images with PiWiGo.')
    parser.add_argument('--sync',
                        action='store_true',
                        help='run sync')

    parser.add_argument('--clean',
                        nargs=1,
                        metavar='folder',
                        action='store',
                        help='clean directory and filenames')

    parser.add_argument('--new-session',
                        nargs=1,
                        metavar='account',
                        action='store',
                        help='create and save a new session')

    parser.add_argument('--refresh-session',
                        nargs=1,
                        metavar='account',
                        action='store',
                        help='load an existing session and refresh the token')

    parser.add_argument('--pretend',
                        action='store_true',
                        default=False,
                        help='dry run only')

    args = parser.parse_args()

    sync = Sync(args.pretend)

    if args.new_session:
        sync.new_session(args.new_session[0])

    if args.refresh_session:
        sync.refresh_session(args.refresh_session[0])

    if args.sync:
        sync.run()

    if args.clean is not None:
        clean(args.clean[0], args.pretend)


if __name__ == "__main__":
    main()
