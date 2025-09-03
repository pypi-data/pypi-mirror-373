from importlib import resources
import numpy as np
import matplotlib.pyplot as plt
from typing import Sequence
import regex
import re
from dataclasses import dataclass
from pathlib import Path


def preprocess(text: str) -> str:
    # preprocess text by deleting spaces and punctuation then lowercasing
    # \p{C} - Control characters (includes things like null bytes, tabs, newlines)
    # \p{M} - Mark characters (combining marks, accents, diacritics)
    # \p{P} - Punctuation characters (periods, commas, quotes, etc.)
    # \p{S} - Symbol characters (mathematical symbols, currency symbols, etc.)
    # \p{Z} - Separator characters including spaces, tabs, etc
    # regex is imported because standard re does not this type of syntax
    remove = regex.compile(
        r"[\p{P}|\p{S}]+", regex.UNICODE
    )  # space at end of pattern is important!
    text = remove.sub("", text)
    text = re.sub(r"(?:\r?\n){2,}", "\n", text)
    text = text.lower()
    return text


@dataclass
class PlainManuscript:
    text: str

    def to_text(self) -> str:
        return self.text

    def to_words(self) -> list[str]:
        return self.text.split()

    def to_lines(self) -> list[str]:
        return self.text.splitlines()


def load_corpus(
    from_dir: str | None = None,
    names: str | list[str] | None = None,
    prep: bool = True,
    limit_length: int | None = 250_000,
    give_objects: bool = False,
) -> dict[str, str | PlainManuscript]:
    """
    Load plaintext(s) and return dict[name: text]
    Loads from library corpus if from_dir is None
    Otherwise uses all .txt files in from_dir, filename (sans .txt) becoming the name
    Accepts single name, list of names, or None for all available texts
    """
    if from_dir is not None:
        # Convert string path to Traversable using pathlib.Path
        text_dir = Path(from_dir)
    else:
        text_dir = resources.files("pykeedy.data.plaintexts")
    result = {}
    for entry in text_dir.iterdir():
        if entry.is_file() and entry.name.endswith(".txt"):
            name = entry.name.strip(".txt")
            if names is not None:
                if isinstance(names, str):
                    if name != names.strip(".txt"):
                        continue
                elif isinstance(names, list):
                    if name not in [n.strip(".txt") for n in names]:
                        continue
            with entry.open("r", encoding="utf-8") as f:
                text = f.read()
            if prep:
                text = preprocess(text)
            if limit_length and len(text) > limit_length:
                orig_len = len(text)
                text = text[:limit_length]
                print(
                    f"Warning: Truncated text '{name}' from {orig_len} to {limit_length} characters"
                )
            result[name] = text
    if not result:
        raise ValueError("No texts found - check from_dir and names arguments")
    if give_objects:
        result = {name: PlainManuscript(text) for name, text in result.items()}

    return result  # type: ignore


def add_axlabels(key: Sequence[str]) -> None:
    if not all(isinstance(x, str) for x in key) or len(key) != 2:
        raise ValueError("key must contain only 2 strings representing labels")

    plt.xlabel(key[0])
    plt.ylabel(key[1])


def scatterplot(
    d: dict, key: Sequence[str] = ("X", "Y"), fname: str = "scatterplot.png"
) -> None:
    # Expect dict of {name: (x, y)} pairs
    # name: str, x & y: float
    for i, (name, (x, y)) in enumerate(d.items()):
        plt.scatter(x, y, label=name, c=f"C{i}")
        plt.annotate(name, (x, y), xytext=(5, 5), textcoords="offset points")
    add_axlabels(key)
    plt.savefig(fname)
    plt.close()
    print(f"Saved scatter plot to {fname}")


def barplot(
    d: dict,
    key: Sequence[str] = ("Item", "Number"),
    fname: str = "barplot.png",
    n_max: int = 20,
    color: str | None = None,
    title: str | None = None,
) -> None:
    names, values = zip(*d.items())
    names, values = list(names), list(values)
    if len(names) > n_max:
        print(f"Warning: More than {n_max=} items passed to barplot, truncating")
        names, values = names[:n_max], values[:n_max]
    plt.bar(names, values, color=color)
    add_axlabels(key)
    if title:
        plt.title(title)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(fname)
    plt.close()
    print(f"Saved bar plot to {fname}")


def heatmap(
    labels: list[str],
    matrix: list[list[float]],
    key: Sequence[str] = ("First element", "Second element"),
    fname: str = "heatmap.png",
    n_max: int = 20,
    title: str | None = None,
) -> None:
    # Convert to numpy array for easier handling
    matrix_array = np.array(matrix)

    if len(labels) > n_max:
        print(
            f"Warning: More than {n_max=} items passed to heatmap, truncating labels and matrix"
        )
        labels = labels[:n_max]
        matrix_array = matrix_array[:n_max, :n_max]

    # Create the heatmap
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(matrix_array, cmap="plasma", aspect="auto")
    if title:
        plt.title(title, pad=15)

    # Set the ticks and labels
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)

    ax.xaxis.tick_top()
    plt.xticks(rotation=45, ha="left")
    ax.xaxis.set_label_position("top")

    # Add colorbar
    plt.colorbar(im)

    # Add text annotations showing the values
    if len(labels) < 10:
        for i in range(len(labels)):
            for j in range(len(labels)):
                ax.text(
                    j, i, matrix_array[i, j], ha="center", va="center", color="black"
                )

    add_axlabels(key)

    plt.tight_layout()
    plt.savefig(fname)
    plt.close()
    print(f"Saved heatmap to {fname}")


def seriesplot(
    d: dict,
    key: Sequence[str] = ("X", "Y"),
    fname: str = "seriesplot.png",
    title: str | None = None,
) -> None:
    # Expect dict of {name: ((x1,y1), (x2,y2), ...)} pairs
    # name: str, x & y: float
    for i, (name, points) in enumerate(d.items()):
        x_vals, y_vals = zip(*points)
        plt.plot(
            x_vals, y_vals, label=name, c=f"C{i}", marker="o", linewidth=2, markersize=4
        )

    if title:
        plt.title(title)

    plt.legend()

    add_axlabels(key)

    plt.tight_layout()
    plt.savefig(fname)
    plt.close()
    print(f"Saved series plot to {fname}")
