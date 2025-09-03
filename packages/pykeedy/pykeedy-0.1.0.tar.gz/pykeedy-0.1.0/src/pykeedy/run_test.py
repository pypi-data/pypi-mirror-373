from pykeedy import VMS
from pykeedy.analysis import conditional_entropy, shannon_entropy
from typing import Literal
from pykeedy.crypt import greshko_decrypt, naibbe_encrypt
from pykeedy.utils import load_corpus, preprocess
import numpy as np


def test_reconstruction(text: str, n: int = 1000) -> float:
    def levenshtein(a, b):
        if len(a) < len(b):
            return levenshtein(b, a)
        if len(b) == 0:
            return len(a)

        prev = list(range(len(b) + 1))
        for i, ca in enumerate(a):
            curr = [i + 1]
            for j, cb in enumerate(b):
                curr.append(
                    min(
                        prev[j + 1] + 1,  # deletion
                        curr[j] + 1,  # insertion
                        prev[j] + (ca != cb),
                    )
                )  # substitution
            prev = curr
        return prev[-1]

    avg = 0
    pre = preprocess(text)
    for i in range(n):
        decoded = greshko_decrypt(
            naibbe_encrypt(text, prngseed=np.random.randint(0, 2**32))
        )
        correct = len(pre) - levenshtein(decoded, pre)
        # print(decoded)
        # print(pre)
        # print(correct)
        # print(len(pre))
        avg += correct / len(pre)

    rec = avg / n
    print(
        f"Reconstruction accuracy: {rec * 100:.2f}% over {n} trials of text length {len(pre)}"
    )
    return rec


def test_entropy(
    encode_seeds: int = 1, mode: Literal["char", "word"] = "char"
) -> dict[str, tuple[float, float]]:
    # Load all available texts and encrypt each encode_seeds times
    # Add vms to corpus then calculate shannon & conditional entropy of each and return dict {name: (shannon, conditional)}
    if mode not in ("char", "word"):
        raise ValueError("mode must be 'char' or 'word'")
    plain = load_corpus()
    all: dict = {}
    for name, text in plain.items():
        all[name] = text
        for i in range(encode_seeds):
            all[name + f"_enc{i}"] = naibbe_encrypt(text, prngseed=i)
    all["vms"] = VMS.to_text()
    if mode == "word":
        for name, text in all.items():
            all[name] = text.split(" ")
    results = {}
    for name, text in all.items():
        results[name] = (shannon_entropy(text), conditional_entropy(text))

    return results
