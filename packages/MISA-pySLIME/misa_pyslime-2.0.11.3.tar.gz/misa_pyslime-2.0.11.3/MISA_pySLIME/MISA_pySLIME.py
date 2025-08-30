import numpy as np
import pandas as pd
import xarray as xr
from tqdm import tqdm
from scipy.interpolate import LinearNDInterpolator
from scipy.spatial import cKDTree
import os
import netCDF4

# -- Define paths to large ancillary NetCDFs (downloaded at install/runtime) --
BASE_DIR       = os.path.dirname(__file__)
PROCESSED_DIR  = os.path.join(BASE_DIR, 'ancillary', 'processed_ncs')
MASTER_GEO_PATH = os.path.join(PROCESSED_DIR, 'master_geo_ds_2.0.10.nc')
master_geo_ds  = xr.load_dataset(MASTER_GEO_PATH,engine='netcdf4')

# -- Load geophysical index master dataset --
# -- Load trained binned-regression model dictionaries for Ne, Ti, Te --
MODEL_DIR      = os.path.join(BASE_DIR, 'model')
ne_model_dict = np.load(os.path.join(MODEL_DIR, 'ne_model_2_0_11.npy'), allow_pickle=True).item()
ti_model_dict = np.load(os.path.join(MODEL_DIR, 'ti_model_2_0_10.npy'), allow_pickle=True).item()
te_model_dict = np.load(os.path.join(MODEL_DIR, 'te_model_2_0_10.npy'), allow_pickle=True).item()

# -- Precompute bidirectional interpolators between (az, alt) and (lat, lon) --
GRID_PATH = os.path.join(PROCESSED_DIR, 'grid_ds_2.0.8.nc')
grid_ds   = xr.load_dataset(GRID_PATH)
flat_alt      = grid_ds['gdalt'].values.flatten()
flat_az       = grid_ds['az_normalized'].values.flatten()
flat_gdlat    = grid_ds['gdlat'].values.flatten()
flat_glon     = grid_ds['glon'].values.flatten()
interp_df = pd.DataFrame({
    'az':  flat_az,
    'alt': flat_alt,
    'lat': flat_gdlat,
    'lon': flat_glon
}).dropna()
# forward mapping: (az, alt) -> (lat, lon)
fwd_pts = interp_df[['az', 'alt']].values
lat_vals = interp_df['lat'].values
lon_vals = interp_df['lon'].values
# inverse mapping: (lat, lon) -> (az, alt)
inv_pts = interp_df[['lat', 'lon']].values
az_vals = interp_df['az'].values
alt_vals = interp_df['alt'].values
lat_interpolator = LinearNDInterpolator(fwd_pts, lat_vals)
lon_interpolator = LinearNDInterpolator(fwd_pts, lon_vals)
az_interpolator = LinearNDInterpolator(inv_pts, az_vals)
alt_interpolator = LinearNDInterpolator(inv_pts, alt_vals)
# Build KD-trees for nearest-neighbor fallback
fwd_tree = cKDTree(fwd_pts)  # (az, alt) -> (lat, lon)
inv_tree = cKDTree(inv_pts)  # (lat, lon) -> (az, alt)
# Domain bounds for more informative messages
az_min, az_max = interp_df['az'].min(), interp_df['az'].max()
alt_min, alt_max = interp_df['alt'].min(), interp_df['alt'].max()
lat_min, lat_max = interp_df['lat'].min(), interp_df['lat'].max()
lon_min, lon_max = interp_df['lon'].min(), interp_df['lon'].max()


