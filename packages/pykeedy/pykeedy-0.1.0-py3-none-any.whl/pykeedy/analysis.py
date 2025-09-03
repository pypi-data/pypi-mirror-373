import numpy as np
from collections import Counter

from collections import defaultdict
import re


def frequency_rank(
    text: str | list[str], n: int = 1, normalize: bool = True
) -> dict[str, float]:
    # Accept either a string and return character frequency rank,
    # Or a list of words and return word frequency rank.
    # Return sorted descending
    char_level = isinstance(text, str)

    seq = np.array(list(text)) if char_level else np.array(text)

    if len(seq) < n:
        return {}

    ngrams = []
    exclude = np.array(list(" .\n"))  # exclude ' ', '.' and '\n' chars from all grams
    for i in range(len(seq) - n + 1):
        gram = seq[i : i + n]
        if np.any(np.isin(gram, exclude)):
            continue
        ngrams.append(gram)

    unique, counts = np.unique(ngrams, axis=0, return_counts=True)

    sorted_indices = np.argsort(counts)[::-1]
    joiner = "" if char_level else " "

    result: dict[str, int | float] = {}
    for idx in sorted_indices:
        key = joiner.join(unique[idx])  # works for all n, including n==1
        if " " in key:
            key = f"'{key}'"
        count = int(counts[idx])
        result[key] = count

    if normalize:
        total = sum(result.values())
        for key in result:
            result[key] = result[key] / total

    return result


def cooccurence_matrix(
    text: str | list[str], n: int = 2, normalize: bool = True
) -> tuple[list[str], list[list[float]]]:
    char_level = isinstance(text, str)
    seq = np.array(list(text)) if char_level else np.array(text)

    if len(seq) < n:
        return [], []

    # Generate n-grams, excluding any containing spaces
    # TODO add option that includes spaces to calculate most common first and last letters
    ngrams = []
    exclude = [" ", "\n", "."]
    for i in range(len(seq) - n + 1):
        ngram = tuple(seq[i : i + n])
        if any(elem in exclude for elem in ngram):
            continue
        ngrams.append(ngram)

    # Get unique n-grams and their counts
    unique_ngrams, counts = np.unique(ngrams, axis=0, return_counts=True)

    # Counting the gram occurences in all ngram occurences
    # Note this duplicates anything not at the start or end of a sequence
    # We want that in this case
    element_counts = {}
    for ngram_array, count in zip(unique_ngrams, counts):
        for element in ngram_array:
            element_counts[element] = element_counts.get(element, 0) + count

    # Generate sorted-descending list of elements by their counts
    sorted_elements = sorted(
        element_counts.keys(), key=lambda x: element_counts[x], reverse=True
    )

    # Create element to index mapping
    element_to_idx = {elem: i for i, elem in enumerate(sorted_elements)}

    # Initialize matrix
    matrix = np.zeros(tuple(len(sorted_elements) for _ in range(n)), dtype=float)

    # Fill matrix using unique n-grams and their counts
    # This works for any n
    for i, ngram_array in enumerate(unique_ngrams):
        ngram_count = counts[i]
        # Reverseing elements to make columns first element and rows second
        idx = tuple(element_to_idx[elem] for elem in ngram_array)[::-1]
        matrix[idx] += ngram_count

    if normalize:
        matrix = matrix / np.sum(matrix)

    return sorted_elements, matrix.tolist()


def shannon_entropy(text: str | list[str]) -> float:
    # Accept either a string and return character entropy,
    # Or a list of words and return word entropy.
    seq = np.array(list(text)) if isinstance(text, str) else np.array(text)
    unique_chars, counts = np.unique(seq, return_counts=True)
    probabilities = counts / len(text)
    entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
    return float(entropy)


