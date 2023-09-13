from dataclasses import dataclass, field


@dataclass
class CensusTable():
    variable_id: str
    variable_description: str
    attributes: list[tuple[str, str]]

    def fetch_dataframe(self):
        pass