def get_lat_lon(az, alt, verbose=True):
    az_arr = np.asarray(az)
    alt_arr = np.asarray(alt)
    pts = np.column_stack((az_arr.ravel(), alt_arr.ravel()))

    lat = lat_interpolator(pts)
    lon = lon_interpolator(pts)

    # Identify NaNs and replace with nearest neighbor
    nan_mask = np.isnan(lat) | np.isnan(lon)
    if np.any(nan_mask):
        bad_pts = pts[nan_mask]
        _, idxs = fwd_tree.query(bad_pts)
        nearest_valid = fwd_pts[idxs]
        lat[nan_mask] = lat_interpolator(nearest_valid)
        lon[nan_mask] = lon_interpolator(nearest_valid)
        if verbose:
            print(
                f"[get_lat_lon] {np.sum(nan_mask)} out-of-bounds point(s) detected.\n"
                f"Valid input ranges: az ∈ [{az_min:.2f}, {az_max:.2f}], alt ∈ [{alt_min:.2f}, {alt_max:.2f}].\n"
                f"Nearest valid grid points used instead."
            )

    return lat.reshape(az_arr.shape), lon.reshape(az_arr.shape)


def get_az_alt(lat, lon, verbose=True):
    lat_arr = np.asarray(lat)
    lon_arr = np.asarray(lon)
    pts = np.column_stack((lat_arr.ravel(), lon_arr.ravel()))

    az = az_interpolator(pts)
    alt = alt_interpolator(pts)

    # Identify NaNs and replace with nearest neighbor
    nan_mask = np.isnan(az) | np.isnan(alt)
    if np.any(nan_mask):
        bad_pts = pts[nan_mask]
        _, idxs = inv_tree.query(bad_pts)
        nearest_valid = inv_pts[idxs]
        az[nan_mask] = az_interpolator(nearest_valid)
        alt[nan_mask] = alt_interpolator(nearest_valid)
        if verbose:
            print(
                f"[get_az_alt] {np.sum(nan_mask)} out-of-bounds point(s) detected.\n"
                f"Valid input ranges: lat ∈ [{lat_min:.2f}, {lat_max:.2f}], lon ∈ [{lon_min:.2f}, {lon_max:.2f}].\n"
                f"Nearest valid grid points used instead."
            )
    return az.reshape(lat_arr.shape), alt.reshape(lat_arr.shape)


def query_model(az, alt, doy, slt, indices, bin_models, feature_order=None):
    """
    Generic binned-regression query function.
    """
    az_arr, alt_arr, doy_arr, slt_arr = map(np.atleast_1d, [az, alt, doy, slt])
    for k, v in indices.items():
        indices[k] = np.atleast_1d(v)
    n = az_arr.size
    # default feature order
    if feature_order is None:
        feature_order = ['doy', 'slt'] + sorted(indices.keys())
    # bin centers for fallback
    bin_centers = {key: ((info['az_range'][0] + info['az_range'][1]) / 2,
                         (info['alt_range'][0] + info['alt_range'][1]) / 2)
                   for key, info in bin_models.items()}
    preds = np.full(n, np.nan)
    for i in range(n):
        # exact bin match
        sel = None
        for key, info in bin_models.items():
            az0, az1 = info['az_range'];
            alt0, alt1 = info['alt_range']
            if az0 <= az_arr[i] < az1 and alt0 <= alt_arr[i] < alt1:
                sel = info;
                break
        # nearest fallback
        if sel is None:
            nearest = min(bin_centers, key=lambda k: np.hypot(
                az_arr[i] - bin_centers[k][0], alt_arr[i] - bin_centers[k][1]))
            sel = bin_models[nearest]
        # build features
        fv = []
        for feat in feature_order:
            if feat == 'doy':
                fv.append(doy_arr[i])
            elif feat == 'slt':
                fv.append(slt_arr[i])
                fv.append(np.sin(2 * np.pi * slt_arr[i] / 24))
                fv.append(np.cos(2 * np.pi * slt_arr[i] / 24))
                fv.append(np.sin(4 * np.pi * slt_arr[i] / 24))
                fv.append(np.cos(4 * np.pi * slt_arr[i] / 24))
                fv.append(np.sin(8 * np.pi * slt_arr[i] / 24))
                fv.append(np.cos(8 * np.pi * slt_arr[i] / 24))
            else:
                fv.append(indices[feat][i])
            # check if fv contains nans-1):
            if np.isnan(fv).any():
                raise ValueError(f"Feature {feat} contains NaN values.")
        X = np.array([fv])
        # scale + poly
        Xs = sel['scaler'].transform(X)
        if sel.get('poly') is not None:
            Xs = sel['poly'].transform(Xs)
        preds[i] = sel['model'].predict(Xs)[0]
    return preds[0] if n == 1 else preds


