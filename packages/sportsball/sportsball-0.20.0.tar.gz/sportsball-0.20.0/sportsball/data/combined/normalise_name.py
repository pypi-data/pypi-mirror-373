"""Function for normalising names."""

import re
import unicodedata

REGEX = re.compile("[^a-zA-Z]")


def normalise_name(name: str) -> str:
    """Handles Surname, Firstname"""
    if "," in name:
        name = " ".join(reversed([x.strip() for x in name.split(",")]))
    return REGEX.sub("", unicodedata.normalize("NFC", name).lower().strip())
