Markdown

# SKF Observer Python Library

A robust and easy-to-use Python client library designed to simplify integration with the SKF Observer API. This library handles authentication, token refreshing, and provides intuitive methods for reading data and interacting with your Observer application programmatically.

## Features

-   **Seamless Authentication:** Automatic handling of access and refresh tokens.
-   **Easy Data Access:** Simple Python functions to retrieve machine data, events, and other Observer resources.
-   **Error Handling:** Built-in error handling for common API responses.
-   **Structured Interface:** A clear, object-oriented approach to API interaction.

## Installation

You can install `skfobserver` using pip:

```bash
pip install skfobserver
```


USAGE 


```bash
from skfobserver import APIClient
from skfobserver.client import SKFObserverAPIError # For specific error handling
from datetime import datetime, timedelta

# Replace with your actual SKF Observer API credentials
USERNAME = "YOUR_API_USERNAME"
PASSWORD = "YOUR_API_PASSWORD"

try:
    # Initialize the client (authentication happens automatically here)
    client = APIClient(username=USERNAME, password=PASSWORD)

    # Example 1: Get a list of all machines
    print("Fetching machines...")
    machines = client.get_machines()
    for machine in machines:
        print(f"  Machine ID: {machine.get('id')}, Name: {machine.get('name')}")

    # Example 2: Get data for a specific machine over the last 24 hours
    if machines:
        target_machine_id = machines[0].get('id') # Use the first machine found
        print(f"\nFetching data for machine ID: {target_machine_id} (last 24 hours)...")
        end_time = datetime.now()
        start_time = end_time - timedelta(days=1)
        machine_data = client.get_machine_data(
            machine_id=target_machine_id,
            start_time=start_time,
            end_time=end_time
        )
        print(f"  Retrieved {len(machine_data)} data points for {target_machine_id}.")
        # print(f"  First data point: {machine_data[0]}") # Uncomment to see actual data

    # Example 3: Send an event to the API
    print("\nSending a test event...")
    event_payload = {
        "type": "MAINTENANCE_LOG",
        "machineId": "some_machine_id", # Replace with a valid machine ID for testing
        "timestamp": datetime.now().isoformat(),
        "description": "Routine check completed by automated script.",
        "severity": "INFO"
    }
    response_event = client.send_event(event_payload)
    print(f"  Event sent successfully. Response ID: {response_event.get('eventId')}")

except SKFObserverAuthError as e:
    print(f"Authentication Error: {e}")
    print("Please check your username and password, or if your refresh token has expired, re-initialize the client.")
except SKFObserverAPIError as e:
    print(f"API Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}") 


```
 