def _prepare_inputs(doy, time, coords, input_coords, time_ref, year=None):
    """
    Helper to convert and wrap inputs for generic prediction.
    """
    doy_arr = np.atleast_1d(doy).astype(float)
    time_arr = np.atleast_1d(time).astype(float)
    coords_arr = np.atleast_2d(coords).astype(float)
    year_arr = np.atleast_1d(year).astype(float)
    if doy_arr.size != coords_arr.shape[0] or time_arr.size != coords_arr.shape[0]:
        raise ValueError(f'Length mismatch among coords, doy, or time\n shapes: {coords_arr.shape}, {doy_arr.shape}, {time_arr.shape}')

    if input_coords == 'az_alt':
        az, alt = coords_arr[:, 0], coords_arr[:, 1]
        lat, lon = get_lat_lon(az, alt)
    else:
        lat, lon = coords_arr[:, 0], coords_arr[:, 1]
        az, alt = get_az_alt(lat, lon)
    # time to slt, ut
    if time_ref == 'slt':
        slt = time_arr; ut = slt - lon / 15.0
    else:
        ut = time_arr; slt = ut + lon / 15.0
    # wrap and adjust doy
    slt_mod = np.mod(slt, 24)
    ut_mod = np.mod(ut, 24)
    doy_arr += ((slt < 0).astype(int) - (slt >= 24).astype(int)
                + (ut < 0).astype(int) - (ut >= 24).astype(int))
    return az, alt, doy_arr, slt_mod, ut_mod


def predict_generic(doy, time, coords, model_dict, target_indices,
                    input_coords='az_alt', time_ref='slt', year=None,
                    geo_ds=master_geo_ds, verbose=False):
    """
    Core prediction routine for ne/ti/te using a binned model dict.
    """
    az, alt, doy_arr, slt, ut = _prepare_inputs(
        doy, time, coords, input_coords, time_ref, year)
    # filter geo data by year
    preds = []
    ds = geo_ds.sel(dates=geo_ds['dates'].dt.year == year) if year else geo_ds
    ds_dates = ds['dates'].dt.dayofyear.values
    for i in tqdm(range(len(az)), disable=not verbose):
        # filter by doy
        mask = ds_dates == doy_arr[i]
        if not mask.any(): raise ValueError(f'No geo data on YEAR {year}, DOY {doy_arr[i]}')
        ds_doy = ds.isel(dates=mask)
        # closest ut
        ut_vals = ds_doy['ut'].values
        idx = np.abs(ut_vals - ut[i]).argmin()
        # build index dict
        idxs = {feat: float(ds_doy[feat].values[idx]) for feat in target_indices}
        preds.append(query_model(az[i], alt[i], doy_arr[i], slt[i], idxs, model_dict,
                                 ['doy', 'slt'] + target_indices))
    out = np.array(preds)
    return out[0] if out.size == 1 else out

# Convenience wrappers
predict_ne = lambda doy, time, coords, **kw: predict_generic(
    doy, time, coords, ne_model_dict, ['fism2_48hr_prior', 'kp_7hr_prior'], **kw)
predict_ti = lambda doy, time, coords, **kw: predict_generic(
    doy, time, coords, ti_model_dict, ['fism2_48hr_prior', 'ap_7hr_prior'], **kw)
predict_te = lambda doy, time, coords, **kw: predict_generic(
    doy, time, coords, te_model_dict, ['fism2_48hr_prior', 'ap_7hr_prior'], **kw)