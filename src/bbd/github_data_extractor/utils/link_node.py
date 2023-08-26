# A class to encapsulate and label primary links (directories and files in a repository) once obtained
from __future__ import annotations
from typing import Optional
from bbd.github_data_extractor.utils.link_type import LinkType
from dataclasses import dataclass

@dataclass
class LinkNode():
    name: str
    url: str
    type_: LinkType
    depth: int
    parent: Optional[LinkNode] = None
    error: Optional[error] = None


    def __repr__(self):
        return f"LinkNode(name: {self.name}, type_: {self.type_}, depth: {self.depth})"
