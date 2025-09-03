# type: ignore
from pykeedy.utils import load_corpus, scatterplot, barplot, seriesplot, heatmap
from pykeedy.analysis import (
    shannon_entropy,
    conditional_entropy,
    frequency_rank,
    cooccurence_matrix,
    length_distribution,
    position_distribution,
)
from pykeedy.crypt import naibbe_encrypt
from pykeedy.datastructures import Manuscript
from pykeedy.utils import PlainManuscript
from datetime import datetime
import time
import os
import json

# This file combines all the real analyses from the examples,
# performs all of them on all of the manuscripts in the library corpus, including VMS,
# and saves all the results as pngs in the current folder,
# along with a manifest.json listing all generated files


# All analyses comparing manuscripts against each other
def cross_manuscript(
    texts: dict[str], output_dir: str, add_encrypted: bool, run_entropy: bool
) -> None:
    all = {}
    # Generate all comparison texts
    for name, ms in texts.items():
        text = ms.to_text()
        all[name] = text
        if add_encrypted:
            # Even do VMS itself as a check on encryption effect
            all[name + "_naibbe"] = naibbe_encrypt(text)

    if run_entropy:
        entropy = {}
        for name, text in all.items():
            entropy[name] = (shannon_entropy(text), conditional_entropy(text))

        # Generate entropy plot
        scatterplot(
            entropy,
            key=("character entropy (bits)", "conditional entropy (bits)"),
            fname=f"{output_dir}/entropy_comparison.png",
        )


# All analyses on individual manuscripts
# Called once per manuscript, so accepts a single one, not multiple like cross_manuscript
def per_manuscript(
    name: str,
    i: int,
    ms: Manuscript | PlainManuscript,
    output_dir: str,
    run_ngrams: bool,
    ngram_max_n: int,
    run_heatmaps: bool,
    run_lengths: bool,
    run_positions: bool,
) -> None:
    # Per-manuscript analysis
    barplot_colors = [
        "red",
        "blue",
        "green",
        "orange",
        "purple",
        "brown",
        "pink",
        "gray",
        "olive",
        "cyan",
    ]
    color = barplot_colors[i]

    # For ngrams and heatmaps, always do them at both character and word level
    for mode in ["char", "word"]:
        if run_ngrams:
            # Generate ngram plots
            text = ms.to_text() if mode == "char" else ms.to_words()
            for i in range(ngram_max_n):
                gramsize = i + 1
                barplot(
                    frequency_rank(text, n=gramsize),
                    key=(f"{mode} {gramsize}-gram", "Frequency"),
                    fname=f"{output_dir}/{name}_{mode}_{gramsize}-gram_freq.png",
                    color=color,
                    title=f"{name} ngram freq",
                )
        if run_heatmaps:
            # Generate heatmaps
            res = cooccurence_matrix(text, n=2)
            heatmap(
                *res,
                fname=f"{output_dir}/{name}_{mode}_cooccurence_heatmap.png",
                title=f"{name} {mode} co-occurence",
            )

    if run_lengths:
        # Generate word length plots
        words = ms.to_words()
        results = {
            "token": length_distribution(words),
            "type": length_distribution(list(set(words))),
        }

        seriesplot(
            results,
            key=("Word length", "Count"),
            fname=f"{output_dir}/{name}_word_lengths.png",
            title=f"{name} word length",
        )

    if run_positions:
        text = ms.to_text()
        letters = set(text)
        word_tokens = ms.to_words()
        lines = ms.to_lines()

        # Positions of letters in words
        all_pos = position_distribution(
            letters, word_tokens, normalize=True, average=False
        )
        many_occurs = {k: sum(v) / len(v) for k, v in all_pos.items() if len(v) > 200}
        barplot(
            many_occurs,
            key=("Letter (most common on left)", "Avg pos in word"),
            fname=f"{output_dir}/{name}_letters_pos_in_words.png",
            n_max=len(many_occurs),
            color=color,
            title=f"{name} letter positions in words",
        )

        # Positions of 20 most common words
        top_words = [k for k, v in frequency_rank(word_tokens).items()][:20]

        barplot(
            position_distribution(top_words, lines, word_mode=True, average=True),
            key=("Word (most common on left)", "Avg pos in line"),
            fname=f"{output_dir}/{name}_words_pos_in_lines.png",
            color=color,
            title=f"{name} word positions in lines",
        )
        barplot(
            position_distribution(top_words, [text], word_mode=True, average=True),
            key=("Word (most common on left)", "Avg pos in VMS"),
            fname=f"{output_dir}/{name}_words_pos_in_manuscript.png",
            color=color,
            title=f"{name} word positions in manuscript",
        )


def run_full_analysis(
    voynich: Manuscript,
    comparison_texts_dir: str | None = None,
    comparison_text_names: list[str] | None = None,
    output_dir: str = "full_analysis_results",
    add_encrypted: bool = True,
    run_entropy: bool = True,
    run_ngram_freqs: bool = True,
    ngram_max_n: int = 3,
    run_cooccurence: bool = True,
    run_word_lengths: bool = True,
    run_positions: bool = True,
) -> None:
    # Currently available analyses
    run_cross_manuscript = any([run_entropy])
    run_per_manuscript = any(
        [run_ngram_freqs, run_cooccurence, run_word_lengths, run_positions]
    )

    start = time.time()

    os.makedirs(output_dir, exist_ok=True)

    if comparison_texts_dir:
        texts = load_corpus(
            from_dir=comparison_texts_dir,
            names=comparison_text_names,
            give_objects=True,
        )
    else:
        texts = load_corpus(names=comparison_text_names, give_objects=True)
    texts["VMS"] = voynich

    if run_cross_manuscript:
        cross_manuscript(
            texts=texts,
            output_dir=output_dir,
            add_encrypted=add_encrypted,
            run_entropy=run_entropy,
        )

    if run_per_manuscript:
        for i, (name, ms) in enumerate(texts.items()):
            per_manuscript(
                name=name,
                i=i,
                ms=ms,
                output_dir=output_dir,
                run_ngrams=run_ngram_freqs,
                ngram_max_n=ngram_max_n,
                run_heatmaps=run_cooccurence,
                run_lengths=run_word_lengths,
                run_positions=run_positions,
            )

    analysis_manifest = {
        "analysis": {
            "generated_at": datetime.now().isoformat(),
            "manuscripts": list(texts.keys()),
            "cross_manuscript": ["entropy_comparison.png"],
            "per_manuscript": {
                # If any of the calculated plots are missing from here they will not be displayed in whatever parses this
                "char_ngram_freq": [
                    "<name>_char_1-gram_freq.png",
                    "<name>_char_2-gram_freq.png",
                    "<name>_char_3-gram_freq.png",
                ],
                "word_ngram_freq": [
                    "<name>_word_1-gram_freq.png",
                    "<name>_word_2-gram_freq.png",
                    "<name>_word_3-gram_freq.png",
                ],
                "cooccurence_heatmaps": [
                    "<name>_char_cooccurence_heatmap.png",
                    "<name>_word_cooccurence_heatmap.png",
                ],
                "word_lengths": ["<name>_word_lengths.png"],
                "positions": [
                    "<name>_letters_pos_in_words.png",
                    "<name>_words_pos_in_lines.png",
                    "<name>_words_pos_in_manuscript.png",
                ],
            },
        }
    }
    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(analysis_manifest, f, indent=4)

    finish = time.time()
    print(
        f"Completed analysis of {len(texts)} manuscripts in {finish - start:.2f} seconds"
    )
