# goit-algo-hw-05

Homework 5: compare Boyer-Moore, Knuth-Morris-Pratt, and Rabin-Karp substring search on two articles.

## Setup

Python 3.10 or newer. No third-party packages are required.

## Tasks

| Task | File | Description |
| ---- | ---- | ----------- |
| 1 | `task_01/task_01.py` | Implement three search algorithms and compare their execution times using `timeit` |

## Run

Run these commands from the repository root.

```bash
python3 task_01/task_01.py
python3 task_01/task_01.py --output task_01/benchmark_results.csv
python3 task_01/task_01.py --repeat 5 --number 100
```

Each algorithm returns the zero-based index of the first match, `-1` if no match exists, and `0` for an empty pattern. Search is case-sensitive. Boyer-Moore uses the bad-character rule. KMP builds a prefix table. Rabin-Karp uses a rolling hash and checks the actual substring when hashes match.

The input files are included in `task_01/data`. They come from the homework links: [article 1](https://drive.google.com/file/d/1EdQUqE_qLDCL_54v8aQ5zlcMf2L9dF_B/view) and [article 2](https://drive.google.com/file/d/1o5uZ8NBMtZmThGIeilCRWgspIOfOnbzQ/view). The downloads were converted from Windows-1251 to UTF-8 with LF line endings. The article content was preserved.

## Search results

Article 1 contains 12,658 characters. Article 2 contains 18,400 characters. Each text is searched for a present phrase and the invented phrase `квантовий борщ на Марсі`, which has 23 characters and is absent from both texts.

| Article | Present pattern | Pattern length | First position |
| ------- | --------------- | -------------: | -------------: |
| 1 | `Експоненціальний пошук` | 22 | 7,270 |
| 2 | `колаборативну фільтрацію` | 24 | 9,796 |

Measured with CPython 3.11.6 on macOS 15.4.1, ARM64. Each measurement uses five repeats of 100 searches. The shortest repeat is divided by 100 to get the time per search. Pattern preprocessing is included in each search. File reading, result validation against `str.find`, and CSV writing are excluded from timing.

Times below are in milliseconds per search. [Full results](task_01/benchmark_results.csv) are saved in seconds.

| Article | Pattern | Boyer-Moore | KMP | Rabin-Karp |
| ------- | ------- | ----------: | --: | ---------: |
| 1 | Present | 0.157892 | 0.569527 | 1.466623 |
| 1 | Absent | 0.231711 | 1.002927 | 2.532287 |
| 2 | Present | 0.193469 | 0.831919 | 2.009087 |
| 2 | Absent | 0.340767 | 1.509093 | 3.722096 |

For each article, the two per-search times are added with equal weight. The overall result adds all four cases.

| Scope | Boyer-Moore total | KMP total | Rabin-Karp total | Fastest |
| ----- | ----------------: | --------: | ---------------: | ------- |
| Article 1 | 0.389603 | 1.572454 | 3.998910 | Boyer-Moore |
| Article 2 | 0.534237 | 2.341012 | 5.731183 | Boyer-Moore |
| Overall | 0.923840 | 3.913466 | 9.730093 | Boyer-Moore |

## Conclusions

- Boyer-Moore was the fastest for article 1 and article 2, both for present and absent patterns. Its shifts let it skip text positions on these inputs.
- KMP was second in all four cases. It scans the text sequentially and has O(n + m) worst-case time, where n is the text length and m is the pattern length.
- Rabin-Karp was the slowest here. Updating the rolling hash at each text position adds arithmetic work in Python. Hash collisions require substring comparisons, so the expected O(n + m) time can become O(nm) in the worst case.
- Overall, Boyer-Moore was about 4.24 times faster than KMP and 10.53 times faster than Rabin-Karp. Absent patterns took longer because the search reached the end of each text.
- These results apply to the selected patterns and implementations. Pattern length, match position, repeated characters, and hardware can change the ranking. The Boyer-Moore version here uses only the bad-character rule and can also take O(nm) time in the worst case.
