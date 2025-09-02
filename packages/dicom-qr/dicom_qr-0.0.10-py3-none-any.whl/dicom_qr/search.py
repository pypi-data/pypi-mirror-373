"""
Search Terms
"""
import datetime

from dataclasses import dataclass
from collections.abc import Sequence


@dataclass(eq=True, frozen=True)
class SearchTerms:  # pylint: disable=too-many-instance-attributes
    """
    dataclass containing all search fields.
    """
    def __post_init__(self) -> None:
        if self.patid is not None:
            assert isinstance(self.patid, str)
            # assert len(self.patid) == 7

    date_range: datetime.date | tuple[datetime.date, datetime.date] | None = None
    timestamp: str | None = None
    study_desc: str | None = None
    study_uid: str | None = None
    patid: str | None = None
    pat_name: str | None = None
    accession_number: str | None = None
    modalities: Sequence[str] | None = None
