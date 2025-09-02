import requests
from pathlib import Path
from Orange.widgets.orangecontrib.AAIT.webserver.start_server import start_server
import aiohttp
from typing import List
import time

def start_server_on_port(port=8000, method ="same_terminal"):
    """
    Starts the server on the specified port.

    :param port: Port to start the server on.
    :param method: The method to start the server.
    """
    print("Starting the server...")
    server = start_server(port, method=method) # type: ignore
    return "http://localhost:{}".format(port)


def launch_workflow(base_url, workflow_name="image-test.ows", force_reload="false", gui="true"):
    """
    Launch the specified workflow on the server.

    :param base_url: The base URL of the server.
    :param workflow_name: The name of the workflow to launch.
    :param force_reload: Whether to force reload the workflow.
    :param gui: Whether to use the GUI.
    :return: Workflow ID if the launch is successful, raise an exception otherwise.
    """
    print("Launching the workflow...")
    launch_response = requests.post(
        f"{base_url}/launch-workflow/",
        params={
            "workflow_name": workflow_name,
            "force_reload": force_reload,
            "gui": gui
        }
    )
    if launch_response.status_code == 200:
        print("Workflow launched successfully.")
        return workflow_name
    else:
        raise Exception("Failed to launch workflow. Status code: {}".format(launch_response.status_code))



def fetch_files(base_url: str, unique_id: str, mode: str):
    """
    Perform a GET request to fetch files using the specified base URL, unique ID, and return mode.

    :param base_url: The base URL of the server.
    :param unique_id: The unique ID for retrieving specific resources.
    :param modes: The mode in which return should be formatted. It is expected to be a string like 'file'.
    :return: The response from the server in JSON format.
    """
    print(f"fetching files in mode {mode}...")
    # Define the endpoint specific to file retrieval
    endpoint = f"/retrieve-outputs/{unique_id}"

    # Construct full URL by concatenating the base_url and endpoint
    full_url = base_url + endpoint

    # Set up headers and parameters
    headers = {
        'Accept': 'application/json'
    }
    params = {
        'return_mode': mode
    }

    # Perform the GET request with headers and parameters
    response = requests.get(full_url, headers=headers, params=params)

    # Return the JSON response
    return response.content

def upload_files_via_path(base_url: str, workflow_id: str, filepaths: List[Path]):
    # Construct the URL
    url = f"{base_url}/upload-files-via-path/"
    
    # Prepare headers
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    # Prepare the JSON payload
    payload = {
        "filepaths": [str(path) for path in filepaths],
        "file_ids": ["input1"] * len(filepaths),
        "opening_methods": ["image_file"] * len(filepaths),
        "text_inputs_id": [],
        "text_inputs_value": []
    }
    
    # Append additional parameters to the URL
    params = {
        'workflow_id': workflow_id,
        'expected_nb_outputs': 1,
        'timeout_limit': 10
    }
    
    # Make the POST request
    response = requests.post(url, headers=headers, json=payload, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        print('Upload successful:', response.json())
        return response.json()['unique_id']
    else:
        print('Upload failed:', response.status_code, response.text)
        raise ValueError("Failed to upload files.")


def main():
    # Example usage
    data_path = Path(__file__).parent / "dataTests"
    file_paths = list(data_path.glob("*.TIF"))

    # base_url = start_server_on_port()
    base_url = "http://localhost:8000"
    workflow_id = launch_workflow(base_url)
    time.sleep(5)   
    unique_id = upload_files_via_path(base_url, workflow_id, file_paths)
    print("unique_id", unique_id)
    time.sleep(2)
    for method in ["json", "html", "file"]:
        response = fetch_files(base_url, unique_id, mode=method)
        print(f"Response in {method} mode:", response)


if __name__ == "__main__":
    main()
