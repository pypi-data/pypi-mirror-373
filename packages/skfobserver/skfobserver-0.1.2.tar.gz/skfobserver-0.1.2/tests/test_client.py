# skfobserver/tests/test_client.py

import pytest
import json
import requests_mock # Tool for mocking HTTP requests
from datetime import datetime, timedelta
import time  
import os
import configparser
# Import the APIClient and custom exceptions from your package
# This assumes your __init__.py exposes APIClient directly,
# and your exceptions are defined in client.py
from skfobserver import APIClient
from skfobserver.client import SKFObserverAPIError, SKFObserverAuthError

# --- Mocking Setup ---
# Use consistent mock values for tests
config_parser = configparser.ConfigParser()
config_dir = os.path.join(os.path.expanduser('~'), '.skfobserver')
config_file_path = os.path.join(config_dir, '.config') 
files_read = config_parser.read(config_file_path) 
TEST_USERNAME = config_parser["profile skfobserver"].get('username') # manully pull the username from the local config file 
TEST_PASSWORD = config_parser["profile skfobserver"].get('password') # manully pull the username from the local config file
TEST_BASE_URL = config_parser["profile skfobserver"].get('base_url') # manully pull the username from the local config file
 
# --- Pytest Fixture for Client ---
# This fixture can provide a pre-configured client for tests,
# useful if many tests need a client instance.

@pytest.fixture
def mock_skf_client():
    """Provides a basic APIClient instance for testing."""
    # Note: For actual tests, you'd typically mock the authentication
    # within each test function or a more elaborate fixture
    # to control the exact mock behavior.
    return APIClient(username = TEST_USERNAME, password = TEST_PASSWORD, base_url = TEST_BASE_URL)

# --- Test Functions ---
def test_initial_client_setup(requests_mock):
    """
    Test that the client can be initialized and attempts authentication.
    """
    # Mock the authentication endpoint's response
    requests_mock.post(
        f"{TEST_BASE_URL}/token",
        json={"access_token": "mock_initial_token", "refresh_token": "mock_refresh_token", "expires_in": 3600},
        status_code=200
    ) 
    client = APIClient(username = TEST_USERNAME, password = TEST_PASSWORD, base_url = TEST_BASE_URL)
    
    assert client._access_token == "mock_initial_token"
    assert client._refresh_token == "mock_refresh_token"
    assert client._token_expiry_time is not None
    assert requests_mock.called # Verify that an HTTP request was made

# --- Test Functions with profile ---
def test_initial_client_setup_profile(requests_mock):
    """
    Test that the client can be initialized and attempts authentication.
    """
    # Mock the authentication endpoint's response
    requests_mock.post(
        f"{TEST_BASE_URL}/token",
        json={"access_token": "mock_initial_token", "refresh_token": "mock_refresh_token", "expires_in": 3600},
        status_code=200
    ) 
    client = APIClient(profile_name="skfobserver")
    
    # This to make sure that it was able to pull data from profile and use it in the api call
    auth_request = requests_mock.last_request 

    assert "Username=" in auth_request.text
    assert "password=" in auth_request.text
    assert "grant_type=" in auth_request.text 
    assert client._access_token == "mock_initial_token"
    assert client._refresh_token == "mock_refresh_token"
    assert client._token_expiry_time is not None
    assert requests_mock.called # Verify that an HTTP request was made

def test_initial_auth_failure(requests_mock):
    """
    Test that client initialization raises an error on authentication failure.
    """
    requests_mock.post(
        f"{TEST_BASE_URL}/token",
        json={"message": "Invalid credentials"},
        status_code=401
    ) 
    with pytest.raises(SKFObserverAuthError, match="Initial authentication failed"):
        APIClient(username = TEST_USERNAME, password = "wrong_password", base_url = TEST_BASE_URL) 
    assert requests_mock.call_count == 1

def test_get_machines_success(requests_mock):
    """
    Test a successful call to get_machines.
    """
    # Mock the initial authentication
    requests_mock.post(
        f"{TEST_BASE_URL}/token",
        json={"access_token": "initial_token", "expires_in": 3600},
        status_code=200
    )
    # Mock the actual /machines endpoint response
    requests_mock.get(
        f"{TEST_BASE_URL}/v1/machines",
        json=[{"id": "machine1", "name": "Test Machine"}],
        status_code=200,
        # Ensure the correct Authorization header is used
        request_headers={"Authorization": "Bearer initial_token"}
    )
    
    client = APIClient(username = TEST_USERNAME, password =  TEST_PASSWORD, base_url = TEST_BASE_URL)
    machines = client.get_machines()
    
    assert isinstance(machines, list)
    assert len(machines) == 1
    assert machines[0]["id"] == "machine1"
    # requests_mock keeps track of calls; we expect 2 calls: 1 for auth, 1 for get_machines
    assert requests_mock.call_count == 2
 

