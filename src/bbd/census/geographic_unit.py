from dataclasses import dataclass
from bbd.census.enumerations import analysis_level, geography


@dataclass
class GeographicUnit():
    geography: geography.GEOGRAPHY
    analysis_level: analysis_level.AnalysisLevel
    value: str
