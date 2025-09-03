import re
from enum import Enum
from dataclasses import dataclass, fields
from typing import Callable, Sequence, Literal
import importlib.resources as resources
from functools import lru_cache


class LocusPropType:
    # A way to tell that something is a filterable property
    pass


class LocusProp:
    class Location(LocusPropType, Enum):
        UnrelatedToPrev = "@"
        BelowPrev = "+"
        BelowAndLeftOfPrev = "*"
        RightOfPrev = "="
        AlongArcFromPrev = "&"
        RightishFromPrev = "~"
        AboveAndRightOfPrev = "/"
        DoesNotExist = "!"

    class Type(LocusPropType, Enum):
        # P: Linear text in paragraphs
        ParagraphLeftJustified = "P0"
        ParagraphNotLeftJustified = "P1"
        ParagraphFreeFloating = "Pb"
        ParagraphCentered = "Pc"
        ParagraphRightJustified = "Pr"
        ParagraphRightJustifiedTitle = "Pt"

        # L: Short piece of text, a word, or a character that is anywhere on the page, mostly labels
        NotDrawingAssociated = "L0"
        AstronomicalLabel = "La"
        PharmaceuticalContainerLabel = "Lc"
        HerbalFragmentLabel = "Lf"
        BiologicalNymphLabel = "Ln"
        HerbalLargePlantLabel = "Lp"
        StarLabel = "Ls"
        BiologicalTubeLabel = "Lt"
        ExtraneousWriting = "Lx"
        ZodiacLabel = "Lz"

        # C: Text along circumference of circle
        CircumferentialClockwise = "Cc"
        CircumferentialCounterClockwise = "Ca"

        # R: Text along radius of circle
        RadialInwards = "Ri"
        RadialOutwards = "Ro"

    class IllustrationType(LocusPropType, Enum):
        Astronomical = "A"
        Biological = "B"
        Cosmological = "C"
        Herbal = "H"
        Pharmaceutical = "P"
        MarginalStarsOnly = "S"
        TextOnly = "T"
        Zodiac = "Z"

    class CurrierLanguage(LocusPropType, Enum):
        A = "A"
        B = "B"

    class DavisHand(LocusPropType, Enum):
        H1 = "1"
        H2 = "2"
        H3 = "3"
        H4 = "4"
        H5 = "5"
        At = "@"

    class CurrierHand(LocusPropType, Enum):
        C1 = "1"
        C2 = "2"
        C3 = "3"
        C4 = "4"
        C5 = "5"
        X = "X"
        Y = "Y"  # IVTFF format pdf and transliteration do not match - pdf claims X + Z, actual transliteration has X + Y

    class ExtraneousWriting(LocusPropType, Enum):
        ColorAnnotation = "C"
        MonthName = "M"
        Other = "O"
        CharOrNumSequence = "S"
        Various = "V"  # This is deprecated but still in the source for some reason.

    @classmethod
    def prop_types(cls) -> list[type]:
        return [
            LocusProp.Location,
            LocusProp.Type,
            LocusProp.IllustrationType,
            LocusProp.CurrierLanguage,
            LocusProp.DavisHand,
            LocusProp.CurrierHand,
            LocusProp.ExtraneousWriting,
        ]

    @classmethod
    def print_props(cls) -> None:
        for proptype in cls.prop_types():
            print(f"LocusProp.{proptype.__name__}:")
            for item in proptype:  # type: ignore
                print(f"  {item.name}")


class VMSDataclass:
    @classmethod
    def print_fields(cls) -> None:
        print(f"{cls.__name__} fields:")
        for field in fields(cls):  # type: ignore
            print(f"Name: {field.name}")


# Transliteration issues:
#   - Rosette page lacking folio number, inconsistent with other headers (this is the only reason folios_in_quire can be None)
#   - IVTFF source says Currier hands contains X & Z but it actually contains X & Y


