"""The enumeration of the different supported sexes."""

from enum import StrEnum

import gender_guesser.detector as gender  # type: ignore


class Sex(StrEnum):
    """An enumeration over the different sexes."""

    MALE = "male"
    FEMALE = "female"
    GELDING = "gelding"
    STALLION = "stallion"
    FILLY = "filly"
    MARE = "mare"
    COLT = "colt"
    RIG = "rig"


GENDER_DETECTOR = gender.Detector()
MALE_GENDERS = {"male", "mostly_male"}
FEMALE_GENDERS = {"female", "mostly_female"}
UNCERTAIN_GENDERS = {"andy", "unknown"}

_SEX = {str(x): x for x in Sex}


def sex_from_str(sex_str: str) -> Sex:
    """Find a sex from a string."""
    sex_str = sex_str.lower().strip()
    sex = _SEX.get(sex_str)
    if sex is None:
        if sex_str == "horse":
            return Sex.STALLION
        raise ValueError(f'Unrecognised sex: "{sex_str}"')
    return sex
