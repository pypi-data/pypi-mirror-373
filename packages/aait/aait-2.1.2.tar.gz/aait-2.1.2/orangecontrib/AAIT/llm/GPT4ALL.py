import configparser
import json
import os
import subprocess
import tempfile
import sys
import time
import xml.etree.ElementTree as ET
from os.path import expanduser

import chardet
import psutil
from Orange.data import Domain, StringVariable, Table

# change this variable to choose a non-standard path
gpt4all_path = ""

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.utils import SimpleDialogQt
    from Orange.widgets.orangecontrib.AAIT.utils.MetManagement import get_local_store_path,getTempDir
else:
    from orangecontrib.AAIT.utils import SimpleDialogQt
    from orangecontrib.AAIT.utils.MetManagement import get_local_store_path,getTempDir


def get_gpt4all_exe_path():
    # If OS is Windows
    if os.name == 'nt':
        if gpt4all_path != "":
            return gpt4all_path
        none_standard_path=sys.executable.replace("\\","/")
        none_standard_path=os.path.dirname(none_standard_path)
        none_standard_path = os.path.dirname(none_standard_path)
        none_standard_path=none_standard_path+"/gpt4all/bin/chat.exe"
        if os.path.isfile(none_standard_path):
            return none_standard_path

        if os.path.isfile(os.path.join(os.getenv('USERPROFILE'), "gpt4all", "bin", "chat.exe")):
            return os.path.join(os.getenv('USERPROFILE'), "gpt4all", "bin", "chat.exe").replace("\\","/")
        none_standard_path = sys.executable.replace("\\", "/")
        none_standard_path = os.path.dirname(none_standard_path)
        none_standard_path = os.path.dirname(none_standard_path)
        none_standard_path = none_standard_path + "/Orange/Lib/site-packages/forall/gpt4all/bin/chat.exe"
        if os.path.isfile(none_standard_path):
            return none_standard_path
        SimpleDialogQt.BoxError("GPT4All Not found!")
        return ""
    if os.name=="posix":# Macintosh and Unix
        if str(os.uname().sysname) == "Darwin":  # Macintosh"
            return "/Applications/gpt4all/bin/gpt4all.app"
        # case Unix not  implemented now
    SimpleDialogQt.BoxError("OS not supported")
    return ""

def get_gpt4all_ini_path():

    if os.name == 'nt':
        appdata_path = os.getenv('APPDATA')
        config_file_path = os.path.join(appdata_path, "nomic.ai", "GPT4All.ini")
        return config_file_path

    elif os.name=="posix":# Macintosh and Unix
        if str(os.uname().sysname) == "Darwin": # Macintosh
            config_file_path = os.path.expanduser("~")
            config_file_path = config_file_path.replace("\\", "/")
            config_file_path =config_file_path+"/.config/gpt4all.io/GPT4All.ini"
            return config_file_path
        # case Unix not  implemented now
    else:
        SimpleDialogQt.BoxError("OS not supported")
        return ""

def get_process_name():
    if os.name == 'nt':
        return "chat.exe"
    if os.name == "posix":
        return "gpt4all"
    SimpleDialogQt.BoxError("OS not supported")
    return ""

# write time in a temp file to be checked if necessary to kill process
def write_time_in_temp_file():
    # print("maj horadatage")
    temp_dir = getTempDir()
    file_path = os.path.join(temp_dir, 'date_heure.txt')
    current_time_seconds = int(time.time())
    with open(file_path, 'w') as file:
        file.write(str(current_time_seconds))

