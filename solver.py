#!/usr/bin/env python3

import argparse
import sys
import json

# ANSI colors
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"

verbose = False
silent = False
data = []
words = set()


def log(msg):
    if not silent:
        print(f"[LOG] {msg}", file=sys.stdout)


def warn(msg):
    if not silent and verbose:
        print(f"{YELLOW}[WARN]{RESET} {msg}", file=sys.stderr)


def error(msg):
    if not silent:
        print(f"{RED}[ERROR]{RESET} {msg}", file=sys.stderr)
    sys.exit(1)


def init_args():
    parser = argparse.ArgumentParser(
        prog="word2",
        description="An insightful wordle solver",
    )
    parser.add_argument("first")
    parser.add_argument("secret")
    parser.add_argument(
        "-v", "--verbose", help="Displays more messages and errors", action="store_true"
    )
    parser.add_argument(
        "-s", "--silent", help="Displays no messages", action="store_true"
    )
    parser.add_argument(
        "-f",
        "--file",
        default="words.jsonl",
        help="Word list file (default: words.jsonl)",
    )
    return parser.parse_args()


def parse(path="words.jsonl"):
    """Parse the dataset into tuples (word, score, frequency)."""
    global data, words
    if data:
        return data, words

    try:
        log(f"Parsing wordlist {path}...")
        with open(path) as f:
            for i, line in enumerate(f, start=1):
                try:
                    obj = json.loads(line)
                    word = obj.get("word")
                    score = obj.get("score")
                    freq = obj.get("frequency")
                    if not (word and score is not None and freq is not None):
                        warn(f"Skipping line {i}: missing keys")
                        continue
                    data.append((word, score, freq))
                except Exception as e:
                    warn(f"Skipping line {i}: {e}")
        words = {word for word, _, _ in data}
        log(f"Parsed {len(data)} valid words")
    except FileNotFoundError:
        error(f"{path} not found")

    return data, words


def guesses_to_solve(first, secret, path="words.jsonl"):
    """Main solver routine."""
    first = first.upper()
    secret = secret.upper()

    parse(path)

    if first not in words:
        error("Please use an opener from the dataset")
    if secret not in words:
        error("Please use a secret from the dataset")

    log(f"First guess: {first}, Secret word: {secret}")

    return True


def main():
    global verbose, silent
    args = init_args()

    if len(args.first) != 5:
        error("Opening word invalid")
    if len(args.secret) != 5:
        error("Secret word invalid")

    verbose = args.verbose
    silent = args.silent

    if verbose:
        log("Verbosity turned on")
    if silent:
        log("If you can read this, something has gone terribly wrong")

    log("Welcome to word2")
    guesses_to_solve(args.first, args.secret, args.file)


if __name__ == "__main__":
    main()