def test_automatic_token_refresh_on_401(requests_mock):
    """
    Test that the client fails with an exception on a 401 after attempting a token refresh.
    """
    # 1. Mock initial authentication with a very short-lived token
    requests_mock.post(
        f"{TEST_BASE_URL}/token",
        json={"access_token": "expired_token", "refresh_token": "valid_refresh", "expires_in": 1},
        status_code=200
    )
    
    # 2. Mock the token refresh requests that the client will make
    requests_mock.post(
        f"{TEST_BASE_URL}/token",
        json={"access_token": "new_fresh_token", "expires_in": 3600},
        status_code=200
    )
    
    # 3. Mock the get_machines request, expecting the client to fail here
    requests_mock.get(
        f"{TEST_BASE_URL}/v1/machines",
        json={'message': 'Unauthorized'},
        status_code=401,
        request_headers={'Authorization': 'Bearer new_fresh_token'}
    )
    
    # Initialize the client. This triggers the first POST call.
    client = APIClient(username=TEST_USERNAME, password=TEST_PASSWORD, base_url=TEST_BASE_URL)
    
    # Assert that calling get_machines() raises the expected exception
    with pytest.raises(SKFObserverAPIError) as excinfo:
        client.get_machines()

    # Verify that the exception message indicates a 401 failure
    assert "401" in str(excinfo.value)
    
    # Verify that the correct number of calls were made
    assert requests_mock.call_count >= 3
 

def test_refresh_token_failure(requests_mock):
    """
    Test that if refresh token itself fails, an authentication error is raised.
    """
    # 1. Mock initial authentication (token will be "expired" later in test)
    requests_mock.post(
        f"{TEST_BASE_URL}/token",
        json={"access_token": "initial_token", "refresh_token": "invalid_refresh_token", "expires_in": 1},
        status_code=200
    )
    client = APIClient(username = TEST_USERNAME, password = TEST_PASSWORD, base_url = TEST_BASE_URL)
    
    # 2. Mock an API call returning 401
    requests_mock.get(
        f"{TEST_BASE_URL}/v1/machines",
        json={'message': 'Unauthorized'},
        status_code=401
    )
    
    # 3. Mock the refresh token request itself failing
    requests_mock.post(
        f"{TEST_BASE_URL}/token",
        json={"message": "Refresh token invalid"},
        status_code=400 # Simulate refresh endpoint returning 401
    )
    
    with pytest.raises(SKFObserverAuthError, match="Failed to refresh token"):
        client.get_machines()
    # Verify that the correct requests were made
    assert requests_mock.call_count == 2
   
   
def test_proactive_token_refresh(requests_mock):
    """
    Test that the client proactively refreshes the token before it expires,
    avoiding a 401 on the actual data request.
    """
    # 1. Mock initial auth with a short-lived token (e.g., 1 second)
    requests_mock.post(
        f"{TEST_BASE_URL}/token",
        json={"access_token": "initial_token_proactive", "refresh_token": "valid_refresh_proactive", "expires_in": 1},
        status_code=200
    )
    client = APIClient(username=TEST_USERNAME, password=TEST_PASSWORD, base_url=TEST_BASE_URL)
    
    # 2. Mock the refresh token call.
    # NOTE: The 'data' parameter is removed to avoid the TypeError
    requests_mock.post(
        f"{TEST_BASE_URL}/token",
        json={"access_token": "proactively_refreshed_token", "expires_in": 3600},
        status_code=200
    )
    
    # 3. Mock the actual data endpoint, expecting the *new* token
    requests_mock.get(
        f"{TEST_BASE_URL}/v1/machines",
        json=[{"id": "proactive_machine", "name": "Proactive Machine"}],
        status_code=200,
        request_headers={"Authorization": "Bearer proactively_refreshed_token"}
    )
    
    # 4. Simulate time passing so the token is near expiration
    time.sleep(1.5)
    
    # 5. Execute the method that triggers the refresh and data request
    machines = client.get_machines()

    # 6. Assertions to verify the test's success
    assert machines[0]["id"] == "proactive_machine"
    assert client._access_token == "proactively_refreshed_token"
    
    # 7. Assert the call count.
    assert requests_mock.call_count >= 3


def get_machine_data_success(requests_mock):
    """Test fetching specific machine data successfully."""
    requests_mock.post(
        f"{TEST_BASE_URL}/token",
        json={"access_token": "init_token", "expires_in": 3600},
        status_code=200
    )
    machine_id = "test_machine_123"
    start = datetime(2025, 1, 1, 10, 0, 0)
    end = datetime(2025, 1, 1, 11, 0, 0)
    
    requests_mock.get(
        f"{TEST_BASE_URL}/machines/{machine_id}/data",
        json=[{"time": "...", "value": 100}],
        status_code=200,
        # requests_mock also checks query parameters if provided
        qs={"start": start.isoformat().replace('+00:00', 'Z'), "end": end.isoformat().replace('+00:00', 'Z')}
    )

    client = APIClient(username = TEST_USERNAME, password = TEST_PASSWORD, base_ul = TEST_BASE_URL)
    data = client.get_machine_data(machine_id, start, end)
    
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["value"] == 100

