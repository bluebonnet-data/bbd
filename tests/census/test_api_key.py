import pytest
import requests
import requests_mock

from bbd import census, models


def test_api_key_required():
    with pytest.raises(ValueError):
        census.construct_api_call(
            geography=models.Geography.STATE,
            variables="B03003_001E",
            year=2018,
            dataset=census.DataSet.ACS5,
        )

def test_can_request_data():
    census.api_key = ""


def test_can_set_api_key():
    SAMPLE_API_KEY = "abc123"
    census.api_key.key = SAMPLE_API_KEY
    assert census.api_key.key == SAMPLE_API_KEY


def test_can_call_census_api():
    SAMPLE_API_KEY = "abc123"
    census.api_key.key = SAMPLE_API_KEY
    url = census.construct_api_call(
        geography=models.Geography.STATE,
        variables="B03003_001E",
        year=2018,
        dataset=census.DataSet.ACS5,
    )

    def callback(request: requests.Request, context):
        # Check for "valid" sample API key
        if request.qs['key'] != [SAMPLE_API_KEY]:
            context.status_code = 404
            context.reason = "Invalid API key"
            return "Invalid API key"
        else:
            context.status_code = 200
            return "Valid API key"

    with requests_mock.Mocker() as mocker:
        mocker.get(url, text=callback)
        assert requests.get(url).text == "Valid API key"

