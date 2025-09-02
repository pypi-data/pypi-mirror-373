"""Segment management for the Permutive API."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Type, Union, Any
from dataclasses import dataclass
from datetime import datetime, timezone

from . import _API_ENDPOINT
from PermutiveAPI._Utils import http
from PermutiveAPI._Utils.json import JSONSerializable, load_json_list

_API_PAYLOAD = ["name", "code", "description", "cpm", "categories"]


@dataclass
class Segment(JSONSerializable[Dict[str, Any]]):
    """Represent a segment in the Permutive API.

    Parameters
    ----------
    code : str
        The code of the segment.
    name : str
        The name of the segment.
    import_id : str
        The import ID of the segment.
    id : Optional[str], optional
        The ID of the segment (default: None).
    description : Optional[str], optional
        The description of the segment (default: None).
    cpm : Optional[float], optional
        The cost per mille of the segment (default: 0.0).
    categories : Optional[List[str]], optional
        Categories associated with the segment (default: None).
    created_at : Optional[datetime], optional
        When the segment was created (default: None).
    updated_at : Optional[datetime], optional
        When the segment was last updated (default: None).

    Methods
    -------
    create(api_key)
        Create a new segment.
    update(api_key)
        Update the segment.
    delete(api_key)
        Delete a segment.
    get_by_code(import_id, segment_code, api_key)
        Retrieve a segment by its code.
    get_by_id(import_id, segment_id, api_key)
        Retrieve a segment by its ID.
    list(import_id, api_key)
        Retrieve a list of segments for a given import ID.
    """

    code: str
    _request_helper = http

    name: str
    import_id: str
    id: Optional[str] = None
    description: Optional[str] = None
    cpm: Optional[float] = 0.0
    categories: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Normalize timestamps for deterministic serialization.

        If one of ``created_at`` or ``updated_at`` is missing, it is copied
        from the other. If both are missing, they are initialized to the
        same current UTC timestamp. This avoids microsecond-level drift
        between the two fields.
        """
        if self.created_at is None and self.updated_at is None:
            now = datetime.now(tz=timezone.utc)
            self.created_at = now
            self.updated_at = now
        elif self.created_at is None:
            self.created_at = self.updated_at
        elif self.updated_at is None:
            self.updated_at = self.created_at

    def create(self, api_key: str) -> None:
        """Create a new segment using the provided API key.

        Parameters
        ----------
        api_key : str
            The API key used for authentication.

        Raises
        ------
        ValueError
            If the segment creation fails.
        """
        logging.debug(f"SegmentAPI::create_segment::{self.import_id}::{self.name}")
        url = f"{_API_ENDPOINT}/{self.import_id}/segments"
        response = self._request_helper.post(
            api_key=api_key,
            url=url,
            data=http.to_payload(dataclass_obj=self, api_payload=_API_PAYLOAD),
        )
        if not response:
            raise ValueError("Unable to create_segment")

        new_segment = Segment.from_json(response.json())
        if isinstance(new_segment, Segment):
            self.__dict__.update(new_segment.__dict__)

    def update(self, api_key: str) -> None:
        """Update the segment using the provided API key.

        Parameters
        ----------
        api_key : str
            The API key used for authentication.

        Raises
        ------
        ValueError
            If the segment update fails.
        """
        logging.debug(f"SegmentAPI::update_segment::{self.import_id}::{self.name}")
        url = f"{_API_ENDPOINT}/{self.import_id}/segments/{self.id}"
        response = self._request_helper.patch(
            api_key=api_key,
            url=url,
            data=http.to_payload(dataclass_obj=self, api_payload=_API_PAYLOAD),
        )
        if not response:
            raise ValueError("Unable to update_segment")

        updated_segment = Segment.from_json(response.json())
        if isinstance(updated_segment, Segment):
            self.__dict__.update(updated_segment.__dict__)

    def delete(self, api_key: str) -> None:
        """Delete a segment using the provided API key.

        Parameters
        ----------
        api_key : str
            The API key used for authentication.

        Raises
        ------
        ValueError
            If the segment deletion fails.
        """
        logging.debug(f"SegmentAPI::delete_segment::{self.import_id}::{self.id}")
        url = f"{_API_ENDPOINT}/{self.import_id}/segments/{self.id}"
        response = self._request_helper.delete(api_key=api_key, url=url)
        if response is None:
            raise ValueError("Response is None")

    @staticmethod
    def get_by_code(import_id: str, segment_code: str, api_key: str) -> "Segment":
        """Retrieve a segment by its code.

        Parameters
        ----------
        import_id : str
            The ID of the import.
        segment_code : str
            The code of the segment to retrieve.
        api_key : str
            The API key for authentication.

        Returns
        -------
        Segment
            The segment object retrieved by the given code.

        Raises
        ------
        ValueError
            If the segment cannot be retrieved.
        """
        logging.debug(f"SegmentAPI::get_segment_by_code::{import_id}::{segment_code}")
        url = f"{_API_ENDPOINT}/{import_id}/segments/code/{segment_code}"
        response = Segment._request_helper.get(url=url, api_key=api_key)
        if not response:
            raise ValueError("Unable to get_segment")
        return Segment.from_json(response.json())

    @staticmethod
    def get_by_id(import_id: str, segment_id: str, api_key: str) -> "Segment":
        """Retrieve a segment by its ID.

        Parameters
        ----------
        import_id : str
            The ID of the import.
        segment_id : str
            The ID of the segment to retrieve.
        api_key : str
            The API key for authentication.

        Returns
        -------
        Segment
            The segment object retrieved by the given ID.

        Raises
        ------
        ValueError
            If the segment cannot be retrieved.
        """
        logging.debug(f"SegmentAPI::get_segment_by_id::{import_id}::{segment_id}")
        url = f"{_API_ENDPOINT}/{import_id}/segments/{segment_id}"
        response = Segment._request_helper.get(url=url, api_key=api_key)
        if not response:
            raise ValueError("Unable to get_by_id")
        return Segment.from_json(response.json())

    @staticmethod
    def list(import_id: str, api_key: str) -> "SegmentList":
        """Retrieve a list of segments for a given import ID.

        Parameters
        ----------
        import_id : str
            The ID of the import to retrieve segments for.
        api_key : str
            The API key for authentication.

        Returns
        -------
        SegmentList
            A list of Segment objects retrieved from the API.

        Raises
        ------
        ValueError
            If the segment list cannot be fetched.
        PermutiveAPIError
            If an error occurs while making the API request.
        """
        logging.debug(f"SegmentAPI::list")

        base_url = f"{_API_ENDPOINT}/{import_id}/segments"
        all_segments = []
        next_token = None

        while True:
            params = {}
            if next_token:
                params["pagination_token"] = next_token

            response = Segment._request_helper.get(api_key, base_url, params=params)
            if response is None:
                raise ValueError("Response is None")
            data = response.json()

            # Extract elements and add them to the list
            all_segments.extend(data.get("elements", []))

            # Check for next_token in the pagination metadata
            next_token = data.get("pagination", {}).get("next_token")

            if not next_token:
                break  # Stop when there are no more pages

        return SegmentList.from_json(all_segments)