@dataclass
class Locus(VMSDataclass):
    # Page properties
    quire_num: int
    page_in_quire_num: int
    folio_in_quire_num: int | None
    bifolio_in_quire_num: int
    illustration: LocusProp.IllustrationType
    currier_language: LocusProp.CurrierLanguage | None
    davis_hand: LocusProp.DavisHand
    currier_hand: LocusProp.CurrierHand | None
    extraneous_writing: LocusProp.ExtraneousWriting | None

    # This can be grabbed from either page or locus level
    # Constructor chooses to grab from locus level
    page_name: str
    # Locus properties

    id_str: str
    locus_in_page_num: int
    location: LocusProp.Location
    type: LocusProp.Type
    text: str

    @classmethod
    def from_line(cls, page_props: tuple, line: str) -> "Locus":
        num_props_from_page_level = 9
        if len(page_props) != num_props_from_page_level:
            raise ValueError(
                f"Incorrect page_props passed to locus constructor, expecting len = {num_props_from_page_level}, got {len(page_props)}"
            )
        # Expects line to be a single locus, with no page headers or comments as lines
        # Example line: "<f89v1.23,@Lf>    opol.olaiin" (no \n)
        # So we want to extract page name, locus number in page, location & type code (3 characters), and text.
        line = re.sub(
            r"<[!@%$].*?>", "", line
        )  # Remove inline comments except interruption tags <[-~]>
        match = re.match(r"<([^.]+)\.([^,]+),([^>]+)>\s*([a-zA-Z?].*)", line)
        # Important parts of above line:

        if not match:
            raise ValueError(f"Line does not match expected locus format: {line}")
        page_name = match.group(1)
        locus_in_page_num = int(match.group(2))

        # Extract 3 character code. First character is location, next two are type.
        loctypecode = match.group(3)
        if len(loctypecode) != 3:  # Must be 3 characters
            raise ValueError(
                f"Corrupted IVTFF file: Locus location & type code must be exactly 3 characters: {loctypecode}"
            )
        locus_location = LocusProp.Location(loctypecode[0])
        locus_type = LocusProp.Type(loctypecode[1:])
        text = match.group(4).strip()
        id_str = f"{page_name}.{locus_in_page_num}"
        return cls(
            *page_props,
            page_name=page_name,
            id_str=id_str,
            locus_in_page_num=locus_in_page_num,
            location=locus_location,
            type=locus_type,
            text=text,
        )

    def props(self) -> list[LocusPropType]:
        return [val for val in self.__dict__.values() if isinstance(val, LocusPropType)]

    def is_label(self) -> bool:
        return "Label" in self.type.name

    def is_paragraph(self) -> bool:
        return "Paragraph" in self.type.name

    def is_below_prev(self) -> bool:
        return "Below" in self.location.name


# Tries to convert strings of form 'letter' or 'numbers' to int.
def to_int(letter: str) -> int:  # A -> 1, B -> 2 ...
    if len(letter) != 1:
        raise ValueError("str must be single character")
    try:
        return int(letter)
    except ValueError:
        if not letter.isalpha():
            raise ValueError("letter str must be alphabetic")
        return ord(letter.upper()) - ord("A") + 1


def loci_list_from_lines(lines: list[str], header: str) -> list[Locus]:
    # Expects each line to be one locus, with no page headers or comments as lines
    # Header example: "$Q=M $P=R $F=y $B=2 $I=B $L=B $H=2 $C=2"
    # We don't care about page name because that is in each line as well as the page header,
    # so the choice was made to extract it at the locus level to ensure it can't be wrong.
    pattern = r"\$([A-Z])=([A-Za-z0-9])"

    # This encodes the order and thing to be called for letter, we'll use it to build a tuple to pass into constructor.
    letters: dict[str, Callable] = {
        # Below 4: we will need to convert from string to int, rest of types are StrEnums so can pass string directly
        "Q": to_int,
        "P": to_int,
        "F": to_int,
        "B": to_int,
        "I": LocusProp.IllustrationType,
        "L": LocusProp.CurrierLanguage,
        "H": LocusProp.DavisHand,
        "C": LocusProp.CurrierHand,
        "X": LocusProp.ExtraneousWriting,
    }

    # Dict e.g. {'Q': 'M', 'P': 'R', ...}
    props_pairs = dict(re.findall(pattern, header))

    # For each possible property, get its value if it is present in this header, then pass it to that property's callable.
    # if it isn't present then use None.
    props = tuple(
        func(props_pairs[key]) if key in props_pairs else None
        for key, func in letters.items()
    )

    # This function is sensitive to the order of the above dict matching the order of constructor parameters. Maybe use type introspection?
    return [Locus.from_line(page_props=props, line=line) for line in lines]