def open_gpt_4_all(table, model_path, progress_callback=None, widget=None):
    """
    Opens the GPT4All application if it is not already running. It waits for the application to be ready,
    then generates and cleans the response using the `generate_and_clean_response` function. If the generation
    and cleaning is successful, it creates a new table with an answer domain and returns it. If the application
    fails to open or the generation and cleaning times out, it returns None.

    :param table: The input table.
    :type table: Orange.data.Table
    :param model_path: The input model.
    :type model_path: str
    :param progress_callback: A callback function to track progress.
    :type progress_callback: function
    :param widget: The widget calling this function.
    :type widget: Orange.widgets.Widget
    :return: A table with an answer domain or None.
    :rtype: Orange.data.Table or None
    """

    # Modify GPT4All configuration
    modify_gpt4all_config()

    # If table is None, return None
    if table is None:
        return None

    # Launch GPT4All application if not already running
    gpt4all_exe_path = get_gpt4all_exe_path()
    # If GPT4All is not already running, try to launch it
    if not is_process_running(get_process_name()):
        try:
            os_type = os.name
            show_window_gpt4all = False
            if os.path.exists(os.path.join(getTempDir(), 'view4all.txt')):
                show_window_gpt4all=True
            if os_type == "nt":
                if show_window_gpt4all == True:
                    subprocess.Popen([gpt4all_exe_path], shell=False, creationflags=subprocess.CREATE_NO_WINDOW)
                else:
                    # Chemin vers ton fichier exécutable exe_path = "chemin/vers/ton_executable.exe"
                    # Créer une instance de STARTUPINFO
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    # Utiliser la fenêtre de démarrage
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                    # Masquer la fenêtre
                    # Lancer le processus avec la fenêtre masquée subprocess.run(exe_path, startupinfo=startupinfo)
                    subprocess.Popen([gpt4all_exe_path], startupinfo=startupinfo, shell=False, creationflags=subprocess.CREATE_NO_WINDOW)

                    # writing a timestamp to a time file
                    write_time_in_temp_file()
                    time.sleep(3)

                    file_py_killer = os.path.dirname(os.path.abspath(__file__)).replace("\\",
                                                                                        "/") + "/GPT4ALL_killer.py"
                    time.sleep(1)
                    #launch of a process that kills chat.exe after a certain period of time
                    subprocess.Popen([sys.executable, file_py_killer], shell=False, creationflags=subprocess.CREATE_NO_WINDOW)





            elif str(os.uname().sysname) == "Darwin": # machintosh
                subprocess.run(["open", gpt4all_exe_path],shell=False)
            else:
                print("platform not suported")
                return None
                #subprocess.Popen([gpt4all_exe_path], shell=False)

        except Exception as e:
            print(f"Error opening GPT4All: {e}")
            if widget is not None:
                widget.error("GPT4All can't be reached check installation")
            return None

    # Wait for GPT4All to be ready
    rows = None

    # wait until gpt4all is opened
    nb_iter_max=10
    for i in range(nb_iter_max):
        time.sleep(0.5)
        if is_process_running(get_process_name()):
            break





    # Wait for GPT4All to be ready or timeout
    if rows is None :
        rows = generate_and_clean_responses(table,model_path, progress_callback)
    # If GPT4All is not ready after timeout, return None
    if rows is None:
        print("Timeout waiting for GPT4All to be ready")
        if widget is not None:
            widget.error("GPT4 must be running. Please launch it and try again.")
        return None

    # Create and return table with answer domain
    answer_dom = [StringVariable("Answer")]
    domain = Domain(attributes=table.domain.attributes, metas=(list(table.domain.metas)) + answer_dom,
                    class_vars=table.domain.class_vars)
    return Table.from_list(domain=domain, rows=rows)

def generate_and_clean_responses(data,model_path, progress_callback):
    """
    Generate and clean responses for each row in the input data.

    Parameters
    ----------
    data : Orange.data.Table
        The input data.
    model_path : str
        The path to the model.
    progress_callback : function
        A callback function to track progress.

    Returns
    -------
    list of lists
        The rows of cleaned responses.
    """
    responses = []
    answer = None
    for i, row in enumerate(data):
        try:
            # Extract features and metas for the current row
            features = list(data[i])
            metas = list(data.metas[i])

            # Call the completion API to get the answer
            prompt = str(row["prompt"])
            for n_try in range(50):# try 50 time
                print("try to call gpt4all ",n_try)
                time.sleep(0.5)
                answer = call_completion_api("localhost:4891",model_path, prompt)
                if answer is not None:
                    break
            # Correct misencoded text and clean the response
            answer = clean_response(answer)

            # Append the answer to the metas list and the current row to the responses list
            metas.append(answer)
            responses.append(features + metas)
        except Exception:
            # If an error occurs, continue to the next row
            continue

        # If a progress callback is provided, call it with the progress value
        if progress_callback:
            progress_value = 100 * (i + 1) / len(data)
            progress_callback(progress_value)

    # If no responses were generated, return None
    if not responses:
        return None

    # Return the rows of cleaned responses
    return responses

def get_model_in_gpt4all():
    """
    Get the name of the model in GPT4All.

    Returns
    -------
    str or None
        The name of the model if it exists, None otherwise.
    """
    # Define the path to the directory containing the models
    model_path = os.path.join(get_local_store_path(), "Models") + "/NLP"
    if not os.path.isdir(model_path):
        return
    # Iterate over the files in the directory
    for filename in os.listdir(model_path):
        # Check if the file name contains "solar" and ends with ".gguf"
        if "solar" in filename and filename.endswith(".gguf"):
            # Return the filename if it meets the conditions
            return filename
    # If no file meets the conditions, return None
    return None



