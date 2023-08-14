from typing import Optional
class OpenElections():
    def __init__(self, states:list[enum.STATE]):
        self.states = states
        self.repository_urls = []
        for state in self.states:
            repository_url = f"openelections-data-{state.value}"
            self.repository_urls.append(repository_url)


        def get_data(self, variables: Optional[list[str]] = None) -> ElectionsResult:
            pass