def to_alphabet(text: str, alphabet: Literal["eva", "cuva"]) -> str:
    subs = [
        (r"a", "A"),
        (r"b", "B"),
        (r"cfh", "FS"),
        (r"ch", "S"),
        (r"ckh", "KS"),
        (r"cph", "PS"),
        (r"cth", "TS"),
        (r"d", "D"),
        (r"e", "E"),
        (r"ee", "U"),
        (r"eee", "UE"),
        (r"eeee", "UU"),
        (r"f", "F"),
        (r"g", "G"),
        (r"i", "I"),
        (r"ii", "N"),
        (r"iii", "M"),
        (r"iin", "M"),
        (r"iiin", "NN"),
        (r"in", "N"),
        (r"j", "Q"),
        (r"k", "K"),
        (r"l", "L"),
        (r"m", "J"),
        (r"n", "I"),
        (r"o", "O"),
        (r"p", "P"),
        (r"q", "H"),
        (r"r", "R"),
        (r"s", "C"),
        (r"sh", "Z"),
        (r"t", "T"),
        (r"u", "A"),
        (r"v", "V"),
        (r"x", "X"),
        (r"y", "Y"),
        (r"z", "J"),
    ]
    if alphabet.lower() not in ("eva", "cuva"):
        raise ValueError("alphabet must be 'eva' or 'cuva'")
    match alphabet:
        case "eva":
            return text
        case "cuva":
            for string, sub in subs:
                text = re.sub(string, sub, text)
            return text


def strip_inline_metadata(
    text: str, normalize_gaps: bool, delete_comments: bool
) -> str:
    if delete_comments:
        # There are only like 3 of these in the text
        text = re.sub(r"<[!@%$].*?>", "", text)
    if normalize_gaps:
        # Convert all <-> <~> , to .
        text = re.sub(r"<[-~]>|,", ".", text)
    return text


@dataclass
class TextProcessingOptions:
    alphabet: Literal["eva", "cuva"] = "eva"
    normalize_gaps: bool = True
    delete_comments: bool = True

    # The point of this is to funnel all the to_text, to_lines, to_words signatures to a single place,
    # by having them just pass kwargs to here
    # I really don't like that kwargs mostly destroys type checking and figuring out the signature
    # Considered decorator but it seems pretty much equivalent in effects but more complicated
    # I think this slightly edges out previous setup of having a million duplicated call signatures
    @classmethod
    def from_kwargs(cls, **kwargs):
        try:
            return cls(**kwargs)
        except TypeError as e:
            if "unexpected keyword argument" in str(e):
                param_name = str(e).split("'")[-2]
                raise ValueError(
                    f"'{param_name}' is not a valid text processing option"
                )
            else:
                raise ValueError(f"Invalid text processing options: {str(e)}")


def to_final_text(text: str, opts: TextProcessingOptions) -> str:
    text = strip_inline_metadata(
        text, normalize_gaps=opts.normalize_gaps, delete_comments=opts.delete_comments
    )
    text = to_alphabet(text, opts.alphabet)
    return text


