from dataclasses import dataclass
from bbd.models import geography
from bbd.census import arguments

@dataclass
class GeographyUnit():
    label: geography.Geography
    argument: arguments.Arguments
    value: str