def get_latest_version_from_xml(file_path, package_name="gpt4all"):
    try:
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Search for the specific package and extract its version
        for package in root.findall('Package'):
            name = package.find('Name').text
            if name == package_name:
                version = package.find('Version').text
                return version
        return None  # If package not found
    except Exception as e:
        print(f"Error: {e}")
        return None

def modify_gpt4all_config():
    """
    Modify the GPT4All configuration to set the GPU device, enable server mode, and configure network settings.

    The function reads the existing configuration file, if it exists, and modifies the necessary sections to set the
    GPU device, server mode, model, and network settings. If a section does not exist, it is created.

    The configuration file is located at `os.getenv('APPDATA')/nomic.ai/GPT4All.ini`.

    Returns:
        None
    """
    if os.name != "nt":
        print("-------------------------------------")
        print("WARNING: Auto config file not provided for OS != Windows, please configure GPT4ALL before using these widgets")
        print("-------------------------------------")
        return

    config_file_path = get_gpt4all_ini_path()
    os.makedirs(os.path.dirname(config_file_path), exist_ok=True)

    gpu_name = get_gpu_name()
    model_name = get_model_in_gpt4all()
    local_store_path = get_local_store_path()
    model_path = os.path.join(local_store_path, "Models", "NLP").replace("\\", "/")
    gpt_version = get_latest_version_from_xml(expanduser("~") + r"\gpt4all\components.xml")

    config = configparser.ConfigParser()

    if os.path.exists(config_file_path):
        try:
            config.read(config_file_path)
        except Exception as e:
            print("Error reading config file:", e)
            print("Creating a new config file...")
            os.remove(config_file_path)

    if not config.has_section('General'):
        config.add_section('General')
    config['General'].update({
        'device': gpu_name if gpu_name else '',
        'serverChat': 'true',
        'userDefaultModel': model_name if model_name else '',
        'modelPath': model_path
    })

    model_section = f"model-{model_name}"
    if not config.has_section(model_section):
        config.add_section(model_section)
    config[model_section].update({
        'filename': str(model_name),
        'contextLength': '4096',
    })

    if not config.has_section('download'):
        config.add_section('download')
    config['download']['lastVersionStarted'] = str(gpt_version)

    if not config.has_section('network'):
        config.add_section('network')
    config['network'].update({
        'usageStatsActive': 'false',
        'isActive': 'false'
    })

    if os.access(config_file_path, os.W_OK):  # Vérifie les droits en écriture
        try:
            with open(config_file_path, 'w') as config_file:
                config.write(config_file)
                print("writing config file to:", config_file_path)
        except PermissionError:
            print(f"Error: No write permission for {config_file_path}")
    else:
        print(f"Error: No write permission for {config_file_path}")
def is_process_running(process_name):
    """
    Check if a process with the given name is already running.

    Parameters:
    process_name (str): The name of the process to check.

    Returns:
    bool: True if a process with the given name is running, False otherwise.
    """

    # Iterate over the running processes and check if the process name matches.
    for process in psutil.process_iter(['name']):
        # Convert both the process name and the given process name to lowercase for case-insensitive comparison.
        if process_name.lower() in process.info['name'].lower():
            # If a match is found, return True.
            return True

    # If no match is found, return False.
    return False


