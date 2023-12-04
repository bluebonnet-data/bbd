import pandas as pd
from ..models import GEOGRAPHY, Election
from typing import Optional, Iterable

def get_elections(election_office: Optional[Election] = None,
                  aggregate_into: Optional[GEOGRAPHY] = None,
                  years: Iterable[int] = (),
                  districts: Iterable[GEOGRAPHY] = ()):
    """
    Returns the election results for a specific election office and election year and returns the Democratic & Republican vote share

    TODOs:
    - collect data
    - connect to data here (caching?)
    - run aggregation
    - Could we allow passing in an arbitrary geoshape to aggregate into?
    - Can we get turnout?
    """

    # dict summarizing dataCoverage
    dataCoverage = {
            "TX": {
                "years": [],
                "election_office": [Election.SL, Election.SU, Election.PRES],
                "geo_levels": [GEOGRAPHY.PRECINCT, GEOGRAPHY.SL, GEOGRAPHY.UL, GEOGRAPHY.COUNTY, GEOGRAPHY.STATE],
                # state, all 33 state districts, all 150 house districts
            }
        }
    

    #example return structure
    return pd.DataFrame([["State House District 21", "TX_HD21", 47.0, 46.5]], 
                columns=["Election Office", "District", "Democratic Vote Share", "Republican Vote Share"])
