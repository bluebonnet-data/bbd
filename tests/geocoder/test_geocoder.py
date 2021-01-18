"""
TESTS FOR bbd.geocoder
"""

from bbd import geocoder as gc
import pytest

import geopy
import timeit
from math import isclose

import pandas as pd
import json
from pathlib import Path

# --------------------------------------
#  ##########   UNIT TESTS   ##########
# --------------------------------------

#A valid email to use accross tests
valid_email = "test@bluebonnetdata.org"

# ###### Test get_geocoder ######
class TestGet_geocoder:
    """Tests for get_geocoder in bbd.geocoder
    """

    def test_reject_invalid_email(self):
        """Test get_geocoder only accepts valid email
        """
        invalid_email = "not an email"
        with pytest.raises(AssertionError):
            gc.get_geocoder(invalid_email)


    def test_geocoder(self):
        """
        Tests that the geocoder returned by get_geocoder
        accurately geocodes an address.
        """
        # setup
        email = valid_email
        geocoder = gc.get_geocoder(email)

        address = "Evans Hall, Berkeley, CA"
        location = geocoder(address)

        error1 = ("Geocoder returned None. Either email not accepted "
                  "or address not found by OpenStreetMap")
        error2 = "Geocoder did not return geopy.location.Location"
        error3 = "Geocder matched with wrong address."
        assert location is not None, error1
        assert isinstance(location, geopy.location.Location), error2
        assert (("Evans Hall".lower() in location.address.lower())
                & isclose(location.latitude, 37.873621099999994) 
                & isclose(location.longitude, -122.25768131042068)), error3


    def test_miniumum_runtime(self):
        """Tests that the geocoder runs at most 1 address per second
        in accordance with Nominatim terms of service.

        Because this test needs to verify the RateLimiter is working 
        consistently, it runs unusually long... sorry.
        """
        email = valid_email
        geocoder = gc.get_geocoder(email)

        error_msg = ("Geocoder running more than once per second violating "
                     "Nominatim terms of service.")

        for n in range(3):
            t0 = timeit.default_timer()
            for i in range(n):
                geocoder("")
            t1 = timeit.default_timer()
            t_diff = t1-t0
            assert t_diff >= n-1, error
        

# ###### Test get_reverse_geocoder ######
class TestGet_reverse_geocoder:
    """Tests for get_reverse_geocoder in bbd.geocoder"""

    def test_reject_invalid_email(self):
        """Test get_reverse_geocoder only accepts valid email"""
        invalid_email = "not an email"
        with pytest.raises(AssertionError):
            gc.get_reverse_geocoder(invalid_email)


    def test_reverse_geocoder(self):
        """Test that the reverse geocoder returned by get_reverse_geocoder
        accurately reverse geocodes an address.
        """
        email = valid_email
        reverse_geocoder = gc.get_reverse_geocoder(email)
        
        point = (37.873621099999994, -122.25768131042068) #Evans Hall, Berkeley Ca
        location = reverse_geocoder(point)

        error1 = ("Geocoder returned None. Either email not accepted "
                  "or address not found by OpenStreetMap")
        error2 = "Geocoder did not return geopy.location.Location"
        error3 = "Geocder matched with wrong address."

        assert location is not None, error1
        assert isinstance(location, geopy.location.Location), error2
        assert (("Evans Hall".lower() in location.address.lower())
                & ("Berkeley".lower() in location.address.lower())
                & isclose(location.latitude, 37.873621099999994) 
                & isclose(location.longitude, -122.25768131042068)), error3


    def test_miniumum_runtime(self):
        """Tests that the geocoder runs at most 1 address per second in 
        accordance with Nominatim terms of service.

        Because this test needs to verify the RateLimiter is working 
        consistently, it runs unusually long... sorry.
        """
        email = valid_email
        reverse_geocoder = gc.get_reverse_geocoder(email)

        error_msg = ("Geocoder running more than once per second violating "
                            "Nominatim terms of service.")

        point = (37.873621099999994, -122.25768131042068) #Evans Hall, Berkeley Ca
        for n in range(3):
            t0 = timeit.default_timer()
            for i in range(n):
                reverse_geocoder(point)
            t1 = timeit.default_timer()
            t_diff = t1-t0
            assert t_diff >= n-1, error


