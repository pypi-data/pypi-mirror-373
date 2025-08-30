# MISA_pySLIME/filedownload.py
import os
import requests
import zipfile

# Dropbox URLs for required files (direct‐download)
MISA_DS_URL      = "https://www.dropbox.com/scl/fi/59ypmunnxai36c1rn1ury/MISA_ds_2.0.6.nc.zip?rlkey=fh4f9o71ffh94h9n9da93lxf3&st=fylj904e&dl=1"
GEO_DS_URL       = "https://www.dropbox.com/scl/fi/slo7d1iv752l5ejqpgq7x/master_geo_ds_2.0.10.nc?rlkey=etcwdxaugl9vvz4gkiqgstx6b&st=1tw5noke&dl=1"

# Where to save them in your repo
MISA_DS_PATH     = os.path.join(os.path.dirname(__file__), "ancillary","processed_ncs", "MISA_ds_2.0.6.nc")
MASTER_GEO_PATH  = os.path.join(os.path.dirname(__file__), "ancillary","processed_ncs", "master_geo_ds_2.0.10.nc")

def download_file(url, save_path, unzip=False):
    """Download a file from URL if it doesn't already exist."""
    if os.path.exists(save_path):
        return
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    print(f"Downloading → {save_path}")
    r = requests.get(url, stream=True)
    r.raise_for_status()
    tmp = save_path + (".zip" if unzip else "")
    with open(tmp, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
    if unzip:
        with zipfile.ZipFile(tmp, "r") as z:
            z.extractall(os.path.dirname(save_path))
        os.remove(tmp)

def ensure_data():
    """Ensure that the two big .nc files are present locally."""
    download_file(MISA_DS_URL, MISA_DS_PATH,    unzip=True)
    download_file(GEO_DS_URL,  MASTER_GEO_PATH, unzip=False)