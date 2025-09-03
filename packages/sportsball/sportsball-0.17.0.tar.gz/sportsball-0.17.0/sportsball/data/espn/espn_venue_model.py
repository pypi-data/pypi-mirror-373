"""ESPN venue model."""

import datetime
from typing import Any

import requests_cache

from ...cache import MEMORY
from ..google.google_address_model import create_google_address_model
from ..venue_model import VenueModel


@MEMORY.cache(ignore=["session"])
def create_espn_venue_model(
    venue: dict[str, Any],
    session: requests_cache.CachedSession,
    dt: datetime.datetime,
    version: str,
) -> VenueModel:
    """Create a venue model from an ESPN result."""
    name = venue.get("fullName", venue.get("name"))
    identifier = venue.get("id", name)
    venue_address = venue.get("address")
    address = None
    if venue_address is not None:
        city = venue_address.get("city", "")
        state = venue_address.get("state", "")
        zipcode = venue_address.get("zipCode", "")
        address = create_google_address_model(
            " - ".join([x for x in [name, city, state, zipcode] if x]),
            session,
            dt,
        )
    else:
        address = create_google_address_model(
            name,
            session,
            dt,
        )
    grass = venue.get("grass")
    indoor = venue.get("indoor")
    return VenueModel(
        identifier=identifier,
        name=name,
        address=address,  # pyright: ignore
        is_grass=grass,
        is_indoor=indoor,
        is_turf=None,
        is_dirt=None,
        version=version,
    )
