# MISA_pySLIME/__init__.py

# first, pull in the downloader so data are in place
from .FILEDOWNLOAD import ensure_data
ensure_data()

__version__ = "2.0.6"

from .MISA_pySLIME import (
    get_lat_lon,
    get_az_alt,
    query_model,
    predict_generic,
    predict_ne,
    predict_ti,
    predict_te,
)

__all__ = [
    "get_lat_lon",
    "get_az_alt",
    "query_model",
    "predict_generic",
    "predict_ne",
    "predict_ti",
    "predict_te",
]