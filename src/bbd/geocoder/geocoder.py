import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

from pathlib import Path
from .utils import is_valid_email

from tqdm import tqdm
from functools import lru_cache

from inspect import signature
import re

import pandas as pd

def get_geocoder(email):
    """Get geocode function for geocoding through Nominatim with supplied
    email address as the user_agent, as per Nominatim's usage policy.

    This geocoder will take at least 1 second per Address queried in
    accordance with Nominatim's terms of service. 
    Note: this process cannot be multi-threaded or run in parallel.

    Arguments
    ---------
    email : str
        A string email Address supplied to Nominatim as user_agent

    Examples
    --------
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
    """Get reverse geocode function for reverse geocoding through Nominatim 
    with supplied email address as the user_agent, as per Nominatim's 
    usage policy.

    This reverse geocoder will take at least 1 second per Address queried
    in accordance with Nominatim's terms of service.
    Note: this process cannot be multi-threaded or run in parallel.

    Arguments
    ---------
    email : str
        A string email Address supplied to Nominatim as user_agent

    Examples
    --------

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


def street_encode(street) -> str:
    """Default street_encoder for GeocodeLocation.

    Gets street address while removing secondary unit designators.
     See: https://pe.usps.com/text/pub28/28apc_003.htm
    Not all secondary unit designators are removed as they may be contained
     in street names e.g. key, hanger, pier

    Arguments
    ---------
    street : str
        a string street component of address

    >>> street_encode("123 Test St")
    "123 Test St"
    >>> street_encode("456 Test Way apt 375")
    "456 Test Way"
    >>> street_encode("420 Test Ave Unit 5")
    "420 Test Ave"
    """
    pattern = r"^.*(?= [Aa]p(?:ar)?t(?:ment)? | [Uu]nit | #| [Ll]ot |"\
              r" [Rr](?:oo)?m | [Bb](?:ui)?ld(?:in)?g | [Uu]pp?e?r| [Ll]o?we?r|"\
              r" [Ss](?:ui)?te | [Ff](?:l )?(?:rnt)?| [Tt]r(?:ai)?le?r | [Dd]ept )"
    try:
        result = re.search(pattern, street) or street
    except TypeError:
        result = ""
    if type(result) is re.Match:
        #want only first result.
        return result[0]
    return result


