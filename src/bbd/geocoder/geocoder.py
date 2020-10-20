import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

from pathlib import Path
from utils import is_valid_email

from tqdm import tqdm
from functools import lru_cache

from inspect import signature
import re

def get_geocoder(email):
    """
    Get geocode function for geocoding through Nominatim with supplied
    email address as the user_agent, as per Nominatim's usage policy.

    This geocoder will take at least 1 second per Address queried in
    accordance with Nominatim's terms of service. 
    Note: this process cannot be multi-threaded or run in parallel.

    email-(Str) A string email Address supplied to Nominatim as user_agent


    >>> email = "valid.email@address.com"
    >>> geocode = get_geocoder(email)
    >>> geocode("1315 10th St, Sacramento, CA 95814")
    Location(California State Capitol, 1315, 10th Street, Land Park, Sacramento,
     Sacramento County, California, 95814, United States of America, (38.57656885,
     -121.4934010890531, 0.0))

    >>> email = "not_an_email"
    >>> geocode = get_geocoder(email)
    AssertionError: Must enter a valid email
    """
    #Must enter a valid email
    assert is_valid_email(email), "Must enter a valid email"
    geolocator=Nominatim(user_agent=email)
    geocoder=RateLimiter(geolocator.geocode, min_delay_seconds=1)
    return geocoder


def get_reverse_geocoder(email):
    """
    Get reverse geocode function for reverse geocoding through Nominatim 
    with supplied email address as the user_agent, as per Nominatim's 
    usage policy.

    This reverse geocoder will take at least 1 second per Address queried
    in accordance with Nominatim's terms of service.
    Note: this process cannot be multi-threaded or run in parallel.

    email-(Str) A string email Address supplied to Nominatim as user_agent


    >>> email = "valid.email@Address.com"
    >>> reverse_coder = get_reverse_geocoder(email)
    >>> reverse_coder("37.873621099999994, -122.25768131042068")
    Location(Evans Hall, Bechtel Drive, Northside, Berkeley, Alameda County,
     California, 94720, United States of America, (37.873621099999994,
     -122.25768131042068, 0.0))

    >>> email = "not_an_email"
    >>> reverse_coder = get_reverse_geocoder(email)
    AssertionError: Must enter a valid email
    """
    #Must enter a valid email
    assert is_valid_email(email), "Must enter a valid email"
    geolocator = Nominatim(user_agent=email)
    reverse_geocoder = RateLimiter(geolocator.reverse, min_delay_seconds=1)
    return reverse_geocoder


def street_encode(address) -> str:
    """
    Default street_encoder for GeocodeLocation.
    Gets street address while removing secondary unit designators.
     See: https://pe.usps.com/text/pub28/28apc_003.htm
    Not all secondary unit designators are removed as they may be contained
     in street names e.g. key, hanger, pier

    >>> street_encode("123 Test St")
    "123 Test St"
    >>> street_encode("456 Test Way apt 375")
    "456 Test Way"
    >>> street_encode("420 Test Ave Unit 5")
    "420 Test Ave"
    """
    pattern = r"^.*(?= [Aa]p(?:ar)?t(?:ment)? | [Uu]nit | #| [Ll]ot |"\
              r" [Rr](?:oo)?m | [Bb](?:ui)?ld(?:in)?g | [Uu]ppr| [Ll]o?wr|"\
              r" [Ss](?:ui)?te | [Ff]l?(?:rnt)? | [Tt]r(?:ai)?le?r | [Dd]ept )"
    try:
        result = re.search(pattern, address) or address
    except TypeError:
        result = ""
    if type(result) is re.Match:
        #want only first result.
        return result[0]
    return result


class GeocodeLocation:
    """
    """
    _cache_size = 4000
    def __init__(self, data, email, path, min_to_checkpoint = 60,
                 defaults = []):
        """
        """
        self._street_encode = street_encode
        pass

    @lru_cache(maxsize = _cache_size)
    def run_geocoder(self, street, city, county, country,
                    postal) -> geopy.location.Location or None:
        """
        Run the geocoder after formatting the inputs for 
        Nominatim properly.
        """
        address_dict = {
            "street": self._street_encode(street),
            "city":city,
            "county":county,
            "state":state,
            "country":country,
            "postalcode":postal
        }
        return self.geocoder(address_dict) 

    @property
    def state(self):
        """
        Geocoded results that have been commited to disk.
        """
        return self._state

    @state.setter
    def _set_state(self, new):
        """
        """
        pass

    @state.deleter
    def _del_state(self):
        """
        """
        pass

    @property
    def street_encode(self):
        """
        getter for _street_encode
        """
        return self._street_encode

    @street_encode.setter
    def set_street_encode(self, new):
        """
        setter for _street_encode. enforces _street_encode 
        must be a callable with 1 arg.
        """
        try:
            sig = signature(new)
        except TypeError:
            print("Encoder not updated: Encoder must be callable")
        else:
            if len(sig.parameters) == 1:
                self._street_encode = new
            else:
                print("Encoder not updated: Encoder must be function of 1"\
                      " argmuent taking str address to str encoded address")
    

    def run(self, num_batches=None):
        """
        """
        pass

