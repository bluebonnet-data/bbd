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
		#setup
		email = valid_email
		geocoder = gc.get_geocoder(email)

		address = "Evans Hall, Berkeley, CA"
		location = geocoder(address)

		error1 = "Geocoder returned None. Either email not accepted "\
				 "or address not found by OpenStreetMap"
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
		"""
		email = valid_email
		geocoder = gc.get_geocoder(email)

		error_msg = "Geocoder running more than once per second violating "\
					"Nominatim terms of service."

		for n in range(1,4):
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

		error1 = "Geocoder returned None. Either email not accepted "\
				 "or address not found by OpenStreetMap"
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
		"""
		email = valid_email
		reverse_geocoder = gc.get_reverse_geocoder(email)

		error_msg = "Geocoder running more than once per second violating "\
					"Nominatim terms of service."

		point = (37.873621099999994, -122.25768131042068) #Evans Hall, Berkeley Ca
		for n in range(1, 4):
			t0 = timeit.default_timer()
			for i in range(n):
				reverse_geocoder(point)
			t1 = timeit.default_timer()
			t_diff = t1-t0
			assert t_diff >= n-1, error


# ###### Test street_encode ######
class TestStreet_encode:
	"""Tests for street_encode in bbd.geocoder
	"""
	def test_unedited_inputs(self):
		"""
		Tests that street_encode will return its input when no regex
		match is found.
		"""
		tests = ["101 Test Ave", ""]

		error = "street_encode not returning input when there are"\
				" no regex matches."
		for test in tests:
			assert gc.street_encode(test) is test, error


	def test_None_input(self):
		"""Tests that street_encode returns an empty string when input 
		is None.
		"""
		test = None

		error = "street_encode not converting None into empty string."
		assert gc.street_encode(test) == "", error


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
			"101 test ave dept 19"
		]
		for test in tests:
			if not gc.street_encode(test) == "101 test ave":
				errors.append(test)

		error_msg = f"""{len(errors)} failed... 
		street_encode failed to trim secondary descriptors from:"""
		assert not errors, error_msg