def joint_entropy(text: str | list[str], n: int = 2) -> float:
    seq = np.array(list(text)) if isinstance(text, str) else np.array(text)

    if len(seq) < n:
        return 0.0

    # Get each ngram from sequence
    ngrams = [tuple(seq[i : i + n]) for i in range(len(seq) - n + 1)]
    unique_ngrams, counts = np.unique(ngrams, axis=0, return_counts=True)
    probabilities = counts / len(ngrams)
    entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
    return float(entropy)


def conditional_entropy(text: str | list[str], n: int = 2) -> float:
    return joint_entropy(text, n) - shannon_entropy(text)


def length_distribution(words: list[str]) -> tuple[tuple[int, int]]:
    token_length_counts = Counter(len(word) for word in words)
    return tuple(sorted(token_length_counts.items()))  # type: ignore


def all_pos(
    text: str, substring: str, word_mode: bool = True, normalize: bool = True
) -> list[float | int]:
    if not len(substring) or not len(text):
        raise ValueError("text and substring must be non-empty strings")

    # Word mode - must be bounded by one of these chars on both sides
    # Not-word-mode - no boundary requirement, which means that
    # anything longer than 1 could have overlaps (2 'aa' in 'aaa')
    word_bounds = set(".\n")

    indexes = []
    start = 0
    word_len = len(substring)

    while True:
        index = text.find(substring, start)
        if index == -1:
            break
        if word_mode:  # Word mode - check boundaries
            start_valid = index == 0 or text[index - 1] in word_bounds
            end_valid = (
                index + word_len == len(text) or text[index + word_len] in word_bounds
            )

            if start_valid and end_valid:
                indexes.append(index)
        else:  # Letter mode - any match means add it
            indexes.append(index)

        start = index + 1
    if normalize:
        # We want both letters and word positions to be normalized to [0, 1]
        # For letters, they can't be at index len(text), so dividing by it
        # means the max normalized value is somewhat less than 1. so sub 1 to make it exact
        # For words, they can only be at the index after the rightmost .
        # (we're assuming no trailing .'s)
        # Same normalization problem, so set total to 1 to right of rightmost .
        total = text.rfind(".") + 1 if word_mode else len(text) - 1
        if total == 0:
            total = len(text)
        indexes = [idx / total for idx in indexes]
    return indexes


# This can tell you how many characters into a string something is
# But what if I want to know how many words into a line a word is
# Or how many lines into a page
# Or how many pages into the manuscript
# Not sure how much the difference would matter in practice?
def position_distribution(
    items: list[str] | set[str],
    sequences: list[str],
    word_mode: bool = False,
    normalize: bool = True,
    average: bool = False,
) -> dict[str, list[int | float] | int | float]:
    """
    Find all positions of each item in items within the list of sequences.
    """
    items = list(dict.fromkeys(items))  # deduplicate, preserve order
    if not items:
        return {}
    results = defaultdict(list)

    if word_mode:
        # Compile regex to match any of the items as whole words
        # Word boundaries (\b) ensure proper token separation
        # Better when len(items) is large: Aho Corasick algorithm
        pattern = re.compile(r"\b(" + "|".join(map(re.escape, items)) + r")\b")

        for seq in sequences:
            for match in pattern.finditer(seq):
                item = match.group(1)
                pos = match.start()
                if normalize:
                    pos /= len(seq)
                results[item].append(pos)

    else:
        pattern = re.compile("|".join(map(re.escape, items)))

        for seq in sequences:
            for match in pattern.finditer(seq):
                item = match.group(0)
                pos = match.start()
                if normalize:
                    pos /= len(seq)
                results[item].append(pos)

    # Drop items with no matches
    results = {k: v for k, v in results.items() if v}

    if average:
        results = {k: sum(v) / len(v) for k, v in results.items()}
        ordered = {
            k: results[k] for k in items if k in results
        }  # preserve original order
        results = ordered
    else:
        # Sort descending by number of occurrences
        results = dict(sorted(results.items(), key=lambda x: len(x[1]), reverse=True))

    return results  # type: ignore