@dataclass
class Manuscript(VMSDataclass):
    loci: list[Locus]
    source_filename: str | None = None

    @classmethod
    @lru_cache(maxsize=1)
    def from_file(cls, text: str, fname: str) -> "Manuscript":
        # Expects text directly from IVTFF file.
        # Split by page and then create Page for each.

        # Delete all comment lines
        text = re.sub(r"#.*?\n", "", text)

        loci: list[Locus] = []
        page_lines: list[str] = []

        # Going in reverse order ( [::-1] ) makes process a bit easier because we don't have to "look forward" for headings,
        # just keep piling up lines and when we do see a heading, ship it all off.
        for line in text.splitlines()[::-1]:
            # Does this line contain a page header?
            header_match = re.search(r"<! (.*?)>", line)
            if header_match:
                # Yep!
                name: str = re.match(r"<(f.*?)>", line).group(1)  # type: ignore - name is guaranteed to exist alongside header for IVTFF
                header: str = header_match.group(1)
                if len(page_lines) and name and header:
                    # Process all lines (still in reverse order)
                    page_loci = loci_list_from_lines(page_lines, header)
                    loci.extend(page_loci)
                    # Get rid of our used up lines
                    page_lines = []
            else:
                # No header in line
                page_lines.append(line)

        if len(page_lines):
            raise ValueError("File ended without final page header. Corrupted file?")

        return cls(
            loci=loci[::-1], source_filename=fname
        )  # Put loci back in normal order

    # to_lines, to_words, and the same names in VMS class are basically just wrappers for this function
    # See note in TextProcessingOptions - not super happy with kwargs
    # The below two methods should be the only methods that create TextProcessingOptions objects!
    # because they are the only ones that have to build up text in different ways by calling to_final_text
    # (it could be reduced to just to_text if Locus had some prop like last_in_page)
    def to_text(self, **kwargs) -> str:
        opts = TextProcessingOptions.from_kwargs(**kwargs)
        text = decompose(self)  # gives us a str
        text = to_final_text(text, opts)
        return text

    def to_pages(self, **kwargs) -> list[str]:
        opts = TextProcessingOptions.from_kwargs(**kwargs)
        # because of fRos, page names can't be sorted alphabetically
        pages: list[list[Locus]] = []
        curr_pagename = ""
        for locus in self.loci:
            if locus.page_name != curr_pagename:
                curr_pagename = locus.page_name
                pages.append([])
            pages[-1].append(locus)
        pagetext: list[str] = [decompose(page) for page in pages]  # type: ignore
        for i, ptext in enumerate(pagetext):
            ptext = to_final_text(ptext, opts)
            pagetext[i] = ptext
        return pagetext

    def to_lines(self, **kwargs) -> list[str]:
        return self.to_text(**kwargs).splitlines()

    def to_words(self, **kwargs) -> list[str]:
        words = []
        for line in self.to_lines(**kwargs):
            words.extend(line.split("."))
        return words


VMSObject = Manuscript | Locus


# We want to be able to easily take any combination and turn it all into text.
def decompose(source: VMSObject | list[VMSObject]) -> str:
    text = ""
    if isinstance(source, list):
        for item in source:
            text += decompose(item)
    else:
        if hasattr(source, "loci"):
            for locus in source.loci:  # type: ignore
                text += decompose(locus)
        elif hasattr(source, "text"):
            text += source.text + "\n"  # type: ignore
        else:
            raise TypeError("source must be Manuscript, Page, or Locus")
    return text


# Helper class to load from transliteration file and create Manuscript objects, returning it or its text/lines/words/filtered etc.
class VMS:
    @classmethod
    def filter(cls, props: Sequence[LocusPropType] | LocusPropType) -> Manuscript:
        if isinstance(props, LocusPropType):
            props = [props]
        filt_props = [
            prop for prop in props if issubclass(prop.__class__, LocusPropType)
        ]

        vms = cls.get()
        loci = []

        for locus in vms.loci:
            if all(fprop in locus.__dict__.values() for fprop in filt_props):
                loci.append(locus)

        if not len(loci):
            print(
                "Warning: No text loci matched the given filter properties, result is empty."
            )
            print(
                f"  (properties: {', '.join(list(f'LocusProp.{p.__class__.__name__ + "." + p.name}' for p in filt_props)) if filt_props else 'None'} )"
            )  # type: ignore

        return Manuscript(loci=loci, source_filename=vms.source_filename)

    @classmethod
    def to_words(cls, **kwargs) -> list[str]:
        return cls.get().to_words(**kwargs)

    @classmethod
    def to_lines(cls, **kwargs) -> list[str]:
        return cls.get().to_lines(**kwargs)

    @classmethod
    def to_pages(cls, **kwargs) -> list[str]:
        return cls.get().to_pages(**kwargs)

    @classmethod
    def to_text(cls, **kwargs) -> str:
        return cls.get().to_text(**kwargs)

    @classmethod
    def get(cls, basic_ver: bool = True) -> Manuscript:
        if not basic_ver:
            print(
                "Warning: Support for extended EVA very untested, please report any issues"
            )
        translit_dir = resources.files("pykeedy.data.transliterations")

        basic = translit_dir / "RF1b-er.txt"
        extended = translit_dir / "RF1b-e.txt"

        path = basic if basic_ver else extended
        with path.open("r", encoding="utf-8") as f:
            raw = f.read()

        vms = Manuscript.from_file(raw, path.name)
        return vms
