#!/usr/bin/env python3

import argparse
import sys
import json
import math
import readline

# ANSI colors
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"

verbose = False
silent = False
practice = False
file = "data.jsonl"
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
    parser.add_argument("--first")
    parser.add_argument("--secret")
    parser.add_argument(
        "-v", "--verbose", help="Displays more messages and errors", action="store_true"
    )
    parser.add_argument(
        "-s", "--silent", help="Displays no messages", action="store_true"
    )
    parser.add_argument(
        "-p",
        "--practice",
        help="Allows previously used wordle words",
        action="store_true",
    )
    parser.add_argument(
        "-f",
        "--file",
        default="data.jsonl",
        help="Word list file",
    )
    return parser.parse_args()


def parse(path=file):
    global data, words, guessct, frequencies
    if data:
        return data, words

    try:
        log(f"Parsing wordlist {path}...")
        with open(path) as f:
            for i, line in enumerate(f, start=1):
                try:
                    obj = json.loads(line)
                    word = obj.get("word").upper()
                    score = obj.get("score")
                    freq = obj.get("frequency")
                    if not (word and score is not None and freq is not None):
                        warn(f"Skipping line {i}: missing keys")
                        continue
                    data.append((word.upper(), score, freq))
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


def pare(data, negative, positive, confirmed, anti):
    negative_set = set("".join(negative))

    filtered = []
    for word, score, freq in data:
        log(word)
        if not set(positive).issubset(set(word)):
            continue

        if set(word).intersection(negative_set):
            continue
        bad = 0
        for i, c in enumerate(word):
            if c is not confirmed[i] and confirmed[i].isalpha():
                bad = 1
            log(c)
            log(anti[i])
            if c in anti[i]:
                bad = 1
        if bad:
            continue
        filtered.append((word, score, freq))

    return filtered


def agent(guess, secret, negative, positive, confirmed, anti):
    new_negative = set()
    new_positive = set()

    for i, c in enumerate(guess):
        if c == secret[i]:
            confirmed[i] = c
        elif c in secret:
            new_positive.add(c)
            anti[i] += c
        else:
            new_negative.add(c)

    negative |= new_negative
    positive |= new_positive

    return negative, positive, confirmed, anti


def sort(data):
    return sorted(data, key=rank, reverse=True)


def rank(e):
    g = e[1]
    f = e[2]
    gmin = min(guessct)
    gmax = max(guessct)
    fmin = min(frequencies)
    fmax = max(frequencies)

    g_range = gmax - gmin if gmax != gmin else 1
    f_range = fmax - fmin if fmax != fmin else 1

    return 1000 * (1 - ((g - gmin) / g_range) * 0.07 ** ((f - fmin) / f_range))


def check(guess, secret):
    printGuess(guess, secret)
    return guess == secret


def guesses_to_solve(first, secret):
    first = first.upper()
    secret = secret.upper()
    global data
    data = []

    parse(file)

    if first not in words:
        error("Please use an opener from the dataset")
    if secret not in words:
        error("Please use a secret from the dataset")

    log(f"First guess: {first}, Secret word: {secret}")

    i = 1
    data = sort(data)
    negative, positive, confirmed, anti = set(), set(), [" "] * 5, [""] * 5
    negative, positive, confirmed, anti = agent(
        list(first), secret, negative, positive, confirmed, anti
    )
    data = pare(data, negative, positive, confirmed, anti)
    if check(first, secret):
        return i

    while True:
        i += 1
        guess = data[0][0]
        if check(guess, secret):
            break
        negative, positive, confirmed, anti = agent(
            list(guess), secret, negative, positive, confirmed, anti
        )
        data = pare(data, negative, positive, confirmed, anti)

    return i


def user(negative=[], positive=[], confirmed=[], anti=[]):
    negative.extend(input("It's not...\n" + "".join(negative)).upper())
    positive.extend(input("It has...\n" + "".join(positive)).upper())
    readline.set_startup_hook(lambda: readline.insert_text("|".join(anti)))
    try:
        newAnti = input("Anti\n").upper().split("|")
    finally:
        readline.set_startup_hook()
    # if newAnti.strip() != "":
    anti = list(newAnti)
    readline.set_startup_hook(lambda: readline.insert_text("".join(confirmed)))
    log(f"Negative: {negative}")
    log(f"Positive: {positive}")
    log(f"Confirmed: {confirmed}")
    try:
        newConfirmed = input("Where?\n12345\n").upper()
    finally:
        readline.set_startup_hook()
    if newConfirmed.strip() != "":
        confirmed = list(newConfirmed)
    return negative, positive, confirmed, anti


def solve(path=file):
    parse(path)

    global data

    i = 1
    data = sort(data)
    negative, positive, confirmed, anti = set(), set(), [" "] * 5, [""] * 5
    negative, positive, confirmed, anti = user(
        list(negative), list(positive), confirmed, anti
    )
    data = pare(data, negative, positive, confirmed, anti)

    while True:
        i += 1
        guess = data[0][0]
        data.pop(0)
        print(guess)
        negative, positive, confirmed, anti = user(
            list(negative), list(positive), confirmed, anti
        )
        data = pare(data, negative, positive, confirmed, anti)

    return i


def main():
    global verbose, silent, file
    args = init_args()

    if args.first or args.secret:
        if args.first and len(args.first) != 5:
            error("Opening word invalid")
        if args.secret and len(args.secret) != 5:
            error("Secret word invalid")

    verbose = args.verbose
    silent = args.silent
    if args.practice:
        file = "full_data.jsonl"
    else:
        file = "data.jsonl"

    if verbose:
        log("Verbosity turned on")
    if silent:
        log("If you can read this, something has gone terribly wrong")

    log("Welcome to word2")
    if args.first and args.secret:
        log(guesses_to_solve(args.first, args.secret))
    else:
        solve(args.file)


if __name__ == "__main__":
    main()
