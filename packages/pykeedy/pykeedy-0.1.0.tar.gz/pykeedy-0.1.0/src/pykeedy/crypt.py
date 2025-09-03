from pykeedy.naibbe import NaibbeEncoding, parse_encoding
import numpy as np
from pykeedy.utils import preprocess
import re


def naibbe_encrypt(
    text: str, encoding: NaibbeEncoding | str | None = None, prngseed: int | None = 42
) -> str:
    """
    Encrypt text using some Naibbe encoding.
    Note that this is a general implementation for encodings with any number of characters, ngram lengths, probabilities, etc.
    A function for only unigram-bigram encodings would be simpler.
    """
    encoding = parse_encoding(encoding)
    text = preprocess(text)
    alphabet_exclude = f"[^{encoding.alphabet}]"
    orig_len = len(text)
    text = re.sub(alphabet_exclude, "", text)
    if len(text) != orig_len:
        print(
            f"Warning: {orig_len - len(text)}/{orig_len} characters were removed from input text because they are not in the encoding alphabet"
        )

    if prngseed is None:
        prngseed = np.random.randint(0, 2**32)
    rng = np.random.default_rng(seed=prngseed)

    def odds_to_thresholds(odds: list[float]) -> np.ndarray:
        # process ordered odds lists to make it easy to select option (ngram length, or, table to use) from a randomly generated number
        # normalize sum of list to 1, then cumsum to get thresholds - last element should always be ~1,
        # which is discarded (rolled to first element then replaced with 0)
        # example: [1 1 1] -> [0 0.3333 0.6666]

        oddsarr = np.array(odds)
        thresharr = np.roll(np.cumsum(oddsarr / np.sum(oddsarr)), 1)
        thresharr[0] = 0.0
        return thresharr

    ngram_length_thresholds = odds_to_thresholds(encoding.ngram_odds)  # type: ignore - not None guaranteed during model validation

    table_thresholds_array = None
    # make and copy single thresholds table if each has the same odds, otherwise do for each
    # copying means we just assume each table has its own odds instead of branching later
    if encoding.common_table_odds:
        table_thresholds = odds_to_thresholds(encoding.table_odds)  # type: ignore
        table_thresholds_array = np.array(
            [table_thresholds for _ in range(len(encoding.ngram_slot_tables))]
        )
    else:
        table_thresholds_array = np.array(
            [odds_to_thresholds(to) for to in encoding.table_odds]
        )  # type: ignore

    def select_option(thresholds: np.ndarray) -> int:
        # using the precomputed threshold table, generate a random number, then see where it falls on the table (the largest index it is larger than)
        # to select how many characters to encode in a word or which table to use for a character
        rand = rng.random()  # 0 -> 1
        return np.nonzero(thresholds < rand)[0][-1]

    i = 0
    encoded = ""
    while i < len(text):
        gramsize = select_option(ngram_length_thresholds) + 1  # select ngram size

        if i + gramsize > len(
            text
        ):  # not enough characters left for selected ngram size, so use smaller
            gramsize = len(text) - i

        start_table_idx = (
            0 if gramsize == 1 else 1 if gramsize == 2 else 3
        )  # Only support up to trigrams (same as NaibbeEncoding)

        word = ""

        for j in range(gramsize):
            char = text[i + j]
            if char not in str(encoding.alphabet):
                raise ValueError(
                    f"Character '{char}' at position {i + j} not in encoding alphabet"
                )
            table = select_option(table_thresholds_array[start_table_idx + j])
            word += encoding.ngram_slot_tables[start_table_idx + j][char][table]
        i += gramsize
        encoded += word + " "

    return encoded.strip()


