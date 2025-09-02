import json
import os
import subprocess
import zipfile
# import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.utils import SimpleDialogQt
else:
    from orangecontrib.AAIT.utils import SimpleDialogQt
try:
    from ..utils import MetManagement
except:
    from Orange.widgets.orangecontrib.AAIT.utils import MetManagement



def generate_listing_json(directory_to_list):
    """
    generate a file file_info.json  with size of file in directory
    for low level devellopper only
    -> use create_index_file
    """
    output_json_file = directory_to_list+'/files_info.json'
    if os.path.isfile(output_json_file):
        os.remove(output_json_file)

    def list_files_recursive(directory):
        files_info = {}

        for root, dirs, files in os.walk(directory):
            for file in files:

                file_path = os.path.join(root, file).replace("\\","/")
                file_size = os.path.getsize(file_path)
                file_path=file_path[len(directory)+1:]
                files_info[file_path]=file_size

        return files_info

    def save_to_json(data, output_file):
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    files_info = list_files_recursive(directory_to_list)
    save_to_json(files_info, output_json_file)
    return files_info

def add_file_to_zip_file(folder,file_in,zip_file):
    """
    folder : a point to start relative path
    file in : a file to add to zip file
    zip file : destination zip file
    for exemple I want to add C:/dir1/dir2/dir3/qwerty.txt to
    C:/dir1//dir2/example.zip and index dir3/qwerty.txt
    folder = C:/dir1/
    file_in=C:/dir1/dir2/dir3/qwerty.txt
    zip_file  C:/dir2/example.zip
    """
    path_in=folder+file_in
    with open(path_in, 'rb') as f:
        contenu = f.read()
    with zipfile.ZipFile(zip_file, 'a', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(file_in, contenu)

def create_index_file(in_repo_file,out_repo_file="a_ignorer"):
    """
    delete files_info.json and regenerate it
    with file contain a dictionnary filename:filesize
    out_repo_file is not used
    """
    if not os.path.isfile(in_repo_file):
        raise Exception("The specified path is not a file "+in_repo_file)
    if 0!=MetManagement.get_size(in_repo_file):
        raise Exception("The file " + in_repo_file+ " need to be empty to use this functions")
    print(MetManagement.get_size(in_repo_file))
    folder_to_process=os.path.dirname(in_repo_file).replace("\\","/")
    file_info=generate_listing_json(folder_to_process)
    print(file_info)
    return

def decode(repo_file,file_to_read):
    """
    /!\ be carrefull with big file (ram saturation)
    return containt of a zipped file
    """
    if not os.path.isfile(repo_file):
        return None
    file_to_read=os.path.splitext(os.path.basename(repo_file))[0]+"/"+file_to_read
    with zipfile.ZipFile(repo_file, 'r') as zip_ref:
        with zip_ref.open(file_to_read) as file:
            content = file.read()
            return content.decode('utf-8')
def decode_to_file(zip_path, target_path, output_path):
    """
    extract a file from a zip file and write it on hdd
    example : I want to extract dir1/qwerty.txt from C:/dir1/dir2/zipfile.zip to C:/dir_a/dir_b/dir1/qwerty.txt
    zip_path=C:/dir1/dir2/zipfile.zip
    target_path=dir1/qwerty.txt
    output_path=C:/dir_a/dir_b/
    """
    chunk_size = 1024 * 1024 * 100 # 100 Mo
    target_path=os.path.splitext(os.path.basename(zip_path))[0]+"/"+target_path
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        target_path = target_path.rstrip('/')
        files_to_extract = [f for f in zip_ref.namelist() if f.startswith(target_path)]

        if len(files_to_extract) == 0:
            raise FileNotFoundError(f"{target_path} not found in the archive.")

        if len(files_to_extract) == 1 and not files_to_extract[0].endswith('/'):
            # Cible est un fichier unique
            output_file_path = output_path
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            with zip_ref.open(files_to_extract[0]) as source, open(output_file_path, 'wb') as target:
                #target.write(source.read())
                while True:
                    # read and write a chunk to avoid ram limitation
                    chunk = source.read(chunk_size)
                    if not chunk:
                        break
                    target.write(chunk)
        else:
            # Cible est un dossier ou plusieurs fichiers
            for file in files_to_extract:
                relative_path = os.path.relpath(file, start=target_path)
                destination_path = os.path.join(output_path, relative_path)

                if file.endswith('/'):
                    os.makedirs(destination_path, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                    with zip_ref.open(file) as source, open(destination_path, 'wb') as target:
                        #target.write(source.read())
                        while True:
                            # read and write a chunk to avoid ram limitation
                            chunk = source.read(chunk_size)
                            if not chunk:
                                break
                            target.write(chunk)

def normalize_path(path):
    """
    Normalize paths for URLs and local usage:
    - Replaces backslashes (\) with forward slashes (/).
    - Removes './' and '\.' segments from paths.
    - Handles redundant slashes.
    """
    # Replace backslashes with slashes
    path = path.replace("\\", "/")

    # Remove any occurrences of './' or '\.'
    path = path.replace("./", "").replace("/./", "/")

    # Clean up multiple slashes (e.g., "///" -> "/")
    path = os.path.normpath(path).replace("\\", "/")

    # Remove trailing and leading slashes (if required)
    path = path.strip("/")

    return path


def normalize_child_name(href):
    """
    Cleans and normalizes the given path or file name.

    This function takes a path or file name as input, and performs the following operations:
    1. Strips leading and trailing whitespace from the input.
    2. Normalizes the path using `os.path.normpath`, which:
        - Removes redundant separators (e.g., '///' -> '/').
        - Removes up-level references (e.g., '/../' -> '').
    3. Removes leading './' from the path if present.

    Parameters:
    href (str): The path or file name to normalize.

    Returns:
    str: The normalized path or file name.
    """
    # 1. Strip leading and trailing whitespace
    child = href.strip()

    # 2. Normalize the path
    child = os.path.normpath(child)

    # 3. Remove leading "./" if present
    if child.startswith("." + os.sep):
        child = child[len("." + os.sep):]

    return child


def download_from_folder_server(base_url: str, local_dir: str = ".", target_subfolder: str = "",
                                visited: set = None) -> None:
    """
    Recursively retrieves all files and subdirectories from the subfolder
    `target_subfolder` on the remote server (base_url) and recreates the structure in the local directory (local_dir).

    :param base_url: Base URL of the server (e.g., "http://server.com/folder").
    :param local_dir: Local path where the downloaded files will be stored.
    :param target_subfolder: Relative path (on the server) to download.
    :param visited: Set of URLs already visited to avoid loops.
    """
    if visited is None:
        visited = set()

    # Build the full URL from the base and the relative path.
    full_url = urljoin(base_url.rstrip('/') + '/', target_subfolder.strip('/'))
    if full_url in visited:
        return
    visited.add(full_url)

    # Determine the local destination path based on target_subfolder.
    # If target_subfolder ends with an extension, it is considered a file.
    local_target_dir = Path(local_dir) / target_subfolder.strip('/')
    is_file = os.path.splitext(target_subfolder)[1] != ""

    if is_file:
        # Direct file download.
        local_filename = local_target_dir
        dialog_progress = SimpleDialogQt.ProgressDialog(
            title="Synchronization, please wait",
            content=("Synchronization of the file " + full_url + "\nThis operation may take a few minutes"))
        dialog_progress.show()
        if MetManagement.already_downloaded_compressed_server(base_url, target_subfolder,
                                                              str(local_filename.resolve())):
            print(f"{local_filename.resolve()} already downloaded -> skip")
            return

        local_filename.parent.mkdir(parents=True, exist_ok=True)
        curl_command = f'curl -L -# -C - -o "{local_filename.resolve()}" "{full_url}"'
        try:
            creation_flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            process = subprocess.Popen(
                curl_command,
                shell=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                creationflags=creation_flags
            )
            while True:
                line = process.stdout.readline()
                if line == "" and process.poll() is not None:
                    break
                if line:
                    print(line.strip())

            retcode = process.poll()
            if retcode != 0:
                print(f"Download failed for {full_url} with return code {retcode}")
            else:
                if not local_filename.exists():
                    print(f"Error: the file {local_filename} does not exist after download.")
                else:
                    print(f"File downloaded: {local_filename.resolve()}")
                    dialog_progress.stop()
        except Exception as e:
            print(f"Exception during download of {full_url}: {e}")
        return

    else:
        creation_flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

        # Case for a folder: retrieve the listing using curl.
        curl_command = f'curl -L -# -C - "{full_url}"'
        process = subprocess.Popen(curl_command, shell=True,text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT,creationflags=creation_flags)
        html_lines = []
        while True:
            line = process.stdout.readline()
            print(type(line),line)
            if line == "" and process.poll() is not None:
                break
            if line:
                html_lines.append(line)
        retcode = process.poll()
        if retcode != 0:

            print(f"Failed to retrieve listing for {full_url} with code {retcode}")
            # Attempt direct download in this case:
            local_filename = local_target_dir
            local_filename.parent.mkdir(parents=True, exist_ok=True)
            # Build the curl command
            curl_command = f'curl -L -# -C - -o "{local_filename.resolve()}" "{full_url}"'
            dialog_progress = SimpleDialogQt.ProgressDialog(
                title="Synchronization, please wait",
                content=("Synchronization of the file " + full_url + "\nThis operation may take a few minutes"))
            dialog_progress.show()
            # On Windows, add the flag to avoid creating a new window.
            creation_flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

            # Run the curl command with no output and no window.
            process = subprocess.Popen(
                curl_command,
                shell=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                creationflags=creation_flags
            )
            if process.returncode != 0:
                print(f"Direct download failed for {full_url}: {process.stderr}")
            else:
                print(f"File downloaded: {local_filename.resolve()}")
                dialog_progress.stop()
            return

        html_content = "".join(html_lines)
        # Parse the HTML content to detect a directory listing.
        soup = BeautifulSoup(html_content, 'html.parser')
        h1 = soup.find('h1')
        has_listing_indicator = (h1 and "contenu de" in h1.get_text().lower())
        table = soup.find('table')

        if has_listing_indicator and table:
            rows = table.find_all('tr')
            for row in rows:
                links = row.find_all('a', href=True)
                if not links:
                    continue
                link = links[0]
                href = link['href']
                if href.startswith('../'):
                    continue

                # Normalize the name using the dedicated function.
                child_name = normalize_child_name(href)
                child_url = urljoin(full_url + '/', href)
                if href.endswith('/'):
                    # Subfolder detected: recursive call.
                    new_target_subfolder = os.path.join(target_subfolder.strip('/'), child_name)
                    new_target_subfolder = os.path.normpath(new_target_subfolder).replace('\\', '/')
                    download_from_folder_server(
                        base_url=base_url,
                        local_dir=local_dir,
                        target_subfolder=new_target_subfolder,
                        visited=visited
                    )
                else:
                    # File detected in the listing.
                    local_filename = local_target_dir / child_name
                    local_filename_parsed = str(local_filename).replace("\\", "/")
                    creation_flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    dialog_progress = SimpleDialogQt.ProgressDialog(
                        title="Synchronization, please wait",
                        content=("Synchronization of the file " + full_url + "\nThis operation may take a few minutes"))
                    dialog_progress.show()
                    if MetManagement.already_downloaded_compressed_server(
                            base_url, f"{target_subfolder}/{child_name}", local_filename_parsed
                    ):
                        print(f"{local_filename.resolve()} already downloaded -> skip")
                        return
                    local_filename.parent.mkdir(parents=True, exist_ok=True)
                    print(f"Downloading file: {child_url} to {local_filename.resolve()}")
                    process_file = subprocess.Popen(
                        ["curl", "-L","-#", "-C", "-o", str(local_filename.resolve()), child_url],
                        shell=True,text=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT,creationflags=creation_flags
                    )
                    if process_file.returncode != 0:
                        print(f"Direct download failed for {full_url}: {process.stderr}")
                    else:
                        print(f"File downloaded: {local_filename.resolve()}")
                        dialog_progress.stop()
        else:
            # No directory listing detected: treat it as a single file.
            local_filename = local_target_dir
            dialog_progress = SimpleDialogQt.ProgressDialog(
                title="Synchronization, please wait",
                content=("Synchronization of the file " + full_url + "\nThis operation may take a few minutes"))
            dialog_progress.show()
            if MetManagement.already_downloaded_compressed_server(
                    base_url, target_subfolder, str(local_filename.resolve())
            ):
                print(f"{local_filename.resolve()} already downloaded -> skip")
                return
            local_filename.parent.mkdir(parents=True, exist_ok=True)

            curl_command = f'curl -L -# -C - -o "{local_filename.resolve()}" "{full_url}"'
            process = subprocess.Popen(
                curl_command, shell=False, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            if process.returncode != 0:
                print(f"Direct download failed for {full_url}: {process.stderr}")
            else:
                print(f"File downloaded: {local_filename.resolve()}")
                dialog_progress.stop()
            return


if __name__ == "__main__":
    # create the json needed to http / zipped stored
    in_repo_file="C:/modele_NLP/IFIA_models/repository.aait"
    create_index_file(in_repo_file)