# ###### Test encode_street_address ######
class TestEncode_street_address:
    """Tests for encode_street_address in bbd.geocoder
    """
    def test_unedited_inputs(self):
        """
        Tests that encode_street_address will return its input when no regex
        match is found.
        """
        tests = ["101 Test Ave", ""]

        error = ("encode_street_address not returning input when there"
                 " are no regex matches.")
        for test in tests:
            assert gc.encode_street_address(test) is test, error


    def test_None_input(self):
        """Tests that encode_street_address returns an empty string when input 
        is None.
        """
        test = None

        error = "encode_street_address not converting None into empty string."
        assert gc.encode_street_address(test) == "", error


    def test_edited_inputs(self):
        """Tests that secondary descriptors are being properly trimmed.
        """
        errors = []
        tests = [
            "101 test ave Apt 1",
            "101 test ave apartment 2",
            "101 test ave Unit 3",
            "101 test ave unit 4",
            "101 test ave #5",
            "101 test ave # 6",
            "101 test ave Lot 7",
            "101 test ave lot 8",
            "101 test ave Room 9",
            "101 test ave rm 10",
            "101 test ave bldg 11",
            "101 test ave Building 12",
            "101 test ave Upper",
            "101 test ave uppr",
            "101 test ave upr",
            "101 test ave Lower",
            "101 test ave lwer",
            "101 test ave lwr",
            "101 test ave Suite 13",
            "101 test ave ste 14",
            "101 test ave Fl 15",
            "101 test ave frnt",
            "101 test ave Trailer 16",
            "101 test ave trlr 17",
            "101 test ave Dept 18",
            "101 test ave dept 19",
            "101 test ave     rm 10",
            "101 test ave"
        ]
        for test in tests:
            if not gc.encode_street_address(test) == "101 test ave":
                errors.append(test)

        error_msg = f"""{len(errors)} failed... 
        street_encode failed to trim secondary descriptors from:"""
        assert not errors, error_msg


def add_set_dummy_geocoder_method():
    gc.LocationsGeocoder.__real_geocoder = gc.get_geocoder(valid_email)

    def _set_dummy_geocoder(self):
        """Method for testing. Will change _geocoder to function that 
        returns geopy.location.Location for Evan's Hall, Berkeley, CA
        and occasionally returns None. 

        Undo with either:
        self.email = str_valid_email 
        or
        self.geocoder = str_valid_email
        """
        # Go Bears!
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

    gc.LocationsGeocoder._set_dummy_geocoder = _set_dummy_geocoder



