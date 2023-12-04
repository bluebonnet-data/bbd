from .Geography import Geography

class Candidate:

    def __init__(self, name: str, district: Geography, votes_received: int = None, vote_share_2_way: float = None, filing_id: str = None):
        self.name = name
        self.filing_id = filing_id
        self.district = district
        