def call_completion_api(localhost, model_name, message_content, temperature=0, top_p=0,max_tokens=4096):
    """
    Calls the GPT4All completion API and returns the response.

    Parameters:
    localhost (str): The address of the local server.
    model_name (str): The name of the model to be used.
    message_content (str): The content of the message to be sent.

    Returns:
    str or None: The response from the API, or None if an error occurs.
    """
    #print(f"Sending message to GPT-4All: {message_content}")
    # Define the command for the API call using curl
    # Créez le payload JSON
    payload = {
        "temperature": temperature,
        "top_p": top_p,
        "model": model_name,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": message_content}]
    }
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as temp_file:
        json.dump(payload, temp_file, ensure_ascii=False)
        temp_filename = temp_file.name

    command = [
        "curl",
        "--noproxy", "*",
        "--location",
        f"http://{localhost}/v1/chat/completions",
        "--header", "Content-Type: application/json; charset=UTF-8",
        "--data", f"@{temp_filename}"
    ]

    try:
        os_type = os.name
        # Determine the OS type and execute the command accordingly
        if os_type == "nt":
            # On Windows, execute the command using subprocess and suppress the CMD window
            write_time_in_temp_file()  # Record the timestamp
            response = subprocess.check_output(
                command,
                universal_newlines=True,
                shell=False,
                encoding='utf-8',
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            os.remove(temp_filename)
            return response
        elif str(os.uname().sysname) == "Darwin":  # On macOS
            import requests

            # Prepare the request data and headers
            request_data = {
                "temperature": temperature,
                "top_p": top_p,
                "model": model_name,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": message_content}]
            }
            request_url = f"http://{localhost}/v1/chat/completions"
            request_headers = {"Content-Type": "application/json; charset=UTF-8"}

            try:
                # Send the POST request to the API
                response = requests.post(
                    request_url,
                    headers=request_headers,
                    data=json.dumps(request_data),
                )
                response.raise_for_status()  # Raise an error for bad responses
                print("Response received:", response)
                os.remove(temp_filename)
                return response.text
            except Exception as e:
                print(f"Error during API call: {e}")
        else:
            print("Platform not supported")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error during API call: {e}")
        return None




def get_gpu_name():
    import platform
    import subprocess
    """
    Checks if an NVIDIA GPU is present on the system and retrieves its name.

    This function uses platform-specific commands to check for a GPU:
    - Windows: Uses 'wmic' and 'nvidia-smi'.
    - macOS: Uses 'system_profiler' and 'nvidia-smi' if NVIDIA GPUs are supported.
    - Linux (Ubuntu): Uses 'lspci' and 'nvidia-smi'.

    Returns:
        str: The GPU name prefixed with "CUDA: " if a GPU is found.
        None: If no GPU is found or an error occurs.
    """
    try:
        os_type = platform.system()

        if os_type == "Windows":
            # Check for GPU on Windows using wmic
            wmic_output = subprocess.check_output(
                ['wmic', 'path', 'win32_VideoController', 'get', 'name'],
                text=True
            )
            if "NVIDIA" not in wmic_output:
                return None
        elif os_type == "Darwin":  # macOS
            # Check for GPU on macOS using system_profiler
            sp_output = subprocess.check_output(
                ['system_profiler', 'SPDisplaysDataType'],
                text=True
            )
            print(sp_output)
            if "NVIDIA" not in sp_output:
                return None
        elif os_type == "Linux":
            # Check for GPU on Linux using lspci
            lspci_output = subprocess.check_output(
                ['lspci'],
                text=True
            )
            if "NVIDIA" not in lspci_output:
                return None
        else:
            return None

        # If NVIDIA GPU is found, use nvidia-smi to get the GPU name
        nvidia_smi_output = subprocess.check_output(
            ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
            text=True
        )
        gpu_name = nvidia_smi_output.strip()
        return "CUDA: " + gpu_name

    except FileNotFoundError:
        # Command not found (wmic, system_profiler, lspci, or nvidia-smi)
        return None
    except subprocess.CalledProcessError:
        # If an error occurs while running the command, return None.
        return None
    except Exception:
        # Catch any other unexpected errors
        return None

def clean_response(response_data):
    """
    Cleans the response text by removing special characters and correcting encoding issues.

    Parameters:
    response_data (str): The response data from the API.

    Returns:
    str: The cleaned and corrected response text.
    """
    try:
        # Parse the response data as JSON
        data = json.loads(response_data)


        # Extract the message content from the response
        choices = data.get("choices", [{}])
        message_content = choices[0].get("message", {}).get("content", "") if choices else ""
        return message_content

    except (json.JSONDecodeError, IndexError):
        # If an error occurs, return an empty string
        return ""

def detect_encoding(file_path):
    """
    Detects the encoding of a file using the chardet library.

    Parameters:
    file_path (str): The path to the file.

    Returns:
    str: The detected encoding of the file.
    """
    # Open the file in binary mode
    with open(file_path, 'rb') as file:
        # Read the file data
        file_data = file.read()

    # Detect the encoding of the file using chardet
    encoding_result = chardet.detect(file_data)

    # Return the detected encoding
    return encoding_result['encoding']

def extract_text_from_file(file_path):
    """
    Extracts and returns text content from a file with proper encoding detection.

    Parameters:
    file_path (str): The path to the file.

    Returns:
    str: The text content of the file.
    """
    # Define the supported encodings for the file
    supported_encodings = ['utf-8', 'latin-1', 'cp1252']

    # Iterate over the supported encodings
    for encoding in supported_encodings:
        try:
            # Open the file with the current encoding and read its content
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()

        # If a UnicodeDecodeError occurs, move to the next encoding
        except UnicodeDecodeError:
            continue

    # If no encoding works, return an empty string
    return ""

if __name__ == "__main__":
    modify_gpt4all_config()