class SegmentList(List[Segment], JSONSerializable[List[Any]]):
    """Custom list that holds Segment objects and provides caching and serialization.

    Methods
    -------
    from_json(data)
        Deserialize a list of segments from various JSON representations.
    id_dictionary()
        Return a dictionary of segments indexed by their IDs.
    name_dictionary()
        Return a dictionary of segments indexed by their names.
    code_dictionary()
        Return a dictionary of segments indexed by their codes.
    """

    @classmethod
    def from_json(
        cls: Type["SegmentList"],
        data: Union[dict, List[dict], str, Path],
    ) -> "SegmentList":
        """Deserialize a list of segments from various JSON representations."""
        data_list = load_json_list(data, cls.__name__, "Segment")
        return cls([Segment.from_json(item) for item in data_list])

    def __init__(self, items_list: Optional[List[Segment]] = None):
        """Initialize the SegmentList with an optional list of Segment objects.

        Parameters
        ----------
        items_list : Optional[List[Segment]], optional
            Segment objects to initialize with (default: None).
        """
        super().__init__(items_list if items_list is not None else [])
        self._id_dictionary_cache: Dict[str, Segment] = {}
        self._name_dictionary_cache: Dict[str, Segment] = {}
        self._code_dictionary_cache: Dict[str, Segment] = {}
        self._refresh_cache()

    def _refresh_cache(self) -> None:
        """Rebuild all caches based on the current state of the list."""
        self._id_dictionary_cache = {
            segment.id: segment for segment in self if segment.id
        }
        self._name_dictionary_cache = {
            segment.name: segment for segment in self if segment.name
        }
        self._code_dictionary_cache = {
            segment.code: segment for segment in self if segment.code
        }

    @property
    def id_dictionary(self) -> Dict[str, Segment]:
        """Return a dictionary of segments indexed by their IDs.

        Returns
        -------
        Dict[str, Segment]
            A dictionary mapping segment IDs to Segment objects.
        """
        if not self._id_dictionary_cache:
            self._refresh_cache()
        return self._id_dictionary_cache

    @property
    def name_dictionary(self) -> Dict[str, Segment]:
        """Return a dictionary of segments indexed by their names.

        Returns
        -------
        Dict[str, Segment]
            A dictionary where the keys are segment names and the values are Segment objects.
        """
        if not self._name_dictionary_cache:
            self._refresh_cache()
        return self._name_dictionary_cache

    @property
    def code_dictionary(self) -> Dict[str, Segment]:
        """Return a dictionary of segments indexed by their codes.

        Returns
        -------
        Dict[str, Segment]
            A dictionary where the keys are segment codes and the values are Segment objects.
        """
        if not self._code_dictionary_cache:
            self._refresh_cache()
        return self._code_dictionary_cache
