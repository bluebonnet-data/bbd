class Geography:
    """Geographies, meaning districts or regions, referencing both census and election data definitions, prioritizing census definitions"""

    TRACT = "tract"
    CD = "congressional district"
    COUNTY = "county"
    STATE = "state"
    ZCTA = "zip code tabulation area"
    BLOCK = "block"
    BLOCKGROUP = "block group"
    # NEW:
    SL = "state legislative district (lower)"
    UL = "state legislative district (upper)"
    PRECINCT = "precinct"


    def __init__(self, year: int, geo_type, id: str, name: str, shape=None):
        self.year = year
        self.geo_type = geo_type
        self.id = id
        self.name = name
        self.shape = shape

    

    def find_intersections(self, other_geography):
        """
        Returns bool if self intersects with other_geography

        If "shape" is not defined for this geographi
        """
        return None