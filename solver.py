#!/usr/bin/env python3

import argparse
import sys

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"

verbose = False
silent = False


def log(msg):
    if not silent:
        print(f"[LOG] {msg}", file=sys.stdout)


def warn(msg):
    if not silent and verbose:
        print(f"{YELLOW}[WARN] {msg}{RESET}", file=sys.stderr)


def error(msg):
    if not silent:
        print(f"{RED}[ERROR] {msg}{RESET}", file=sys.stderr)


def initArgs():
    parser = argparse.ArgumentParser(
        prog="word2",
        description="An insightful wordle solver",
        # epilog="",
    )
    parser.add_argument(
        "-v", "--verbose", help="Displays more messages and errors", action="store_true"
    )
    parser.add_argument(
        "-s", "--silent", help="Displays no messages", action="store_true"
    )
    args = parser.parse_args()
    if args.verbose:
        verbosity = 2
        log("Verbosity turned on")
    if args.silent:
        verbosity = 0
        log("Verbosity turned on")


def main():
    initArgs()
    log("Welcome to word2")


if __name__ == "__main__":
    main()
