"""The base class for a data model."""

# pylint: disable=too-few-public-methods
import pandas as pd
from scrapesession.scrapesession import ScrapeSession  # type: ignore
from scrapesession.scrapesession import create_scrape_session


class Model:
    """The base model class."""

    _session: ScrapeSession | None

    def __init__(self, session: ScrapeSession) -> None:
        self._session = session

    @property
    def session(self) -> ScrapeSession:
        """Fetch a session that can never be null."""
        session = self._session
        if session is None:
            session = create_scrape_session(
                "sportsball",
                fast_fail_urls={
                    "https://news.google.com/",
                    "https://historical-forecast-api.open-meteo.com/",
                    "https://api.open-meteo.com/",
                },
            )
            self._session = session
        return session

    def clear_session(self):
        """Clear the session."""
        self._session = None

    def to_frame(self) -> pd.DataFrame:
        """Render the model as a dataframe."""
        raise NotImplementedError("to_frame not implemented by parent class.")