class GeocodeLocations:
    """ Friendly wrapper to geocode large batches of data with Nominatim
    and saves to file located at path. This will remember your progress
    across session and also allows user to only run a number of batches 
    of size batch_size.

    Please note, this process MAY NOT be multi-threaded or run in parallel.
    Please read Nominatim's Usage Policy here: 
    https://operations.osmfoundation.org/policies/nominatim/

    Attributes
    ----------
    data : pandas dataframe, list of dicts, or list of strings.
        Data where each row or item represents 1 address to be geocoded. 
        NOTE: Inputting falsey value for data allows for providing
            column of components by kwarg as either Series or list of
            str and setting defaults as necessary. (see defaults)
        For dataframe: 
            data should either contain 1 column
            OR 
            columns using follow VAN default column names (not case sensitive):
             "Address" - column of str street component of address
             "City" - column of str city component of address
             "County" - column of str county component of address
             "State" - column of str state component of address
             "Zip5" - column of str 5-digit postal code for address
             "Country" - column of str country component of address
                         (if applicable, default will set country to US)
        For list of dicts:
            Each item should be a dict of the form
             "Address" : str street component of address
             "City" : str city component of address
             "County" : str county component of address
             "State" : str state component of address
             "Zip5" : str 5-digit postal code for address
             "Country" : str country component address
                         (if applicable, default will set country to US)
        For list of strings:
            Each item should str full address to pass as query.

    email : str
        A valid email address as str to pass to Nominatim as user_agent.
        See Nominatim's Usage Policy.

    path : str or pathlib Path object
        A path to where geocoded data will be saved.

    batch_size : (Optional) int
        Number of batches to geocode at a time. Useful for running subset of
        data. Will determin size of batch for run(num_batches) and size of 
        progress bar while running.

    defaults : (Optional) dict
        A dictionary of default values for query. Should be of form:
        {
            "Address" : address_default,
            "City" : city_default,
            "County" : county_default,
            "State" : state_default,
            "Zip5" : postal_default,
            "Country" : country_default
        }
        Will set country to United States by default.

    keep_index : (Optional) bool
        Whether to use the index of data for the geocoded result. If 
        False, will use 
        It is recommended to use the same index for the inputted data
        to easily merge the data.
        True by default.

    Properties
    ----------
    street_encode : func
        A function of 1 argument used to encode the street address. The 
        default is street_encode(address) used to remove secondary 
        descriptors from the street address. This is recommended 
        because many addresses in OpenStreetMaps do not have
        secondary descriptors attached and therefore will not be 
        geocoded.

    geocoder : str
        Enter email as str to change geocoder user_agent.

    email : str
        Alias for geocoder

    Methods
    -------
    run(k_batches = None)
        Run num_batches batches of size batch_size through the geocoder.
        If None will run all batches.

    reset()
        Method to reset progress and overwrite file at path.
        WARNING: This method will overwrite file at path, do not use
        unless you want to restart geocoding or if path is a path to 
        existing file.

    """

    _cache_size = 4000
    def __init__(self, data, email, path, batch_size = 3600,
                 defaults = {"Country":"United States"}, 
                 keep_index = True):
        """Constructor for bbd.geocoder.GeocodeLocations"""

        #Creates geocoder with email passed as user_agent
        self.geocoder = email #self.email is alias for self.geocoder
        self.__real_geocoder = self._geocoder #for testing

        self.defaults = defaults.copy()

        self.data = pd.DataFrame(data)

        if data.empty:
            raise ValueError("Data cannot be empty!")

        if not keep_index:
            self.data = self.data.reset_index(drop=True)

        #Verifying address components.
        if len(self.data.columns) > 1:
            #Components of address that will be passed to Nominatim.
            component_list = ['address', 'street', 'city', 'county', 
                              'state', 'country', 'zip5', 'zip', 
                              'postal', 'postalcode']

            self.included_cols = [col for col in data.columns
                                  if col.lower() in component_list]

            if not self.included_cols:
                raise ValueError("If data a pd.DataFrame with multiple "\
                                 "columns or a list of dictionaries, it "\
                                 "must include labels/keys for at least "\
                                 "some components of an address.")

            #Defaults must be dict of address components.
            if not all([key.lower() in component_list for key in defaults]):
                raise ValueError("All keys in defaults must be components"\
                                 "of an address.")

        self.batch_size = batch_size

        #Check file status then load or create file.
        self.path = Path(path)
        try:
            #Load already geocoded results.
            self.locations = pd.read_csv(self.path)
            
            #check that self.locations is appropriate file.
            if not all([col in self.locations.columns for col 
                       in ["latitude", 'longitude', 'address']]):
                raise ValueError(f"Path {self.path} is an unrelated file!")

            self._load_queue()

        #Has never been run before.
        except FileNotFoundError:
            self.locations = pd.DataFrame(columns = ['latitude', 
                                                     'longitude', 
                                                     'address'])
            self._make_file(path)
            self._fill_queue() 

        #Set default street encoder
        self._street_encode = street_encode
 

    def _make_file(self, path):
        """Make new file at self.path and put in the header."""
        header = ",latitude,longitude,address\n"
        with open(path, "w") as f:
            f.write(header)


    def _fill_queue(self):
        """Fill Queue as copy from data's index."""
        #Set queue
        self._queue = list(self.data.index)

        #Set batch info: Only used for display purposes
        self.tot_batches = len(self._queue)//self.batch_size + 1
        self.curr_batch = 1 #curr_batch not zero indexed.


    def _load_queue(self):
        """Set Queue to only remaining addresses."""
        #Set queue
        self._queue = [i for i in self.data.index if i 
                       not in self.locations.index]

        
        #Set batch info: Only used for display purposes
        tot_run = len(self.data.index) - len(self._queue)

        self.tot_batches = len(self.data.index)//self.batch_size + 1
        self.curr_batch = tot_run//self.batch_size + 1


    #_run_geocoder exists to provide cache to geocoder.
    #turns mutable dict input into immutable kwargs.
    @lru_cache(maxsize = _cache_size)
    def _run_geocoder(self, *args, **kwargs
                       ) -> geopy.location.Location or None:
        """Run the geocoder based on inputs."""
        if args and not kwargs:
            return self.geocoder(*args)

        elif kwargs and not args:
            return self.geocoder(kwargs) #not unpacked to pass dict.

        else:
            _msg = "Either pass full address as arg or components as keywords"
            raise ValueError(_msg)


    def _process_address_string(self, i):
        """Return results when data is list of str or only has 
        single address column.

        Returns (lat, lon, address)
        """
        try:
            col = self.included_cols[0]
        except NameError:
            col = self.data.columns[0]
        address = data.loc[i, col]
        
        result = self._run_geocoder(address)
        try:
            return result.latitude, result.longitude, result.address

        #AttributeError typically occurs if no result from geocoder.
        except AttributeError:
            return None, None, address


    def _process_address_components(self, i):
        """Return geocoded results when data is list of dict
        or dataframe of address components.

        Returns (lat, lon, address)
        """
        def component_formatter(key, value):
            """Helper function to format keys for address passed 
            to Nominatim.

            Returns formatted (key, value) pair
            """
            #With components address is assumed to be street component
            if key.lower() == "address" or key.lower() == "street":
                return "street", self.street_encode(value)

            elif (key.lower() in "zip5" or key.lower() == "postal"):
                return "postalcode", value

            else:
                return key.lower(), value
        
        #Unpack components in self.data
        address = {key: value for key, value in 
                   [component_formatter(col, self.data.loc[i, col]) 
                   for col in self.included_cols]}

        #Set default components in defaults
        for key, value in zip(self.defaults, self.defaults.values()):
            key, value = component_formatter(key, value)
            address[key] = value

        result = self._run_geocoder(**address)
        try:
            return result.latitude, result.longitude, result.address

        #AttributeError typically occurs if no result from geocoder
        except AttributeError:
            #Format Address in proper order.
            formatted_address = ", ".join([str(address[key]) for key in 
                                          ['street', 'city', 
                                          'county', 'state', 
                                          'country', 'postalcode']
                                          if key in address])
            return None, None, formatted_address


    def _run_batch(self, batch_list):
        """Run each item from batch_list through geocoder 
        saving to disk as it goes and updating self.locations
        once complete.

        batch - list of indexes from queue to run through 
                self.geocoder.
        """
        #tqdm for progress bar.
        with open(self.path, "a") as f:
            desc = f"{self.curr_batch}/{self.tot_batches}"
            for i in tqdm(batch_list, desc = desc):
                #For list of str or dataframe of 1 column
                if (len(self.data.columns) == 1 
                        or (len(self.included_cols) == 1 
                            and self.included_cols[0] == 'address')):
                    lat, lon, address = self._process_address_string(i)

                #For DataFrame or list of dicts
                else:
                    lat, lon, address = self._process_address_components(i)

                #Add processed addresses to self.locations
                self.locations.loc[i, ['latitude', 
                                       'longitude', 
                                       'address']] = lat, lon, address

                #Save processed address to path.
                f.write(f"{i}, {lat}, {lon}, {address}\n")


    def run(self, num_batches=None):
        """
        """
        if num_batches is None:
            num_batches = len(self._queue)//self.batch_size + 1

        if num_batches <= 0 or len(self._queue) == 0:
            print("All done!")
            return self.locations

        batch = [] #need to decide how to pull batches from queue
        for i in range(self.batch_size):
            try:
                batch.append(self._queue.pop(0))
            except IndexError:
                pass #reached end of Queue

        print(f"Running batch {self.curr_batch} of {self.tot_batches}: ", 
              flush = True)
        self._run_batch(batch)

        print("Batch complete!")
        self.curr_batch += 1 #Update batch count
        
        return self.run(num_batches-1)


    def reset(self):
        """Method to reset progress and overwrite file at path.
        WARNING: This method will overwrite file at path, do not use
        unless you want to restart geocoding or if path is a path to 
        existing file.
        """
        if self.path.exists():
            warn_msg = f"""WARNING:
            This will overwrite file at {self.path}...
            Type 'DELETE' to continute.
            """
            confirmation = input(warn_msg)

            if confirmation != "DELETE":
                print("File not reset.")
                return #Exit without overwritting file

            else:
                print(f"File at {self.path} was reset.")

        self._make_file(self.path)
        self._fill_queue()


    @property
    def street_encode(self):
        """getter for _street_encode"""
        return self._street_encode


    @street_encode.setter
    def street_encode(self, new):
        """setter for _street_encode. enforces _street_encode 
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


    @property
    def geocoder(self):
        return self._geocoder


    @geocoder.setter
    def geocoder(self, email):
        """Setter for geocoder. Will keep asking for valid email until one
        is entered.
        """
        try:
            self._geocoder = get_geocoder(email)
        except AssertionError:
            #Will keep asking for new email until valid one input.
            print("Error: Must be a valid email...")
            new_email = input("Please enter a valid email: ")
            self.geocoder = new_email #recursion


    #email is alias for setting new geocoder
    email = geocoder


    def _set_test_geocoder(self):
        """Method for testing. Will change _geocoder to function that 
        returns geopy.location.Location for Evan's Hall, Berkeley, CA
        and occasionally returns None. 

        Undo with either:
        self.email = str_valid_email 
        or
        self.geocoder = str_valid_email
        """
        #Go Bears!
        evans_hall = self.__real_geocoder("Evan's Hall, Berkeley, CA")
        def test_generator():
            n = 0
            while True:
                n += 1
                if n%10 == 0:
                    yield None
                else:
                    yield evans_hall
        gen = test_generator()
        self._geocoder = lambda *args, **kwargs: next(gen)
