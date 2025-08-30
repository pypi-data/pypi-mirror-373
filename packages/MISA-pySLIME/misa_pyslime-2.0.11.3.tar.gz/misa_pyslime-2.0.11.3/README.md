# **MISA pySLIME: Ionospheric Background Modeling Toolkit**
*Millstone Hill Incoherent Scatter Radar Spatial-Linear Ionospheric Modeling Engine*

--- 
MISA pySLIME is a Python library for building and querying binned‑regression ionospheric background models for ion and electron temperature (`Ti`/`Te`) and density (`Ne`) from Millstone Hill Incoherent Scatter Radar (MISA) data.
It supports querying predictions for both `lat`&`lon` and `alt`&`azimuth`, day of year (`DOY`), and solar local time (`SLT`) or universal time (`UT`), while leveraging pre-computed geophysical indices. The library also supports efficient vectorized predictions for multiple inputs.
---

## **Features**  
- Predict electron density (`Ne`), electron temperature (`Te`), or ion temperature (`Ti`) for specific geospatial and temporal conditions.
- Flexibility between querying with `lat`/`lon` or `UT`/`SLT`
- Efficient batch predictions using vectorized input arrays for higher performance.
- Supports querying geophysical indices from provided datasets.

---


## 🔧 Installation

### Prerequisites

* Python 3.8+
* NumPy
* requests 
* SciKit-Learn 
* Pandas 
* Xarray 
* tqdm 
* SciPy

### Installation
You can install this package via **pip**:

``
pip install MISA_pySLIME
``
---
The model downloads missing dependencies on first import (e.g., the geophysical dataset):
```bash
Downloading MISA dataset from https://www.dropbox.com/...
MISA dataset downloaded and saved to ancillary/processed_ncs/...
Downloading Geophysical Dataset from https://www.dropbox.com/...
Geophysical Dataset downloaded and saved to ancillary/processed_ncs/...
```

If the files already exist locally, the library will skip the download step and use the existing files.

---


## Usage
### 🚀 Quickstart

Here's how you can use the model to predict electron density over 24 hours:

```python
from MISA_pySLIME import predict_ne, predict_ti, predict_te

# Example: predict electron density (Ne) at azimuth=-80°, altitude=350 km,
# DOY=99, UT=12.5 in 2024:
ne = predict_ne(
  doy=99,
  time=12.5,
  year=2024,
  coords=(-80, 350),
  input_coords='az_alt',  # or 'lat_lon'
  time_ref='ut'  # 'slt' or 'ut'
)
print(f"Predicted Ne: {ne:.3e} m⁻³")
```
#### **Batch Predictions**

To predict multiple inputs efficiently, you can pass arrays to `predict_ne`,`predict_te`, or `predict_ti`:

```python
placeholder
```

---

## **Inputs and Parameters**

### **Clamping and Wrapping Input Values**

Set argument `verbose=True` to enable progress bar.

placeholder

---


> All functions are defined in `pySLIME.py`.

* **`get_lat_lon(az, alt)`**
  Convert radar beam geometry (azimuth, altitude) to geographic (latitude, longitude).

* **`get_az_alt(lat, lon)`**
  Inverse mapping: geographic coords → beam (azimuth, altitude).

* **`query_model(az, alt, doy, slt, indices, bin_models, feature_order)`**
  Low‑level engine that selects the correct bin, scales & transforms features, and runs the Ridge regression.

* **`predict_ne(...)`, `predict_ti(...)`, `predict_te(...)`**
  High‑level convenience wrappers loading pre‑trained models for electron density, ion temperature, and electron temperature.

---

## 📁 Project Structure

```text
pySLIME/
├── ancillary/             # Geophysical & grid datasets (netCDF, CSV)
├── model/                 # Pre‑trained model artifacts (.npy)
├── notebooks/             # Example & tutorial Jupyter notebooks
├── pySLIME.py             # Core library functions
├── requirements.txt       # Python dependencies (pip)
├── environment.yml        # Optional: conda environment spec
├── README.md              # This file
├── LICENSE                # Open‑source license
└── .gitignore             # Ignore patterns for git
```