# ###### Test GeoLocations Methods ######
class TestLocationsGeocoder:
    """Tests for methods in bbd.geocoder.LocationsGeocoder """

    # Setting up cross-test enviornment
    data_df_path = Path(__file__).parent / "test_data/data.json"
    data_df_path = data_df_path.resolve()

    assert data_df_path.exists()

    data_list_path = Path(__file__).parent / "test_data/data.txt"
    data_list_path = data_list_path.resolve()
    
    assert data_list_path.exists()

    # Making address_df for testing pd.DataFrame implementation
    # address_df has Address, City, State, Zip5 columns
    address_df = pd.read_json(data_df_path)

    # Making address_list for testing list of str implementation 
    with open(data_list_path,"r") as f:
        address_list = f.read().splitlines()

    # Making address_dict for testing list of dict implementation
    with open(data_df_path, "r") as f:
        address_dict = json.load(f)


    # Method for setting dummy _geocoder
    add_set_dummy_geocoder_method()

    def test_LocationsGeocoder_make_file_header(self, tmp_path):
        """Tests the ._make_file() and ._make_header() methods
        for LocationsGeocoder
        """
        p = tmp_path/"test.csv"

        gl = gc.LocationsGeocoder(self.address_df, valid_email, p)

        test = pd.read_csv(p, sep = "\t")

        error_msg = "Saved File has improper header."
        assert "latitude" in test.columns, error_msg
        assert "longitude" in test.columns, error_msg
        assert "address" in test.columns, error_msg
        assert len(test.columns) <= 4, error_msg


    def test_LocationsGeocoder_run_one_batch(self, tmp_path):
        """Tests the .run() and associated methods for
        LocationsGeocoder.
        """
        p = tmp_path/"test.csv"

        gl = gc.LocationsGeocoder(self.address_df, valid_email, p)
        gl._set_dummy_geocoder()

        gl.run()

        test = pd.read_csv(p, sep = "\t")

        assert not test.empty, "No results saved to disk."
        assert not gl.locations.empty, "No results stored in object."

        assert len(test) == 234, "Not all lines were saved to disk"
        assert len(gl.locations) == 234, "Not all lines were saved in object"

        assert len(test.columns) <= 4, "Saved too many columns in tsv format"


    def test_LocationsGeocoder_run_mult_batches(self, tmp_path):
        """Tests the .run() and associated methods for LocationsGeocoder when
        multiple batches are needed.
        """
        p = tmp_path/"test.csv"

        gl = gc.LocationsGeocoder(self.address_df, valid_email, p,
                                 batch_size = 100)
        gl._set_dummy_geocoder()

        gl.run()

        test = pd.read_csv(p, sep = "\t")

        assert gl.tot_batches == 3, "Batches are not constructed properly."

        assert not test.empty, "No results saved to disk."
        assert not gl.locations.empty, "No results stored in object."

        assert len(test) == 234, "Not all lines were saved to disk."
        assert len(gl.locations) == 234, "Not all lines were saved in object."


    def test_LocationsGeocoder_run_less_than_all_batches(self, tmp_path):
        """Tests the .run() and associated methods for LocationsGeocoder when
        running less than all batches. 
        """
        p = tmp_path/"test.csv"

        gl = gc.LocationsGeocoder(self.address_df, valid_email, p,
                                 batch_size = 100)
        gl._set_dummy_geocoder()

        gl.run(num_batches = 1)

        test = pd.read_csv(p)

        assert gl.tot_batches == 3, "Batches are not constructed properly."
        assert gl.curr_batch < 3, "Run running too many batches."

        assert not test.empty, "No results saved to disk."
        assert not gl.locations.empty, "No results stored in object."

        assert len(test) < 234, "Not all lines were saved to disk."
        assert len(gl.locations) < 234, "Not all lines were saved in object."


    def test_LocationsGeocoder_process_address_string(self, tmp_path):
        """Tests the .run() and associated methods for LocationsGeocoder when
        running on a list of address strings.
        """
        p = tmp_path/"test.csv"

        gl = gc.LocationsGeocoder(self.address_list, valid_email, p,
                                 batch_size = 100)
        gl._set_dummy_geocoder()

        gl.run()

        test = pd.read_csv(p, sep = "\t")

        assert gl.tot_batches == 3, "Batches are not constructed properly."

        assert not test.empty, "No results saved to disk."
        assert not gl.locations.empty, "No results stored in object."

        assert len(test) == 234, "Not all lines were saved to disk."
        assert len(gl.locations) == 234, "Not all lines were saved in object."


    def test_LocationsGeocoder_address_dict(self, tmp_path):
        """Tests the .run() and associated methods when constructing df from
        list of dicts.
        """
        p = tmp_path/"test.csv"

        gl = gc.LocationsGeocoder(self.address_dict, valid_email, p,
                                 batch_size = 100)
        gl._set_dummy_geocoder()

        gl.run()

        test = pd.read_csv(p, sep = "\t")

        assert gl.tot_batches == 3, "Batches are not constructed properly."

        assert not test.empty, "No results saved to disk."
        assert not gl.locations.empty, "No results stored in object."

        assert len(test) == 234, "Not all lines were saved to disk."
        assert len(gl.locations) == 234, "Not all lines were saved in object."


    def test_LocationsGeocoder_test_real_geocoder(self, tmp_path):
        """Tests the .run() and associated methods with a real geocoder
        """
        p = tmp_path/"test.csv"

        gl = gc.LocationsGeocoder(self.address_df, valid_email, p,
                                 batch_size = 1)
        gl.run(num_batches=3)

        assert all(gl.locations.all())


    def test_LocationsGeocoder_reset(self, tmp_path):
        """
        """
        #Mocks the input asking for DELETE
        gc.input = lambda *args : "DELETE"

        p = tmp_path/"test.csv"

        gl = gc.LocationsGeocoder(self.address_df, valid_email, p)
        gl._set_dummy_geocoder()

        gl.run()

        gl.reset()

        test = pd.read_csv(p, sep = "\t")

        assert test.empty, "File was not deleted"
        assert gl.curr_batch == 1, "Batches were not reset"
        assert len(gl._queue) == 234, "Queue was not reset"


    def teardown_method(self):
        gc.input = input