def send_event_success(requests_mock):
    """Test sending an event successfully."""
    # Mock initial authentication
    requests_mock.get(
        f"{TEST_BASE_URL}/token",
        json={"access_token": "init_token", "expires_in": 3600},
        status_code=200
    )
    event_payload = {"type": "TEST_EVENT", "description": "This is a test."}

    # Corrected way to mock:
    # The first 'json' is the expected *request* body (what your client sends)
    # The 'json' inside the dictionary is the *response* body (what the mock server returns)
    requests_mock.post(
        f"{TEST_BASE_URL}/events",
        json=event_payload, # This defines the EXPECTED request body (what your client sends)
        status_code=200,
        response_json={"eventId": "abc-123-def"} # This defines the actual JSON RESPONSE from the mock API
    )

    client = APIClient(username = TEST_USERNAME, password = TEST_PASSWORD, base_ul = TEST_BASE_URL)
    response = client.send_event(event_payload)

    assert response["eventId"] == "abc-123-def"
    # You can also check that the correct request was made:
    assert requests_mock.called_once # Ensures the event endpoint was hit once
    history = requests_mock.request_history
    assert len(history) == 2 # Auth post, then event post
    assert history[1].json() == event_payload # Verify the body of the second request
    assert history[1].url == f"{TEST_BASE_URL}/events"


def test_get_trend_measurements(requests_mock):
    """
    Test fetching trend measurements with optional query parameters.
    """
    # Mock initial authentication
    requests_mock.post(
        f"{TEST_BASE_URL}/token",
        json={"access_token": "init_token", "expires_in": 3600},
        status_code=200
    )
    
    # Mock the API response for trend measurements
    mock_response = [
        {"ReadingTimeUTC": "2023-01-01T12:00:00Z", "PointID": 100, "Measurements": [{"Level": 5.2, "Channel": 1}]},
        {"ReadingTimeUTC": "2023-01-01T12:01:00Z", "PointID": 100, "Measurements": [{"Level": 5.3, "Channel": 1}]}
    ]

    requests_mock.get(
        f"{TEST_BASE_URL}/v1/points/100/trendMeasurements",
        json=mock_response,
        status_code=200,
        # We can add an assertion on the params here
        # E.g., request_history[1].qs == {'numReadings': ['1'], 'descending': ['false']}
    )
    
    client = APIClient(username=TEST_USERNAME, password=TEST_PASSWORD, base_url=TEST_BASE_URL)
    
    # Make a call with optional query parameters
    measurements = client.get_trend_measurements(point_id=100, numReadings=1, descending=False)

    # Assert that the response is correct
    assert len(measurements) == 2
    assert measurements[0]["PointID"] == 100
    
    # Assert that the correct requests were made
    assert requests_mock.call_count == 2

    
def test_get_hierarchy(requests_mock):
    """
    Test fetching the hierarchy with and without points.
    """
    # Mock initial authentication
    requests_mock.post(
        f"{TEST_BASE_URL}/token",
        json={"access_token": "init_token", "expires_in": 3600},
        status_code=200
    )
    
    # Mock the hierarchy response without points
    hierarchy_mock_response = [
        {"name": "Company", "path": "Company", "children": [{"name": "Machine", "children": []}]}
    ]

    requests_mock.get(
        f"{TEST_BASE_URL}/v1/hierarchy",
        json=hierarchy_mock_response,
        status_code=200,
        # Check that includePoints is False by default
        # E.g., request_history[1].qs == {'includePoints': ['false']}
    )
    
    # Mock the hierarchy response with points
    hierarchy_with_points_mock_response = [
        {"name": "Company", "children": [{"name": "Machine", "children": [{"name": "Point", "typeName": "ePointSwSpeed"}]}]}
    ]

    requests_mock.get(
        f"{TEST_BASE_URL}/v1/hierarchy",
        json=hierarchy_with_points_mock_response,
        status_code=200,
        # E.g., request_history[2].qs == {'includePoints': ['true']}
    )
    
    client = APIClient(username=TEST_USERNAME, password=TEST_PASSWORD, base_url=TEST_BASE_URL)
    
    # Test without including points
    hierarchy_without_points = client.get_hierarchy()
    assert hierarchy_without_points[0]["name"] == "Company"
    
    # Test with including points
    hierarchy_with_points = client.get_hierarchy(include_points=True)
    assert hierarchy_with_points[0]["children"][0]["children"][0]["typeName"] == "ePointSwSpeed"

    # Assert that the correct number of calls were made
    assert requests_mock.call_count >= 3

