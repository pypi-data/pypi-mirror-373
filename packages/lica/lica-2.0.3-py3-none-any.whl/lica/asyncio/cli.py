# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) 2021
#
# See the LICENSE file for details
# see the AUTHORS file for authors
# ----------------------------------------------------------------------

# --------------------
# System wide imports
#  -------------------

import sys
import logging
from logging import StreamHandler
from logging.handlers import WatchedFileHandler, QueueHandler, QueueListener
import traceback
import queue
import asyncio
from argparse import ArgumentParser, Namespace
from typing import Callable

# -------------
# Local imports
# -------------

# -----------------------
# Module global variables
# -----------------------

log = logging.getLogger()
listener = None

# ------------------------
# Module utility functions
# ------------------------


def configure_logging(args: Namespace) -> QueueListener:
    """Configure the root logger"""
    if args.verbose:
        level = logging.DEBUG
    elif args.quiet:
        level = logging.WARNING
    else:
        level = logging.INFO
    # set the root logger level
    log.setLevel(level)
    # Log formatter
    # fmt = logging.Formatter('%(asctime)s - %(name)s [%(levelname)s] %(message)s')
    fmt = logging.Formatter("%(asctime)s [%(levelname)-8s] [%(name)s] %(message)s")
    # create console handler and set level to debug
    q = queue.Queue()
    log.addHandler(QueueHandler(q))
    handlers = list()
    if args.console:
        ch = StreamHandler()
        ch.setFormatter(fmt)
        ch.setLevel(logging.DEBUG)
        handlers.append(ch)
    # Create a file handler suitable for logrotate usage
    if args.log_file:
        fh = WatchedFileHandler(args.log_file)
        # fh = TimedRotatingFileHandler(args.log_file, when='midnight', interval=1, backupCount=365)
        fh.setFormatter(fmt)
        fh.setLevel(logging.DEBUG)
        handlers.append(fh)
    listener = QueueListener(q, *handlers)
    return listener


def arg_parser(name: str, version: str, description: str) -> ArgumentParser:
    # create the top-level parser
    parser = ArgumentParser(prog=name, description=description)
    # Generic args common to every command
    parser.add_argument("--version", action="version", version="{0} {1}".format(name, version))
    parser.add_argument("--console", action="store_true", help="Log to console.")
    parser.add_argument("--log-file", type=str, metavar="<FILE>", default=None, help="Log to file.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--verbose", action="store_true", help="Verbose output.")
    group.add_argument("--quiet", action="store_true", help="Quiet output.")
    parser.add_argument("--trace", action="store_true", help="Show exception stack trace.")
    return parser


async def _wrapped_main(main_func: Callable[[Namespace], None], args: Namespace, name: str, version: str) -> None:
    """Internal coroutine that starts logging thread and the main coroutine"""
    global listener
    listener = configure_logging(args)
    listener.start()
    log.info("============== %s %s ==============", name, version)
    await main_func(args)


def execute(
    main_func: Callable[[Namespace], None],
    add_args_func: Callable[[ArgumentParser], None],
    name: str,
    version: str,
    description: str,
) -> None:
    """
    Utility entry point
    """
    try:
        return_code = 1
        parser = arg_parser(name, version, description)
        add_args_func(parser)  # Adds more arguments
        args = parser.parse_args(sys.argv[1:])
        asyncio.run(_wrapped_main(main_func, args, name, version))
        return_code = 0
    except KeyboardInterrupt:
        log.critical("[%s] Interrupted by user ", name)
    except Exception as e:
        log.critical("[%s] Fatal error => %s", name, str(e))
        if args.trace:
            traceback.print_exc()
    finally:
        if listener:
            listener.stop()
        sys.exit(return_code)