def greshko_decrypt(encoded: str, encoding: NaibbeEncoding | str | None = None) -> str:
    # IMPORTANT: If the encoding is ambiguous (Greshko encoding is), some information is lost in the encryption/decryption process. With this decoding algorithm and the current encoding algorithm reconstruction rate is 95%.

    # This uses the algorithm from the paper (Greshko 2025). It makes use of properties of the encoding tables so it will not work for other encodings!
    # Strategy is important because the encoding is not just a little ambiguous - 90% of unigrams are also valid bigrams.
    # Step 1: If word is a valid unigram, decode it as such (it is usually the far more likely option even if it's also a bigram)
    # Step 2: Use "breakpoint" strings: There are strings unique to one of the two word types that bigrams are built from (type 1/2 affixes). Type 1 is very likely to be a prefix and type 2 to be a suffix, so the rightmost breakpoint string in a suffix or leftmost in a prefix defines the breakpoint, both affixes are then parsed (prefix and suffix tables are unique)
    # Step 3: Refer to a grammar slot table. Check each character against successive slots until there's a match, then decode the prefix as the longest valid string.

    # One can imagine algorithms that do various types of "greedy parsing" to find the likeliest decoding instead of using a hardcoded method and this is a future goal.
    # When doing this it will also be important to focus on the 15th-century-human-doability as the paper does.

    encoding = parse_encoding(encoding)

    if encoding.name != "greshko_202507":
        raise NotImplementedError("Decryption for other encodings not yet implemented")

    prefix_only_strs = ["ch", "sh", "cfh", "ckh", "cph", "cth", "f", "k", "p", "t", "x"]
    suffix_only_strs = ["a", "e", "g", "i", "m", "n"]

    t1_slots = [
        ["q", "s", "d", "x"],
        ["o", "y"],
        ["d", "r"],
        ["t", "k", "p", "f"],
        ["ch", "sh"],
        ["cth", "ckh", "cph", "cfh"],
    ]

    t2_slots = [
        ["e", "ee", "eee", "g"],
        ["s", "d"],
        ["o", "a"],
        ["i", "ii", "iii"],
        ["d", "l", "r", "m", "n"],
        ["s"],
        ["y"],
    ]

    slot_decrypt_tables: list[dict[str, str]] = encoding.get_slot_decrypt_tables  # type: ignore

    slot_lists: list[list[str]] = encoding.get_slot_lists  # type: ignore

    def common_prefix_length(s1: str, s2: str) -> int:
        # Finds length of common prefix between two strings
        # "Prefix" used here entirely unrelated to voynich grammar
        i = 0
        min_len = min(len(s1), len(s2))

        while i < min_len and s1[i] == s2[i]:
            i += 1

        return i

    def slot_hit(glyph: str, vord_remaining: str) -> bool:
        return common_prefix_length(glyph, vord_remaining) == len(glyph)

    def get_longest_affix(vord: str, slots: list[list[str]]) -> int:
        i = 0
        for slot_options in slots:
            best = 0
            for glyph in slot_options:
                if slot_hit(glyph, vord[i:]):
                    best = len(glyph)
            i += best
        return i

    def parse_from_breakpoint(vord: str, pt: int) -> str:
        pre = vord[:pt]
        suf = vord[pt:]
        return slot_decrypt_tables[1][pre] + slot_decrypt_tables[2][suf]

    def step1(vord: str) -> str | None:
        if vord in slot_lists[0]:
            return slot_decrypt_tables[0][vord]

    def step2(vord: str) -> str | None:
        best = None
        for glyph in prefix_only_strs:  # Get rightmost prefix glyph
            pos = vord.rfind(glyph)
            if pos != -1:
                if best is None or pos > best:
                    best = pos + len(glyph)
        for glyph in suffix_only_strs:  # Get leftmost suffix glyph
            pos = vord.find(glyph)
            if pos != -1:
                if best is None or pos < best:
                    best = pos
        if best and best > 0:
            try:
                # Sometimes the process is just wrong because type 1 affixes can be suffixes and vice versa,
                # so have to catch it and continue to step. words caught here tend to have no type 1 affix glyphs
                # example: daleor, lsdaiin, oldal, alaiin, aleedal, qodain...
                return parse_from_breakpoint(vord, best)
            except KeyError:
                return None

    def step3(vord: str) -> str | None:
        t1 = get_longest_affix(vord, t1_slots)
        t2 = get_longest_affix(vord, t2_slots)
        longest_idx = max(t1, t2)

        try:
            return parse_from_breakpoint(vord, longest_idx)
        except (IndexError, KeyError):
            return None

    vords = encoded.split(" ")
    decoded = ""  # We add to this with each decode
    for vord in vords:  # Each word is entirely independent
        for i, step in enumerate([step1, step2, step3]):
            res = step(vord)  # Result is either successfully decoded text or None
            if res is not None:
                decoded += res
                break
            if i == 2:
                # We're after the last step (i==2) and found nothing
                # (any success would've broken out of the lower loop)
                decoded += "?"

        # Problem grams:
        # qol + o - grammar suggests qo + lo, lo is invalid (same for qolor)
        # o + ry / or + y - is also a valid t2 gram, so greedy parsing leaves no suffix
        # aiir + y - valid t2 gram
    return decoded
