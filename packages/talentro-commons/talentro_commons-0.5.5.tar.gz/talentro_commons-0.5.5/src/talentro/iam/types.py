from dataclasses import dataclass
from typing import List

@dataclass
class Organization:
    id: str
    name: str
    displayName: str
    attributes: dict
    roles: List[str]
    url: str
    role: str
