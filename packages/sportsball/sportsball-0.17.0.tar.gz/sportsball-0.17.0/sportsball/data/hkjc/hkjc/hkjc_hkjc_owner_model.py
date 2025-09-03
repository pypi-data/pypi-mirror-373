"""HKJC HKJC owner model."""

import logging
import urllib.parse
from urllib.parse import urlparse

from ...owner_model import VERSION, OwnerModel


def create_hkjc_hkjc_owner_model(
    url: str,
) -> OwnerModel | None:
    """Create an HKJC owner."""
    o = urlparse(url)
    query = urllib.parse.parse_qs(o.query)
    try:
        name = query["HorseOwner"][0]
    except KeyError as exc:
        logging.debug(url)
        logging.debug(str(exc))
        return None
    return OwnerModel(
        identifier=name,
        name=name,
        version=VERSION,
    )
