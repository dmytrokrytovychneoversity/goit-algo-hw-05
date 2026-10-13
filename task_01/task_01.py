"""Compare three substring search algorithms on two articles."""

import argparse
import csv
import platform
import timeit
from pathlib import Path


def boyer_moore_search(text: str, pattern: str) -> int:
    """Return the first match using the Boyer-Moore bad-character rule."""
    if not pattern:
        return 0
    last_occurrence = {char: index for index, char in enumerate(pattern)}
    offset = 0
    while offset <= len(text) - len(pattern):
        index = len(pattern) - 1
        while index >= 0 and pattern[index] == text[offset + index]:
            index -= 1
        if index < 0:
            return offset
        offset += max(1, index - last_occurrence.get(text[offset + index], -1))
    return -1


def build_prefix_table(pattern: str) -> list[int]:
    """Build lengths of matching proper prefixes and suffixes."""
    table = [0] * len(pattern)
    prefix_length = 0
    for index in range(1, len(pattern)):
        while prefix_length > 0 and pattern[index] != pattern[prefix_length]:
            prefix_length = table[prefix_length - 1]
        if pattern[index] == pattern[prefix_length]:
            prefix_length += 1
        table[index] = prefix_length
    return table


def kmp_search(text: str, pattern: str) -> int:
    """Return the first match using the Knuth-Morris-Pratt algorithm."""
    if not pattern:
        return 0
    if len(pattern) > len(text):
        return -1
    table = build_prefix_table(pattern)
    matched = 0
    for index, char in enumerate(text):
        while matched > 0 and char != pattern[matched]:
            matched = table[matched - 1]
        if char == pattern[matched]:
            matched += 1
        if matched == len(pattern):
            return index - len(pattern) + 1
    return -1


def rabin_karp_search(text: str, pattern: str) -> int:
    """Return the first match using a rolling hash and collision checks."""
    pattern_length = len(pattern)
    if pattern_length == 0:
        return 0
    if pattern_length > len(text):
        return -1
    base = 256
    modulus = 1_000_000_007
    highest_power = pow(base, pattern_length - 1, modulus)
    pattern_hash = 0
    window_hash = 0
    for index in range(pattern_length):
        pattern_hash = (pattern_hash * base + ord(pattern[index])) % modulus
        window_hash = (window_hash * base + ord(text[index])) % modulus
    for start in range(len(text) - pattern_length + 1):
        if window_hash == pattern_hash:
            if text[start : start + pattern_length] == pattern:
                return start
        if start < len(text) - pattern_length:
            window_hash = (
                (window_hash - ord(text[start]) * highest_power) * base
                + ord(text[start + pattern_length])
            ) % modulus
    return -1


def benchmark(repeat: int, number: int) -> list[dict]:
    """Check search results and measure the best repeated time per call."""
    algorithms = {
        "boyer_moore": boyer_moore_search,
        "kmp": kmp_search,
        "rabin_karp": rabin_karp_search,
    }
    articles = {
        "article_1": "Експоненціальний пошук",
        "article_2": "колаборативну фільтрацію",
    }
    absent_pattern = "квантовий борщ на Марсі"
    data_directory = Path(__file__).resolve().parent / "data"
    rows = []
    print(f"Python {platform.python_version()} ({platform.python_implementation()})")
    print(f"Platform: {platform.platform()}")
    print(f"Repeats: {repeat}. Searches per repeat: {number}.")
    print(
        f"{'Article':<12} {'Case':<8} {'Position':>8} "
        f"{'Boyer-Moore (ms)':>17} {'KMP (ms)':>12} {'Rabin-Karp (ms)':>17}"
    )
    for article, present_pattern in articles.items():
        text = (data_directory / f"{article}.txt").read_text(encoding="utf-8")
        patterns = {"present": present_pattern, "absent": absent_pattern}
        for case, pattern in patterns.items():
            expected = text.find(pattern)
            if (case == "present" and expected < 0) or (
                case == "absent" and expected != -1
            ):
                raise ValueError(f"The {case} pattern is unsuitable for {article}")
            row = {
                "article": article,
                "characters": len(text),
                "case": case,
                "pattern": pattern,
                "position": expected,
            }
            for label, algorithm in algorithms.items():
                if algorithm(text, pattern) != expected:
                    raise AssertionError(f"{label} failed for {article}, {case}")
                timer = timeit.Timer(lambda: algorithm(text, pattern))
                row[label] = min(timer.repeat(repeat=repeat, number=number)) / number
            rows.append(row)
            print(
                f"{article:<12} {case:<8} {expected:>8} "
                f"{row['boyer_moore'] * 1000:>17.6f} "
                f"{row['kmp'] * 1000:>12.6f} {row['rabin_karp'] * 1000:>17.6f}"
            )
    for group in [*articles, "overall"]:
        selected = [
            row for row in rows if group == "overall" or row["article"] == group
        ]
        totals = {label: sum(row[label] for row in selected) for label in algorithms}
        winner = min(totals, key=totals.get)
        print(f"Fastest for {group}: {winner} (sum: {totals[winner] * 1000:.6f} ms)")
    return rows


def main() -> None:
    """Run the comparison and optionally save per-call seconds as CSV."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--number", type=int, default=100)
    parser.add_argument("--output", type=Path, help="CSV output path")
    args = parser.parse_args()
    if args.repeat < 1 or args.number < 1:
        parser.error("repeat and number must be positive")
    try:
        rows = benchmark(args.repeat, args.number)
        if args.output:
            with args.output.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(
                    file, fieldnames=list(rows[0]), lineterminator="\n"
                )
                writer.writeheader()
                writer.writerows(rows)
            print(f"Saved {args.output}")
    except (OSError, ValueError) as error:
        parser.exit(1, f"Cannot complete benchmark: {error}\n")


if __name__ == "__main__":
    main()
