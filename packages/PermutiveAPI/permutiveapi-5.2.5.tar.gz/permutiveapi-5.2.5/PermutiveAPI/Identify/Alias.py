"""User identification helpers for the Permutive API."""

from dataclasses import dataclass
from typing import Dict, Any


from PermutiveAPI.Utils import JSONSerializable


@dataclass
class Alias(JSONSerializable[Dict[str, Any]]):
    """Dataclass for the Alias entity in the Permutive ecosystem.

    Parameters
    ----------
    id : str
        The ID of the alias.
    tag : str
        The tag of the alias.
    priority : int
        The priority of the alias.
    """

    id: str
    tag: str
    priority: int