# ###### Test GeoLocations Methods ######
class TestGeocodeLocations:
	"""Tests for methods in bbd.geocoder.GeocodeLocations """

	#Setting up cross-test enviornment
	#data_df_path = Path("test_data/data.json").resolve()
	data_df_path = Path(__file__).parent / "test_data/data.json"
	data_df_path = data_df_path.resolve()
	assert data_df_path.exists()
	#data_list_path = Path("test_data/data.txt").resolve()
	data_list_path = Path(__file__).parent / "test_data/data.txt"
	data_list_path = data_list_path.resolve()
	assert data_list_path.exists()

	#Making address_df for testing pd.DataFrame implementation
	#address_df has Address, City, State, Zip5 columns
	address_df = pd.read_json(data_df_path)

	#Making address_list for testing list of str implementation 
	with open(data_list_path,"r") as f:
		address_list = f.read().splitlines()

	#Making address_dict for testing list of dict implementation
	with open(data_df_path, "r") as f:
		address_dict = json.load(f)


	def test_GeocodeLocatios_make_file_header(self, tmp_path):
		"""Tests the ._make_file() and ._make_header() methods
		for GeocodeLocations
		"""
		p = tmp_path/"test.csv"

		gl = gc.GeocodeLocations(self.address_df, valid_email, p)

		test_df = pd.read_csv(p)

		error_msg = "Saved File has improper header."
		assert "latitude" in test_df.columns, error_msg
		assert "longitude" in test_df.columns, error_msg
		assert "address" in test_df.columns, error_msg


	def test_GeocodeLocations_run_one_batch(self, tmp_path):
		"""Tests the .run() and associated methods for
		GeocodeLocations.
		"""
		p = tmp_path/"test.csv"

		gl = gc.GeocodeLocations(self.address_df, valid_email, p)
		gl._set_test_geocoder()

		gl.run()

		test = pd.read_csv(p)

		assert not test.empty, "No results saved to disk."
		assert not gl.locations.empty, "No results stored in object."

		assert len(test) == 234, "Not all lines were saved to disk"
		assert len(gl.locations) == 234, "Not all lines were saved in object"


	def test_GeocodeLocations_run_mult_batches(self, tmp_path):
		"""Tests the .run() and associated methods for GeocodeLocations when
		multiple batches are needed.
		"""
		p = tmp_path/"test.csv"

		gl = gc.GeocodeLocations(self.address_df, valid_email, p,
		                         batch_size = 100)
		gl._set_test_geocoder()

		gl.run()

		test = pd.read_csv(p)

		assert gl.tot_batches == 3, "Batches are not constructed properly."

		assert not test.empty, "No results saved to disk."
		assert not gl.locations.empty, "No results stored in object."

		assert len(test) == 234, "Not all lines were saved to disk."
		assert len(gl.locations) == 234, "Not all lines were saved in object."


	def test_GeocodeLocations_run_less_than_all_batches(self, tmp_path):
		"""Tests the .run() and associated methods for GeocodeLocations when
		running less than all batches. 
		"""
		p = tmp_path/"test.csv"

		gl = gc.GeocodeLocations(self.address_df, valid_email, p,
		                         batch_size = 100)
		gl._set_test_geocoder()

		gl.run(num_batches = 1)

		test = pd.read_csv(p)

		assert gl.tot_batches == 3, "Batches are not constructed properly."
		assert gl.curr_batch < 3, "Run running too many batches."

		assert not test.empty, "No results saved to disk."
		assert not gl.locations.empty, "No results stored in object."

		assert len(test) < 234, "Not all lines were saved to disk."
		assert len(gl.locations) < 234, "Not all lines were saved in object."


	def test_GeocodeLocations_process_address_string(self, tmp_path):
		"""Tests the .run() and associated methods for GeocodeLocations when
		running on a list of address strings.
		"""
		p = tmp_path/"test.csv"

		gl = gc.GeocodeLocations(self.address_list, valid_email, p,
		                         batch_size = 100)
		gl._set_test_geocoder()

		gl.run()

		test = pd.read_csv(p)

		assert gl.tot_batches == 3, "Batches are not constructed properly."

		assert not test.empty, "No results saved to disk."
		assert not gl.locations.empty, "No results stored in object."

		assert len(test) == 234, "Not all lines were saved to disk."
		assert len(gl.locations) == 234, "Not all lines were saved in object."


	def test_GeocodeLocations_address_dict(self, tmp_path):
		"""Tests the .run() and associated methods when constructing df from
		list of dicts.
		"""
		p = tmp_path/"test.csv"

		gl = gc.GeocodeLocations(self.address_dict, valid_email, p,
		                         batch_size = 100)
		gl._set_test_geocoder()

		gl.run()

		test = pd.read_csv(p)

		assert gl.tot_batches == 3, "Batches are not constructed properly."

		assert not test.empty, "No results saved to disk."
		assert not gl.locations.empty, "No results stored in object."

		assert len(test) == 234, "Not all lines were saved to disk."
		assert len(gl.locations) == 234, "Not all lines were saved in object."


	def test_GeocodeLocations_test_real_geocoder(self, tmp_path):
		"""Tests the .run() and associated methods with a real geocoder
		"""
		p = tmp_path/"test.csv"

		gl = gc.GeocodeLocations(self.address_df, valid_email, p,
		                         batch_size = 1)
		gl.run(num_batches=3)

		assert all(gl.locations.all())


	def test_GeocodeLocations_reset(self, tmp_path):
		"""
		"""
		#Mocks the input asking for DELETE
		gc.input = lambda *args : "DELETE"

		p = tmp_path/"test.csv"

		gl = gc.GeocodeLocations(self.address_df, valid_email, p)
		gl._set_test_geocoder()

		gl.run()

		gl.reset()

		test = pd.read_csv(p)

		assert test.empty, "File was not deleted"
		assert gl.curr_batch == 1, "Batches were not reset"
		assert len(gl._queue) == 234, "Queue was not reset"


	def teardown_method(self):
		gc.input = input
		gc.email = valid_email #undoes ._set_test_geocoder()

