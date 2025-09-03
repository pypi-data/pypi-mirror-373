# skfobserver/skfobserver/client.py

import requests
import datetime
import time 
import os
import configparser  
from typing import List 
from .hierarchy_models import NodeContainer
from .machine_models import MachineCollection
class SKFObserverAPIError(Exception):
    """Custom exception for SKF Observer API errors."""
    pass

class SKFObserverAuthError(SKFObserverAPIError):
    """Custom exception for SKF Observer API authentication errors."""
    pass

class APIClient:
    """
    Client for interacting with the SKF Observer API.

    Handles authentication, token refresh, and provides methods
    for common API operations like reading data.
    """
    def __init__(self, username: str= None
                 , password: str = None
                 , base_url: str = ""
                 , grant_type: str = None
                 , profile_name: str = None):
        
         
        self._session = requests.Session()
        self._access_token = None
        self._refresh_token = None
        self._token_expiry_time = None

        # --- Define hardcoded fallback values ---
        self._default_username = None
        self._default_password = None
        self._default_grant_type = None
        self._default_base_url = ""
        
        # --- Determine credentials order of precedence ---
        # 1. Explicit arguments to __init__ take highest precedence
        self.username = username if username else None
        self.password = password if password else None
        self.grant_type = grant_type if grant_type else "password"
        self.base_url = base_url if base_url else "" 
        
        # 2. Try to read from config file using the specified profile (or 'default')
        config_read_username, config_read_password, config_read_base_url = \
            self._read_credentials_from_config(profile_name)
        
        # Apply config values IF the corresponding argument was NOT provided
        if not self.username:
            self.username = config_read_username
        if not self.password:
            self.password = config_read_password
        if not self.base_url:
            self.base_url = config_read_base_url
        
        # 3. Fall back to hardcoded defaults if still missing after args and config attempts
        if not self.username:
            self.username = self._default_username
            print(f"Warning: Username not found via args or config. Using default: {self.username}")
        if not self.password:
            self.password = self._default_password
            print("Warning: Password not found via args or config. Using default password.")
        if not self.base_url:
            self.base_url = self._default_base_url
            print(f"Warning: Base URL not found via args or config. Using default: {self.base_url}")
        
        # Ensure base_url doesn't have a trailing slash for consistent path joining
        if self.base_url.endswith('/'):
            self.base_url = self.base_url[:-1]
         
        # Authenticate immediately upon client creation
        self._authenticate()
        print(f"APIClient initialized at '{self.base_url}'")
        #self.check_for_updates()
        self.settings = self.get_settings() 
        self.hierarchy = self.get_hierarchy()
        self.machines = self.get_machines()
        self.time_metadata_collected = datetime.datetime.now()


    def _read_credentials_from_config(self, profile_name: str = None):
        """
        Helper method to read credentials from the user's config file based on profile.
        Prioritizes specified profile, then 'default' profile.
        Returns (username, password, base_url) or (None, None, None) if not found/error.
        """
        config_parser = configparser.ConfigParser()
        
        # Construct the cross-platform path to the config file
        config_dir = os.path.join(os.path.expanduser('~'), '.skfobserver')
        config_file_path = os.path.join(config_dir, '.config') 
        read_username = None
        read_password = None
        read_base_url = ""

        target_section_names = []
        if profile_name:
            target_section_names.append(f"profile {profile_name}")
        # Always try 'default' if no specific profile, or if specified profile didn't yield results
        target_section_names.append("profile default") 
        #print(f"Attempting to read config from: {config_file_path}")
        try:
            files_read = config_parser.read(config_file_path)
            if files_read:
                found_any_section = False
                for section_name in target_section_names:
                    if section_name in config_parser:
                        found_any_section = True
                        read_username = config_parser[section_name].get('username')
                        read_password = config_parser[section_name].get('password')
                        read_base_url = config_parser[section_name].get('base_url')
                        
                        # If we found at least one non-empty value, use this section's values
                        # You can refine this: e.g., require ALL to be present, or only use if username/password found
                        if read_username and read_password:
                            print(f"Credentials loaded from section '{section_name}' in '{config_file_path}'.")
                            break # Found credentials, stop searching
                        else:
                            print(f"Section '{section_name}' found, but missing username/password in '{config_file_path}'. Trying next if available.")
                            # Reset for next section attempt
                            read_username, read_password, read_base_url = None, None, None 

                if not found_any_section:
                    print(f"Neither specified profile nor default profile found in '{config_file_path}'.")
            else:
                print(f"Config file not found at '{config_file_path}'.")
        except configparser.Error as e:
            print(f"Error parsing config file '{config_file_path}': {e}.")
        except Exception as e:
            print(f"An unexpected error occurred while reading config: {e}.")

        return read_username, read_password, read_base_url


 

    def _authenticate(self):
        """Authenticates with the API and obtains access/refresh tokens."""
        auth_url = f"{self.base_url}/token"    
        try:
            response = self._session.post(auth_url, {"Username":self.username,"password":self.password, "grant_type":self.grant_type}) 
            response.raise_for_status()  
            data = response.json()
            self._access_token = data["access_token"]
            self._session.headers.update({"Authorization": f"Bearer {self._access_token}"})
            self._refresh_token = data.get("refresh_token")
            self._token_expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=data["expires_in"])
            print("SKFObserver: Successfully authenticated and obtained tokens.",self._token_expiry_time)
        except requests.exceptions.RequestException as e:
            raise SKFObserverAuthError(f"SKFObserver: Initial authentication failed: {e}")
        except KeyError:
            raise SKFObserverAuthError("SKFObserver: Authentication response missing required token fields.")

    def _refresh_access_token(self):
        """Uses the refresh token to get a new access token.""" 
        if not self._refresh_token:
            # If no refresh token, or it's been revoked, force re-authentication
            print("SKFObserver: No refresh token available or it's invalid. Attempting full re-authentication...")
            self._authenticate() # Attempt full re-auth with username/password
            return

        refresh_url = f"{self.base_url}/token" 
        print(refresh_url)
        try:
            response = self._session.post(refresh_url, 
                                        {
                                            "Username":"",
                                            "password":"", 
                                            "grant_type":"refresh_token",
                                            "refresh_token": self._refresh_token 
                                        }) 
            response.raise_for_status()
            data = response.json()
            self._access_token = data["access_token"]
            self._session.headers.update({"Authorization": f"Bearer {self._access_token}"})
            if "refresh_token" in data: # Update refresh token if rotated by API
                self._refresh_token = data["refresh_token"]
            self._token_expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=data["expires_in"])
            print("SKFObserver: Access token refreshed successfully using refresh token.")
        except requests.exceptions.RequestException as e:
            raise SKFObserverAuthError(f"SKFObserver: Failed to refresh token: {e}. Please ensure your credentials are valid or manually re-initialize.")


    def _check_and_refresh_token(self):
        """Checks if token is near expiry and refreshes if needed.""" 
        # Refresh if token expires in less than 60 seconds (or has already expired)
        if self._token_expiry_time and datetime.datetime.now() >= (self._token_expiry_time - datetime.timedelta(seconds=60)):
            print("SKFObserver: Access token is expiring or expired. Attempting to refresh...")
            self._refresh_access_token()

    def _make_request(self, method: str, endpoint: str, retry_count: int = 1, **kwargs):
        """Internal helper to make API requests with automatic retry on token expiry."""
        for attempt in range(retry_count + 1):
            self._check_and_refresh_token() # Proactive check before request

            headers = {"Authorization": f"Bearer {self._access_token}"}
            kwargs.setdefault('headers', {}).update(headers)
            
            url = f"{self.base_url}{endpoint}" 
            try: 
                print(url)
                response = self._session.request(method, url, **kwargs) 
                response.raise_for_status() 
                if response.content:
                    # If the response has a body, return it as JSON
                    return response.json()
                else:
                    # Handle 204 No Content gracefully by returning None
                    return None 
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401 and attempt < retry_count:
                    print(f"SKFObserver: Request failed with 401. Attempting token refresh and retry...")
                    try:
                        self._refresh_access_token()
                    except SKFObserverAuthError:
                        raise # Re-raise if refresh itself fails
                elif e.response.status_code in [400, 404, 500]:
                    try:
                        error_message = e.response.json().get('message', 'An API error occurred.')
                    except ValueError:
                        error_message = f"An API error occurred with status code {e.response.status_code}."
                    raise SKFObserverAPIError(f"API Error: {error_message}") from e

                else:
                    raise SKFObserverAPIError(f"An unexpected API error occurred with status code {e.response.status_code}.") from e

                #else:
                #    raise SKFObserverAPIError(f"SKFObserver: API request failed ({e.response.status_code}): {e.response.text}") from e
            except requests.exceptions.RequestException as e:
                raise SKFObserverAPIError(f"SKFObserver: Network or connection error: {e}") from e
    """
    def check_for_updates(self): 
        try:
            # Use pkg_resources to get the installed version of your package
            current_version = pkg_resources.get_distribution("skfobserver").version
            
            # Query the PyPI API for the latest version
            response = requests.get("https://pypi.org/pypi/skfobserver/json")
            response.raise_for_status()
            pypi_version = response.json()["info"]["version"]

            # Compare the versions
            if pkg_resources.parse_version(pypi_version) > pkg_resources.parse_version(current_version):
                print("-" * 50)
                print(f"🎉 A new version of skfobserver ({pypi_version}) is available!")
                print(f"   You are using version {current_version}.")
                print(f"   To upgrade, run: pip install --upgrade skfobserver")
                print("-" * 50)

        except pkg_resources.DistributionNotFound:
            print("Warning: 'skfobserver' not installed via pip. Cannot check for updates.")
        except requests.exceptions.RequestException:
            # Silently fail if there's a network or connection issue
            pass
        except Exception as e:
            # Catch any other unexpected errors
            print(f"An error occurred while checking for updates: {e}")
    # --- Public API Methods for Customers ---
    """
    def get_settings(self):
        """
        Fetches the full settings of observer 
        """
        endpoint = "/v1/settings"
        response = self._make_request("GET", endpoint, params={})  
        if response:   
            return  response
        else:
            return response
        
    def get_machines(self) -> list[dict]:
        """  
        Retrieves a list of all machines registered in the SKF Observer application.

        This function makes a GET request to the '/machines' endpoint of the API.
        It does not require any parameters.

        Returns:
            list[dict]: A list of dictionaries, where each dictionary represents a machine.
                        Each machine dictionary typically includes fields :
                        id (integer, optional): Database ID of the machine ,
                        - name (string, optional): Name of the machine ,
                        - description (string, optional): Description of the machine ,
                        - path (string, optional): Hierarchy path from the root to the machine ,
                        - driving (Array[CM.Phoenix.Model.General.IdString], optional): Properties for the driving unit like manufacturer, type, serial number and coupling ,
                        - driven (Array[CM.Phoenix.Model.General.IdString], optional): Properties for the driven unit like manufacturer, type, serial number and coupling. ,
                        - transmission (Array[CM.Phoenix.Model.General.IdString], optional): Properties for the transmission unit like manufacturer, type and serial number ,
                        - machineCode (string, optional): Machine code for asset ,
                        - power (string, optional): Power of the driving unit ,
                        - gear (string, optional): Type of gear for transmission ,
                        - isoClass (integer, optional): Machine ISO class according with vibration level standards ,
                        - idContact (integer, optional): Id of user set as contact person for the machine ,
                        - conditionalPoint (integer, optional): Id of the conditional point ,
                        - conditionalPointSrc (string, optional): Link to the conditional point ,
                        - conditionalPointTag (Array[CM.Phoenix.Model.General.IdString], optional): Properties for the conditional point tag, such as name and description. ,
                        - coordinates (Array[CM.Phoenix.Model.General.IdSingle], optional): coordinates

        Raises:
            SKFObserverAPIError: If the API call fails due to network issues,
                                 invalid response, or server errors.
            SKFObserverAuthError: If authentication fails or tokens cannot be refreshed.

        Example:
            >>> client = APIClient(username="test_user", password="test_password")
            >>> machines = client.get_machines()
            >>> for machine in machines:
            ...     print(f"Machine ID: {machine['id']}, Name: {machine['name']}") 
        
        """ 
        response = self._make_request("GET", "/v1/machines") 
        if(response):
            self.machines = response
            return self.machines
        else:
            return MachineCollection([]) 

    def get_machine_data(self, machine_id: str, start_time: datetime.datetime, end_time: datetime.datetime):
        """
        Fetches data for a specific machine within a time range.

        Args:
            machine_id: The ID of the machine.
            start_time: The start time for data (datetime object).
            end_time: The end time for data (datetime object).
        """
        # Placeholder: Adjust endpoint and query parameters based on your API docs
        params = {
            "start": start_time.isoformat(),
            "end": end_time.isoformat(),
            # Add other relevant parameters
        }
        return self._make_request("GET", f"/machines/{machine_id}/data", params=params)

    def send_event(self, event_data: dict):
        """Sends an event to the Observer API."""
        # Placeholder: Adjust endpoint and request body structure
        return self._make_request("POST", "/events", json=event_data)

    
    def get_trend_measurements(self, point_id: int, **kwargs):
        """
        Fetches a list of trend measurements for a specified point.

        Args:
            point_id: The ID of the measurement point.
            **kwargs: Optional query parameters from the API documentation:
                      numReadings, fromDateUTC, toDateUTC, directionNumber,
                      includeAlarmInfo, descending.
        """
        endpoint = f"/v1/points/{point_id}/trendMeasurements"
        response = self._make_request("GET", endpoint, params=kwargs)
        if response:
            # If a response was received, return its JSON content.
            return response
        else:
            # If the response was None (204 No Content), return an empty list.
            return []
    
  

    def get_hierarchy(self, include_points: bool = True):
        """
        Fetches the full hierarchy of the system.

        Args:
            include_points: A boolean to include point data in the hierarchy.
                            Defaults to False.
        """
        endpoint = "/v1/hierarchy"
        params = {"includePoints": include_points}
        response = self._make_request("GET", endpoint, params=params)  
        if response:   
            self.hierarchy = NodeContainer(response)
            return  self.hierarchy
        else:
            return NodeContainer([])