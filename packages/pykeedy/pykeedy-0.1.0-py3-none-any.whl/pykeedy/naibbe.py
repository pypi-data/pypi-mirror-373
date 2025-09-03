from pydantic import BaseModel, model_validator
import yaml
from pathlib import Path
import importlib.resources as resources
from functools import lru_cache
from typing import ClassVar


class NaibbeEncoding(BaseModel):
    name: str | None = None
    ngram_slot_tables: list[
        dict[str, list[str]]
    ]  # [unigram, bigram_prefix, bigram_suffix, ...] - order extremely important for lists!
    table_odds: (
        list[float] | list[list[float]]
    )  # e.g. [5, 2, 2, 2, 1, 1] - order corresponding to lists in ngram_slot_tables
    ngram_odds: list[float] | None = (
        None  # [1, 1] for equal odds unigram + bigram - order is ascending (first position is unigram, second bigram)
    )

    VALID_TABLES: ClassVar[tuple] = (
        "unigram",
        "bigram_prefix",
        "bigram_suffix",
        "trigram_prefix",
        "trigram_core",
        "trigram_suffix",
    )

    @model_validator(mode="after")
    def check_encoding(self) -> "NaibbeEncoding":
        if self.ngram_odds is None:
            self.ngram_odds = [1.0]
        num_ngrams = len(self.ngram_odds)
        num_tables = num_ngrams * (num_ngrams + 1) // 2
        # one slot per table
        # unigram only -> 1 table
        # unigram + bigram -> 3 tables (Greshko encoding)
        # unigram + bigram + trigram -> 6 tables

        if len(self.ngram_slot_tables) != num_tables:
            raise ValueError(
                "Number of possible ngram lengths and number of tables do not match"
            )

        # Limit to trigram (most of code should work for higher, limit mostly for more clarity in certain areas)
        if len(self.ngram_odds) > 3:
            raise ValueError("Only up to trigrams are supported")

        alphabet = {}
        num_encodings = 0
        for i, tab in enumerate(self.ngram_slot_tables):
            if i == 0:
                alphabet = set(tab.keys())
                if any(len(char) > 1 for char in alphabet):
                    raise ValueError(
                        "ngram slot tables must have only single letters as keys"
                    )
            else:
                if set(tab.keys()) != alphabet:
                    raise ValueError(
                        "All ngram_tables must use the same plaintext alphabet"
                    )

            lengths = set(len(v) for v in tab.values())
            if len(lengths) != 1:
                raise ValueError(
                    f"Each encoding table must have same number of encodings per character (problem with table: {self.tabname(i)})"
                )

            if i == 0:
                num_encodings = len(list(tab.values())[0])
                if isinstance(
                    self.table_odds[0], float
                ):  # single common odds list for all slots
                    if len(self.table_odds) != num_encodings:
                        raise ValueError(
                            "If table_odds is a single list, it must have the same length as the number of encodings per character"
                        )
                elif isinstance(
                    self.table_odds[0], list
                ):  # leaving the door open for slots having different numbers of encodings in future (len would be checked)
                    if len(self.table_odds[i]) != len(self.ngram_slot_tables):  # type: ignore
                        raise ValueError(
                            "If table_odds is a list of lists, it must have the same length as ngram_tables"
                        )
            else:
                if len(list(tab.values())[0]) != num_encodings:
                    raise ValueError(
                        "All tables must have the same number of encodings per character"
                    )

        return self

    @classmethod
    def from_name(cls, name: str) -> "NaibbeEncoding":
        encodings = load_encodings()
        if name not in encodings:
            raise ValueError(
                f"Encoding '{name}' not found. Available encodings: {list(encodings.keys())}"
            )
        filename = encodings[name]
        enc_dir = resources.files("pykeedy.data.encodings")
        filepath = enc_dir / filename
        with resources.as_file(filepath) as file:
            return cls.from_file(file)

    @classmethod
    def from_file(cls, filepath: Path) -> "NaibbeEncoding":
        with open(filepath, "r") as f:
            data: dict = yaml.safe_load(f)
        try:
            data = data["encoding"]
        except KeyError:
            raise ValueError(
                "Encoding YAML file must contain 'encoding' as top-level key"
            )

        tables = []
        valid_tables: tuple = cls.VALID_TABLES  # type: ignore
        for tabname in valid_tables:
            if tabname in data:
                tables.append(data.pop(tabname))
        if len(tables) == 0:
            raise ValueError(
                f"No valid encoding tables found in file. Valid names: {valid_tables}"
            )
        data["ngram_slot_tables"] = tables

        for valname in ("name", "table_odds", "ngram_odds"):
            if valname not in data:
                raise ValueError(f"Encoding YAML file must contain '{valname}' key")

        return cls(**data)

    def to_file(self, filepath: Path) -> None:
        if self.name is None:
            raise ValueError("Encoding must have a name to be saved to file")
        data = {
            "name": self.name,
            "table_odds": self.table_odds,
            "ngram_odds": self.ngram_odds,
        }
        valid_tables = (
            "unigram",
            "bigram_prefix",
            "bigram_suffix",
            "trigram_prefix",
            "trigram_core",
            "trigram_suffix",
        )
        for i, tabname in enumerate(valid_tables):
            if i < len(self.ngram_slot_tables):
                data[tabname] = self.ngram_slot_tables[i]

        with open(filepath, "w") as f:
            yaml.dump({"encoding": data}, f)

    def print(self) -> None:
        print("NaibbeEncoding(")
        print("    ngram_slot_tables = [")

        for i, table in enumerate(self.ngram_slot_tables):
            print(f"        # {self.tabname(i)} table")
            print("        {")
            for key, value in table.items():
                print(f'            "{key}": {value},')
            print("        },")

        print("    ],")
        print(f"    table_odds = {self.table_odds},")
        print(f"    ngram_odds = {self.ngram_odds}")
        print(")")

    def save(self) -> None:
        if self.name is None:
            raise ValueError("Encoding must have a name to be saved to file")
        self.to_file(Path(f"{self.name}.yaml"))

    @property
    def alphabet(self) -> str:
        return "".join(sorted(self.ngram_slot_tables[0].keys()))

    @property
    def common_table_odds(self) -> bool:
        # Checks if table_odds is a single list (same odds for all slots) or a list of lists (different odds for each slot)
        return isinstance(self.table_odds[0], float)

    @property
    def get_slot_decrypt_tables(self) -> list[dict[str, str]]:
        # return: [slot1decode, slot2decode, slot3decode]
        # slot1decode: {"qokchedy": "h", "okchedy": "h", ...}
        return [
            {enc: char for char, encs in slot_dict.items() for enc in encs}
            for slot_dict in self.ngram_slot_tables
        ]

    @property
    def get_slot_lists(self) -> list[list[str]]:
        # return: [slot1list, slot2list, slot3list]
        # slot1list: ["qokchedy", "okchedy", ...]
        return [list(dec.keys()) for dec in self.get_slot_decrypt_tables]  # type: ignore

    def tabname(self, tab: int) -> str:
        names = (
            "unigram",
            "bigram prefix",
            "bigram suffix",
            "trigram prefix",
            "trigram core",
            "trigram suffix",
        )
        try:
            return names[tab]
        except IndexError:
            raise ValueError("Only up to trigrams are supported")

    def ambiguousity(self):
        # Debug for now, later return a value for exactly how ambiguous encoding is.

        # An encoding is ambiguous if and only if:
        # -For any slot (unigram, bigram prefix, bigram suffix) there is a duplicate (among any character or table)
        # -An encoding from an earlier slot can be built from a combination of later ones
        # -There is overlap in the valid ngrams for n>2

        def find_duplicates(lst):
            seen = set()
            duplicates = set()

            for item in lst:
                if item in seen:
                    duplicates.add(item)
                else:
                    seen.add(item)

            return list(duplicates)

        # Check first case
        for i, chartab in enumerate(self.ngram_slot_tables):
            # Encodings within the same slot and letter don't have to be unique to be unambiguous, so take their set
            all_encs = [enc for encs in chartab.values() for enc in set(encs)]
            encset = set(all_encs)
            print(f"{self.tabname(i)}: {len(encset)} / {len(all_encs)} (unique/total)")
            # if len(encset) != len(all_encs):
            #     print(f"Duplicate encodings in {self.tabname(i)} table ({find_duplicates(all_encs)})")
            #     return True

        # Check second case
        if len(self.ngram_odds) == 2:
            unigram_encs = set(
                enc for encs in self.ngram_slot_tables[0].values() for enc in encs
            )
            bigram_prefix_encs = set(
                enc for encs in self.ngram_slot_tables[1].values() for enc in encs
            )
            bigram_suffix_encs = set(
                enc for encs in self.ngram_slot_tables[2].values() for enc in encs
            )

            bigrams = []

            for bpre in bigram_prefix_encs:
                for bsuf in bigram_suffix_encs:
                    bigrams.append(bpre + bsuf)
            bigram_set = set(bigrams)
            print(f"bigrams: {len(bigram_set)} / {len(bigrams)} (unique/total)")
            intersection = bigram_set.intersection(unigram_encs)
            if len(intersection) > 0:
                print(f"Unigram-bigram collision: {len(intersection)}")
                return True
            if len(bigram_set) != len(bigrams):
                print("Intersection within bigrams")
                return True
            return False

        elif len(self.ngram_odds) == 3:
            raise NotImplementedError

        else:
            raise ValueError("Only up to trigram supported")


@lru_cache(maxsize=1)
def get_default_encoding() -> NaibbeEncoding:
    DEFAULT_ENCODING_NAME: str = "greshko_202507"
    return NaibbeEncoding.from_name(DEFAULT_ENCODING_NAME)


def parse_encoding(encoding: NaibbeEncoding | str | None) -> NaibbeEncoding:
    if not isinstance(encoding, NaibbeEncoding):
        if isinstance(encoding, str):
            encoding = NaibbeEncoding.from_name(encoding)
        elif encoding is None:
            encoding = get_default_encoding()
    return encoding


@lru_cache(maxsize=1)
def _load_encodings() -> dict[str, str]:  # [enc_name: filename]
    enc_dir = resources.files("pykeedy.data.encodings")
    result = {}
    for entry in enc_dir.iterdir():
        if entry.is_file() and entry.name.endswith(".yaml"):
            with entry.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            try:
                result[data["encoding"]["name"]] = entry.name
            except KeyError:
                print(
                    f'Warning: Encoding file {entry.name} does not contain "encoding"->"name" key and cannot be parsed, skipping'
                )
    return result


def load_encodings(force_update: bool = False) -> dict[str, str]:
    if force_update:
        _load_encodings.cache_clear()
    return _load_encodings()
