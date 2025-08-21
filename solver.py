#!/usr/bin/env python3

import argparse
import sys
import json
import math

# ANSI colors
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"

verbose = False
silent = False
data = []
words = set()
guessct = set()
frequencies = set()


def log(msg):
    if verbose:
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
        default="data.jsonl",
        help="Word list file (default: words.jsonl)",
    )
    return parser.parse_args()


def parse(path="data.jsonl"):
    global data, words, guessct, frequencies
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
        guessct = {gct for _, gct, _ in data}
        frequencies = {frq for _, _, frq in data}
        log(f"Parsed {len(data)} valid words")
    except FileNotFoundError:
        error(f"{path} not found")

    return data, words


def printGuess(guess, secret):
    if silent:
        return
    n = 0
    for character in guess:
        if character == secret[n]:
            print(f"{GREEN}{character}{RESET}", end="")
        elif character in secret:
            print(f"{YELLOW}{character}{RESET}", end="")
        else:
            print(character, end="")
        n += 1
    print()


def pare(guess, secret, data, negative, positive, confirmed):
    log(f"Paring {guess}")
    data = [w for w in data if not any(char in w[0] for char in negative)]
    data = [w for w in data if all(char in w[0] for char in positive)]
    data = [
        w
        for w in data
        if all(c == " " or w[0][i] == c for i, c in enumerate(confirmed))
    ]

    log(len(data))
    return data


def agent(guess, secret, negative=[], positive=[], confirmed=[]):
    negative = [c for c in guess if c not in secret]
    positive = [c for c in guess if c in secret]
    confirmed = "".join(c if c == secret[i] else " " for i, c in enumerate(guess))
    return negative, positive, confirmed


def sort(data):
    return sorted(data, key=rank, reverse=True)


def rank(e):
    g = e[1]
    f = e[2]
    gmin = min(guessct)
    gmax = max(guessct)
    fmin = min(frequencies)
    fmax = max(frequencies)
    return 1000 * (
        1 - ((g - gmin) / (gmax - gmin)) + math.sqrt((f - fmin) / (fmax - fmin))
    )


def check(guess, secret):
    printGuess(guess, secret)
    return guess == secret


def guesses_to_solve(first, secret, path="words.jsonl"):
    first = first.upper()
    secret = secret.upper()

    parse(path)

    if first not in words:
        error("Please use an opener from the dataset")
    if secret not in words:
        error("Please use a secret from the dataset")

    log(f"First guess: {first}, Secret word: {secret}")
    global data

    i = 1
    data = sort(data)
    negative, positive, confirmed = agent(first, secret)
    data = sort(pare(first, secret, data, negative, positive, confirmed))
    if check(first, secret):
        return i

    while True:
        i += 1
        guess = data[0][0]
        if check(guess, secret):
            break
        negative, positive, confirmed = agent(
            guess, secret, negative, positive, confirmed
        )
        data = sort(pare(guess, secret, data, negative, positive, confirmed))

    return i


def user(negative, positive):
    neg = input("It's not...\n" + "".join(negative)).upper()
    pos = input("It has...\n" + "".join(positive)).upper()
    return neg, pos


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
    log(guesses_to_solve(args.first, args.secret, args.file))


if __name__ == "__main__":
    main()
