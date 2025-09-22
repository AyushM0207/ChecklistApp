"""Fetch trending topics that can be used for the cartoon short."""
from __future__ import annotations

from typing import List

from pytrends.request import TrendReq


class TrendFetchError(RuntimeError):
    """Raised when the automation cannot fetch trending topics."""


def fetch_trending_topics(region: str, limit: int = 10) -> List[str]:
    """Return a list of trending topics for ``region``.

    Parameters
    ----------
    region:
        The Google Trends region code (for example ``"united_states"`` or
        ``"india"``). The list of supported regions is documented in the
        :mod:`pytrends` project.
    limit:
        Maximum number of topics to return.
    """

    pytrends = TrendReq(hl="en-US", tz=360)

    try:
        trending_df = pytrends.trending_searches(pn=region)
    except Exception as exc:  # pragma: no cover - defensive against API changes
        raise TrendFetchError(f"Failed to fetch trending data: {exc}") from exc

    topics = [str(item) for item in trending_df[0].tolist() if str(item).strip()]
    if not topics:
        raise TrendFetchError("Received an empty list of trending topics.")

    return topics[:limit]
