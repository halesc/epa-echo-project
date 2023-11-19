"""
This file is used to extract the raw data from the EPA's ECHO database. The data is downloaded from the EPA's website and extracted to the lib/raw folder.
This file can take a while to run, as it downloads and extracts 6 zip files. The files are large, and the extraction process is slow.
"""

import io
import os
import requests
import zipfile
from dotenv import load_dotenv

load_dotenv()

# Access the variables using os.environ
path_variable = os.environ.get("DEV_PATH")

# TODO: Add state databases.

ECHO_LOC = f"{path_variable}/lib/raw/"
URL1 = "https://echo.epa.gov/files/echodownloads/ICIS-AIR_downloads.zip"
URL2 = "https://echo.epa.gov/files/echodownloads/frs_downloads.zip"
URL3 = "https://echo.epa.gov/files/echodownloads/echo_demographics.zip"
URL4 = "https://echo.epa.gov/files/echodownloads/npdes_downloads.zip"
URL5 = "https://echo.epa.gov/files/echodownloads/npdes_eff_downloads.zip"
URL6 = "https://echo.epa.gov/files/echodownloads/case_downloads.zip"
ZIP_URLS = [URL1, URL2, URL3, URL4, URL5, URL6]
WRITE_PATH = os.path.join(os.path.dirname(os.path.abspath("")[:-3]), ECHO_LOC)


def download_and_extract_zip(url, destination_folder):
    """
    Download and extract a zip file from a url to a destination folder.
    :param url: The url of the zip file.
    :param destination_folder: The folder to extract the zip file to.
    """
    response = requests.get(url)

    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
        zip_file.extractall(destination_folder)


# Generate folder.
try:
    os.mkdir(WRITE_PATH)
except FileExistsError:
    pass
# Download and extract the data.
# TODO: Check for a way to get less tables vs all.
print("Downloading and Extracting Files...", flush=True)
print("This process can take a while. Please be patient.", flush=True)
for url in ZIP_URLS:
    try:
        download_and_extract_zip(url, WRITE_PATH)
    except Exception as e:
        print(f"Error: {str(e)} - {url} ", flush=True)
    print(f"Completed: {url}", flush=True)
print("Finished downloading and extracting zip files. Saved to lib/raw.", flush=True)
