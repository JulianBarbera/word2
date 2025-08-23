import json
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from solver import guesses_to_solve

GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"

VERBOSE = True


def parse(path="data.jsonl"):
    words = []
    print(f"Parsing wordlist {path}...")
    with open(path) as f:
        for i, line in enumerate(f, start=1):
            obj = json.loads(line)
            word = obj.get("word")
            words.append(word.upper())
    return words


def process_word_pair(base_word, word_list, verbose=False):
    results = []
    for compare_word in word_list:
        try:
            score = guesses_to_solve(base_word, compare_word)
            results.append(score)
            if verbose:
                print(f"{base_word} x {compare_word}: {YELLOW}{score}{RESET}")
        except Exception:
            continue
    if results:
        average_score = sum(results) / len(results)
        return base_word, average_score
    return None


def main():
    words = parse()
    results_dict = {}
    num_workers = multiprocessing.cpu_count()
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [
            executor.submit(process_word_pair, base_word, words, VERBOSE)
            for base_word in words
        ]
        for future in as_completed(futures):
            result = future.result()
            if result:
                word, average = result
                results_dict[word] = average
                with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                    json.dump({word: average}, f)
                    f.write("\n")
                print(f"{GREEN}{word} average: {average}{RESET}")
    if results_dict:
        best_word = min(results_dict, key=results_dict.get)
        print(f"Best word: {best_word} with score {results_dict[best_word]}")


if __name__ == "__main__":
    main()
