"""
TESTS FOR bbd.geocoder
"""

from bbd import geocoder as gc
import pytest

import geopy
import timeit
from math import isclose

# --------------------------------------
#  ##########   UNIT TESTS   ##########
# --------------------------------------

# ++++++ Test get_geocoder ++++++
class TestGet_geocoder:
	"""
	Tests for get_geocoder in bbd.geocoder
	"""
	def test_reject_invalid_email(self):
		"""
		Test get_geocoder only accepts valid email
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
		email = "test@bluebonnetdata.org"
		geocoder = gc.get_geocoder(email)

		address = "Evans Hall, Berkeley, CA"
		location = gc.geocoder(address)

		error1 = "Geocoder returned None. Either email not accepted "\
				 "or address not found by OpenStreetMap"
		error2 = "Geocoder did not return geopy.location.Location"
		error3 = "Geocder matched with wrong address."
		assert location is not None, error1
		assert isinstance(location, geopy.location.Location), error2
		assert (location.address.contains("Evans Hall") 
		        & isclose(location.latitude, 38.57656885) 
		        & isclose(location.longitude, -121.4934010890531)), error3


	def test_miniumum_runtime(self):
		"""
		Tests that the geocoder runs at most 1 address per second
		in accordance with Nominatim terms of service.
		"""
		email = "test@bluebonnetdata.org"
		geocoder = gc.get_geocoder(email)

		n = 3 

		t0 = timeit.default_timer()
		
		for i in range(n):
			gc.geocoder("")

		t1 = timeit.default_timer()

		error = "Geocoder running more than once per second violating"\
				"Nominatim terms of service."
		assert t1-t0 >= n, error
		

# ++++++ Test get_reverse_geocoder ++++++
class TestGet_reverse_geocoder:
	"""
	Tests for get_reverse_geocoder in bbd.geocoder
	"""
	def test_reject_invalid_email(self):
		"""
		Test get_reverse_geocoder only accepts valid email
		"""
		invalid_email = "not an email"
		with pytest.raises(AssertionError):
			gc.get_reverse_geocoder(invalid_email)


	def test_reverse_geocoder(self):
		"""
		Test that the reverse geocoder returned by get_reverse_geocoder
		accurately reverse geocodes an address.
		"""
		email = "test@bluebonnetdata.org"
		reverse_geocoder = gc.get_reverse_geocoder(email)
		pass

	def test_miniumum_runtime(self):
		"""
		Tests that the geocoder runs at most 1 address per second in 
		accordance with Nominatim terms of service.
		"""
		pass


# ++++++ Test street_encode +++++++
class TestStreet_encode:
	"""
	Tests for street_encode in bbd.geocoder
	"""
	def test_unedited_inputs(self):
		"""
		Tests that street_encode will return its input when no regex
		match is found.
		"""
		test = "101 Test Ave"

		error = "street_encode not returning input when there are"\
				" no regex matches."
		assert gc.street_encode(test) is test, error


	def test_None_input(self):
		"""
		Tests that street_encode returns an empty string when input 
		is None.
		"""
		test = None

		error = "street_encode not converting None into empty string."
		assert gc.street_encode(test) == "", error


	def test_edited_inputs(self):
		"""
		Tests that secondary descriptors are being properly trimmed.
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

		error_msg = f"{len(errors)} failed... street_encode failed to trim "\
					"secondary descriptors from :"\
					"\n".join(errors)
		assert not errors, error_msg


# ++++++ Test GeoLocation Methods ++++++
class TestGeocodeLocation:
	"""
	"""
	def test1(self):
		pass


	def test2(self):
		pass

		
	def test3(self):
		pass
