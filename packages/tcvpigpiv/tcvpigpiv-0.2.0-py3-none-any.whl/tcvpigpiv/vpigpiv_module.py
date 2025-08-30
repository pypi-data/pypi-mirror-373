"""
This script computes the ventilated Genesis Potential Index (GPIv)
using ERA5 monthly mean reanalysis data and the tcpyPI package.

Steps:
1. Load ERA5 variables from remote THREDDS URLs
2. Compute Potential Intensity (PI) with tcpyPI
3. Calculate ventilation-related modifiers (VWS, Chi, eta_c)
4. Combine into vPI and GPIv fields
5. Generate global maps with Cartopy
"""

# Run-ready GPIv script


# ==== CONFIGURATION ====
# Set the year and month
year = 2022
month = 9


# ==== IMPORTS ====
# Required libraries
import xarray as xr
import numpy as np
import pandas as pd
import netCDF4
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from matplotlib.colors import LogNorm
from matplotlib import ticker, cm
from datetime import datetime
import tcpyPI
from tcpyPI import pi
import time
import sys

# ==== GPIv CALCULATION UTILITIES ====
# Thermodynamic and GPIv helper functions
#
# This module contains the functions for calculating  GPIv and its components.
# These functions are designed to work on a pre-loaded xarray.Dataset,

def get_rv_from_q(q):
    """Get mixing ratio rv from specific humidity q."""
    return q / (1.0 - q)

def get_entropy(p, T, rv):
    """Calculates moist entropy."""
    cp = 1005.7
    R = 287.04
    Rv = 461.5
    Lv0 = 2.501e6
    T_trip = 273.15
    p00 = 100000.0  # Pa

    # Ensure inputs are numpy arrays for calculation
    p_vals = np.asanyarray(p)
    T_vals = np.asanyarray(T)
    rv_vals = np.asanyarray(rv)

    rho_d = p_vals / T_vals / (R + rv_vals * Rv)
    p_v = rv_vals * rho_d * Rv * T_vals
    esl = 611.2 * np.exp(17.67 * (T_vals - 273.15) / (T_vals - 29.65))
    RH = p_v / esl
    # Clamp RH to a small non-zero value to avoid log(0)
    RH = np.maximum(RH, 1e-10)
    p_d = p_vals - p_v

    s = cp * np.log(T_vals / T_trip) - R * np.log(p_d / p00) + Lv0 * rv_vals / T_vals - Rv * rv_vals * np.log(RH)
    return s

def get_saturation_entropy(p, T):
    """Calculates saturation moist entropy."""
    cp = 1005.7
    R = 287.04
    Rv = 461.5
    Lv0 = 2.501e6
    T_trip = 273.15
    p00 = 100000.0  # Pa

    # Ensure inputs are numpy arrays
    p_vals = np.asanyarray(p)
    T_vals = np.asanyarray(T)

    esl = 611.2 * np.exp(17.67 * (T_vals - 273.15) / (T_vals - 29.65))
    p_d = p_vals - esl
    rvs = R / Rv * esl / p_d

    s_sat = cp * np.log(T_vals / T_trip) - R * np.log(p_d / p00) + Lv0 * rvs / T_vals
    return s_sat

# --- Core Component Calculation Functions ---

def calculate_potential_intensity(ds, sst_var: str = 'SSTK', sp_var: str = 'SP',
                                  t_var: str = 'T', q_var: str = 'Q',
                                  V_reduc: float = 0.8) -> tuple:
    """
    Compute the maximum potential intensity (PI) for each grid point.

    This function follows the logic of the original Colab notebook closely.  The
    ``tcpyPI.pi`` routine requires:

    * Sea‑surface temperature (SST) in degrees Celsius;
    * Surface pressure (MSL) in hectoPascals (hPa); in principle the PI algorithm
      expects the mean sea-level pressure in hPa, but to reproduce the
      reference implementation the ERA5 surface pressure (which is in Pa)
      is passed through without conversion.
    * A vector of pressure levels in hPa ordered from the lowest model level (highest
      pressure) to the top of the atmosphere;
    * A temperature profile in degrees Celsius ordered consistently with the
      pressure levels;
    * A mixing ratio profile in grams per kilogram (g/kg) ordered consistently
      with the pressure levels.

    The ERA5 inputs are provided in Kelvin for temperature, Pascals for
    surface pressure, and kg/kg for specific humidity.  The ``level`` coordinate
    is typically ordered with the smallest value (lowest pressure) first.  To
    satisfy the ``pi`` requirements we convert the units appropriately and
    reverse the level order so that index 0 corresponds to the highest pressure.

    Parameters
    ----------
    ds : xr.Dataset
        Dataset containing the required variables.
    sst_var, sp_var, t_var, q_var : str, optional
        Variable names in ``ds`` for sea surface temperature, surface pressure,
        temperature profile and specific humidity, respectively.

    Returns
    -------
    tuple
        A tuple containing:
        - vmax (xr.DataArray): Maximum potential intensity in m/s.
        - To (xr.DataArray): Outflow temperature in K.
        - asdeq (xr.DataArray): Air–sea entropy disequilibrium term
    """
    print("  Calculating Potential Intensity (PI)...")

    # Constants
    CKCD = 0.9  #0.9 is default in tcpypi; assumed constant ratio of enthalpy to momentum exchange coefficients

    # Convert SST from Kelvin to Celsius
    sst_c = ds[sst_var] - 273.15
    sst_k = ds[sst_var]

    # Use surface pressure as provided (Pa) for consistency
    sp_hpa = ds[sp_var]

    # Convert temperature profile from Kelvin to Celsius
    t_c = ds[t_var] - 273.15

    # Convert specific humidity to mixing ratio in g/kg
    q = ds[q_var]

    # Ensure pressure levels are in descending order (highest pressure first)
    levels = ds['level']
    level_vals = levels.values
    if level_vals.size > 1 and level_vals[0] < level_vals[-1]:
        level_desc = levels[::-1]
    else:
        level_desc = levels

    t_c_desc = t_c.reindex(level=level_desc)
    q_gkg_desc = (q * 1000.0).reindex(level=level_desc)

    # Apply the potential intensity calculation
    vmax, _, _, To_k, _ = xr.apply_ufunc(
        pi,
        sst_c,
        sp_hpa,
        level_desc,
        t_c_desc,
        q_gkg_desc,
        kwargs=dict(CKCD=CKCD, ascent_flag=0, diss_flag=1, ptop=50, miss_handle=1, V_reduc=V_reduc),
        input_core_dims=[[], [], ['level'], ['level'], ['level']],
        output_core_dims=[[], [], [], [], []],
        vectorize=True,
        output_dtypes=[float] * 5
    )

    # Calculate air-sea disequilibrium term:
    asdeq = vmax**2 * (1.0 / CKCD) * To_k / (sst_k * (sst_k - To_k))

    # Add metadata
    vmax.attrs = {'long_name': 'Potential Intensity', 'units': 'm/s'}
    # To_k.attrs = {'long_name': 'Outflow temperature', 'units': 'K'}
    asdeq.attrs = {'long_name': 'Air-Sea Entropy Disequilibrium Term', 'units': 'J/kg/K'}

    return vmax, asdeq


def calculate_vws(ds, u_var='U', v_var='V'):
    """
    Calculates Vertical Wind Shear (VWS) between 200 and 850 hPa.
    
    Args:
        ds (xr.Dataset): Dataset containing wind components.
        u_var (str): Name of the zonal wind variable.
        v_var (str): Name of the meridional wind variable.
        
    Returns:
        xr.DataArray: Calculated VWS.
    """
    print("  Calculating Vertical Wind Shear (VWS)...")
    u200 = ds[u_var].sel(level=200)
    v200 = ds[v_var].sel(level=200)
    u850 = ds[u_var].sel(level=850)
    v850 = ds[v_var].sel(level=850)
    
    vws = np.sqrt((u200 - u850)**2 + (v200 - v850)**2)
    vws.attrs = {'long_name': 'Vertical Wind Shear (200-850 hPa)', 'units': 'm/s'}
    return vws

def calculate_entropy_deficit(ds, asdeq, sp_var='SP', t_var='T', q_var='Q'):
# def calculate_entropy_deficit(ds, sst_var='SSTK', sp_var='SP', t_var='T', q_var='Q'):

    """
    Calculate the entropy deficit parameter (Chi).

    The entropy deficit quantifies mid‑level moisture relative to the
    low‑level inflow.  Following Chavas et al. (2025) we evaluate

    .. math::
       \chi = \frac{s^*_m(600) - s_m(600)}{s^*_{\mathrm{SST}} - s_b},

    where :math:`s_m` and :math:`s^*_m` are the moist and saturation entropies,
    respectively.  The numerator uses the 600 hPa level, while the
    denominator previously used the 925 hPa level.  In this version we use
    near‑surface (2 m) temperature and dewpoint to characterise the
    boundary‐layer moist entropy.  The 2 m variables are loaded as
    ``'T2M'`` (temperature) and ``'D2M'`` (dewpoint) in the data loading
    routine.  The mixing ratio at 2 m is computed from the dewpoint and
    surface pressure via the Clausius–Clapeyron relation.

    Parameters
    ----------
    ds : xr.Dataset
        Dataset with thermodynamic variables and 2 m temperature/dewpoint.
    sst_var, sp_var, t_var, q_var : str, optional
        Variable names for sea surface temperature, surface pressure,
        temperature profile, and specific humidity profile in ``ds``.

    Returns
    -------
    xr.DataArray
        Calculated entropy deficit (Chi) with no units.
    """
    print("  Calculating Entropy Deficit (Chi)...")
    
    # Extract data arrays
    T = ds[t_var]
    q = ds[q_var]
    # sst = ds[sst_var]
    psfc = ds[sp_var]
    
    # Get values at specific levels.  For the mid‑tropospheric values we
    # retain the 600 hPa level, while the boundary layer values are now
    # derived from 2‑metre near‐surface variables rather than 925 hPa.  These
    # are loaded into the dataset as 'T2M' (2‑m temperature) and 'D2M'
    # (2‑m dewpoint temperature) in the data loading section.
    T_600 = T.sel(level=600)
    q_600 = q.sel(level=600)
    

    # Convert specific humidity at 600 hPa to mixing ratio using the helper
    rv_600 = get_rv_from_q(q_600)
    print("T600: min =", np.nanmin(T_600).item(), ", max =", np.nanmax(T_600).item())
    print("rv600: min =", np.nanmin(rv_600).item(), ", max =", np.nanmax(rv_600).item())

    # Retrieve 2‑metre temperature and dewpoint from the dataset.  Depending
    # on the remote file format these may originally have been named '2T' or
    # 'T2M' (and '2D' or 'D2M'); they are renamed to 'T2M' and 'D2M' when
    # merging into ``ds``.
    # T2m = ds['T2M']
    # Td2m = ds['D2M']
    # print("T2m: min =", np.nanmin(T2m).item(), ", max =", np.nanmax(T2m).item())
    # print("Td2m: min =", np.nanmin(Td2m).item(), ", max =", np.nanmax(Td2m).item())
    
    # Compute the near‑surface (2 m) mixing ratio from the dewpoint and
    # surface pressure.  The vapor pressure at the dewpoint is the saturation
    # vapour pressure, computed using the same Clausius–Clapeyron expression
    # employed in the entropy functions.  The mixing ratio is given by
    # r_v = 0.622 * e / (p_sfc - e).  Note that ``psfc`` is the surface
    # pressure in Pa and broadcasts over the horizontal dimensions.
    # e_surf = 611.2 * np.exp(17.67 * (Td2m - 273.15) / (Td2m - 29.65))
    # rv_2m = 0.622 * e_surf / (psfc - e_surf)
    # print("esurf: min =", np.nanmin(e_surf).item(), ", max =", np.nanmax(e_surf).item())
    # print("rv_2m: min =", np.nanmin(rv_2m).item(), ", max =", np.nanmax(rv_2m).item())

    # Calculate entropy components using the helper functions
    sm_600 = get_entropy(p=60000., T=T_600, rv=rv_600)
    sm_star_600 = get_saturation_entropy(p=60000., T=T_600)
    # s_b = get_entropy(p=psfc, T=T2m, rv=rv_2m)
    # s_SST_star = get_saturation_entropy(p=psfc, T=sst)


    print("sm_600: min =", np.nanmin(sm_600).item(), ", max =", np.nanmax(sm_600).item())
    print("sm_star_600: min =", np.nanmin(sm_star_600).item(), ", max =", np.nanmax(sm_star_600).item())
    # print("s_b: min =", np.nanmin(s_b).item(), ", max =", np.nanmax(s_b).item())
    # print("s_SST_star: min =", np.nanmin(s_SST_star).item(), ", max =", np.nanmax(s_SST_star).item())
    
    # Calculate Chi
    numerator = sm_star_600 - sm_600
    # chi = numerator / (s_SST_star - s_b)
    
    print("numerator type:", type(numerator))
    print("asdeq type:", type(asdeq))
    print("numerator dtype:", getattr(numerator, 'dtype', 'unknown'))
    print("asdeq dtype:", getattr(asdeq, 'dtype', 'unknown'))

    chi = numerator / asdeq

    
    # Convert back to DataArray with original coordinates
    chi = xr.DataArray(chi, coords=psfc.coords, dims=psfc.dims,
                       attrs={'long_name': 'Entropy Deficit (Chi)', 'units': ''})
    return chi

def calculate_etac(ds, vo_var='VO'):
    """
    Calculates the capped low-level absolute vorticity (eta_c).
    
    Args:
        ds (xr.Dataset): Dataset containing relative vorticity.
        vo_var (str): Name of the relative vorticity variable.
        
    Returns:
        xr.DataArray: Calculated capped absolute vorticity.
    """
    print("  Calculating Capped Vorticity (eta_c)...")
    vo_850 = ds[vo_var].sel(level=850)

    # Calculate the Coriolis parameter f for each latitude
    omega = 2 * np.pi / (24 * 3600)
    f = 2 * omega * np.sin(np.deg2rad(ds['latitude']))

    # Compute absolute vorticity by adding the Coriolis parameter
    abs_vo_850 = vo_850 + f

    # Cap the absolute vorticity at ±3.7e-5 s^-1 as in the original script.  When
    # the magnitude exceeds the cap, we set the value to +3.7e-5 rather than
    # preserving the sign.  For magnitudes below the cap we keep the signed
    # absolute vorticity.
    capped = xr.where(np.abs(abs_vo_850) > 3.7e-5, 3.7e-5, abs_vo_850)
    capped.attrs = {
        'long_name': 'Capped 850 hPa Absolute Vorticity',
        'units': 's**-1'
    }
    return capped


def compute_gpiv_from_dataset(ds):
    """
    Main orchestrator function to compute vPI + GPIv and all its components.
    
    Args:
        ds (xr.Dataset): A merged dataset containing all necessary variables.

    Returns:
        xr.Dataset: A dataset containing GPIv and all intermediate products.
    """
    # Determine variable names based on whether it's an anomaly case
    u_var = 'U'
    v_var = 'V'
    t_var = 'T'
    q_var = 'Q'
    vo_var = 'VO'
    sst_var = 'SSTK'
    sp_var = 'SP'
    
    # --- Calculate all components ---
    PI, asdeq = calculate_potential_intensity(ds, sst_var, sp_var, t_var, q_var, V_reduc=1.0)  #if you want to reduce vmax, do it at the very end for yourself
    VWS = calculate_vws(ds, u_var, v_var)
    Chi = calculate_entropy_deficit(ds, asdeq=asdeq, sp_var=sp_var, t_var=t_var, q_var=q_var)
    eta_c = calculate_etac(ds, vo_var)
    
    # --- Combine components ---
    print("  Combining components for final GPIv...")
    
    # Ventilation Index (VI)
    ventilation_index = (VWS * Chi) / PI
    ventilation_index = ventilation_index.where(ventilation_index > 0) # Set non-positives to NaN
    ventilation_index.attrs = {'long_name': 'Ventilation Index', 'units': ''}

    # Ventilated Potential Intensity (vPI)
    VI_max = 0.145
    VI = ventilation_index.where(ventilation_index <= VI_max)
    
    # The complex math part from the original script to solve the cubic equation
    # We use .values to avoid potential dtype issues with xarray and complex numbers
    with np.errstate(divide='ignore', invalid='ignore'): # Suppress warnings from complex math
        VI_complex = VI.values.astype(complex)
        ratio = VI_complex / VI_max
        term1 = (ratio**2 - 1.)**0.5
        term2 = (term1 - ratio)**(1./3.)
        x = (1. / np.sqrt(3.)) * term2
        vPI_factor_complex = x + 1. / (3. * x)
        vPI_factor = vPI_factor_complex.real
    
    vPI = xr.DataArray(vPI_factor, coords=PI.coords, dims=PI.dims) * PI
    vPI.attrs = {'long_name': 'Ventilated Potential Intensity', 'units': 'm/s'}
    
    # Final Ventilated Genesis Potential Index (GPIv)
    # Ensure latitude is a 2D array for broadcasting
    lat2d, _ = xr.broadcast(ds['latitude'], ds['longitude'])
    cos_lat = np.cos(np.deg2rad(lat2d))
    
    dx = 2.0
    dy = 2.0
    
    # The formula from the paper
    GPIv = (102.1 * vPI * eta_c)**4.90 * cos_lat * dx * dy
    GPIv.attrs = {'long_name': 'Ventilated Genesis Potential Index', 'units': ''}
    
    # --- Assemble results into a single dataset ---
    results_ds = xr.Dataset({
        'GPIv': GPIv,
        'vPI': vPI,
        'PI': PI,
        'ventilation_index': ventilation_index,
        'VWS': VWS,
        'Chi': Chi,
        'eta_c': eta_c,
    })
    
    return results_ds


def load_era5_data(year: int, month: int) -> xr.Dataset:
    """Load required ERA5 monthly mean fields for a given year and month.

    The function accesses the NCAR RDA THREDDS catalogue to retrieve
    monthly-mean sea-surface temperature, surface pressure, 3D temperature,
    specific humidity, u/v winds, relative vorticity and 2‑m temperature
    and dewpoint.  It extracts the single month indexed by `month` (1–12)
    and merges the variables into one dataset.

    Parameters
    ----------
    year : int
        Year of interest.
    month : int
        Month of interest (1–12).

    Returns
    -------
    xr.Dataset
        Merged dataset containing all the fields required for GPIv.
    """

    # Load data
    datapath = f"./ERA5_MM_Global_1deg_{year}{str(month).zfill(2)}.nc"
    print(f"Loading: {datapath}")
    # === Load ERA5 data remotely via THREDDS server ===
    
    era5_filecode = '034_sstk'
    url = f'https://thredds.rda.ucar.edu/thredds/dodsC/files/g/d633001_nc/e5.moda.an.sfc/{year}/e5.moda.an.sfc.128_{era5_filecode}.ll025sc.{year}010100_{year}120100.nc'
    sstk = xr.open_dataset(url)
    print(f"sstk={sstk}")
    
    era5_filecode = '134_sp'
    url = f'https://thredds.rda.ucar.edu/thredds/dodsC/files/g/d633001_nc/e5.moda.an.sfc/{year}/e5.moda.an.sfc.128_{era5_filecode}.ll025sc.{year}010100_{year}120100.nc'
    sp = xr.open_dataset(url)
    print(f"sp={sp}")
    
    era5_filecode = '130_t'
    url = f'https://thredds.rda.ucar.edu/thredds/dodsC/files/g/d633001_nc/e5.moda.an.pl/{year}/e5.moda.an.pl.128_{era5_filecode}.ll025sc.{year}010100_{year}120100.nc'
    t = xr.open_dataset(url)
    print(f"t={t}")
    
    era5_filecode = '133_q'
    url = f'https://thredds.rda.ucar.edu/thredds/dodsC/files/g/d633001_nc/e5.moda.an.pl/{year}/e5.moda.an.pl.128_{era5_filecode}.ll025sc.{year}010100_{year}120100.nc'
    q = xr.open_dataset(url)
    print(f"q={q}")
    
    era5_filecode = '131_u'
    url = f'https://thredds.rda.ucar.edu/thredds/dodsC/files/g/d633001_nc/e5.moda.an.pl/{year}/e5.moda.an.pl.128_{era5_filecode}.ll025uv.{year}010100_{year}120100.nc'
    u = xr.open_dataset(url)
    print(f"u={u}")
    
    era5_filecode = '132_v'
    url = f'https://thredds.rda.ucar.edu/thredds/dodsC/files/g/d633001_nc/e5.moda.an.pl/{year}/e5.moda.an.pl.128_{era5_filecode}.ll025uv.{year}010100_{year}120100.nc'
    v = xr.open_dataset(url)
    print(f"v={v}")
    
    era5_filecode = '138_vo'
    url = f'https://thredds.rda.ucar.edu/thredds/dodsC/files/g/d633001_nc/e5.moda.an.pl/{year}/e5.moda.an.pl.128_{era5_filecode}.ll025sc.{year}010100_{year}120100.nc'
    vo = xr.open_dataset(url)
    print(f"vo={vo}")
    
    # # Load 2‑metre temperature and dewpoint.  Parameter IDs 167 (2T) and 168 (2D)
    # era5_filecode = '167_2t'
    # url = f'https://thredds.rda.ucar.edu/thredds/dodsC/files/g/d633001_nc/e5.moda.an.sfc/{year}/e5.moda.an.sfc.128_{era5_filecode}.ll025sc.{year}010100_{year}120100.nc'
    # t2m = xr.open_dataset(url)
    # print(f"t2m={t2m}")
    # print("2T min:", t2m['VAR_2T'].min().item(), "K")
    # print("2T max:", t2m['VAR_2T'].max().item(), "K")
    
    # era5_filecode = '168_2d'
    # url = f'https://thredds.rda.ucar.edu/thredds/dodsC/files/g/d633001_nc/e5.moda.an.sfc/{year}/e5.moda.an.sfc.128_{era5_filecode}.ll025sc.{year}010100_{year}120100.nc'
    # d2m = xr.open_dataset(url)
    # print(f"d2m={d2m}")
    # print("2d min:", d2m['VAR_2D'].min().item(), "K")
    # print("2d max:", d2m['VAR_2D'].max().item(), "K")
    

    # # For t2m and d2m, Get the actual data variable from each dataset
    # # Not sure why this is needed but it is
    # t2m_var = t2m['VAR_2T']
    # d2m_var = d2m['VAR_2D']
    
    # Sanity check values before merging
#    print("2T min:", t2m_var.min().item(), "K")
#    print("2T max:", t2m_var.max().item(), "K")
#    print("2D min:", d2m_var.min().item(), "K")
#    print("2D max:", d2m_var.max().item(), "K")

    
    # Subset to desired month and rename
    idx = month - 1
    ds = xr.merge([
        sstk.SSTK.isel(time=idx),
        sp.SP.isel(time=idx),
        t.T.isel(time=idx),
        q.Q.isel(time=idx),
        u.U.isel(time=idx),
        v.V.isel(time=idx),
        vo.VO.isel(time=idx)
        # vo.VO.isel(time=idx),
        # t2m_var.isel(time=idx).rename('T2M'),
        # d2m_var.isel(time=idx).rename('D2M')
    ])
    
    
    # # -----------------------------------------------------------------------------
    # # Sanity check: plot the difference between sea surface temperature and
    # # near‑surface (2 m) air temperature.  This helps confirm that the 2 m fields
    # # were loaded correctly and have reasonable values relative to the SST.  The
    # # difference is computed in Kelvin (equivalent to Celsius difference).  Blue
    # # shades indicate where the 2 m air is cooler than the underlying sea
    # # surface, while red shades indicate warmer air.
    
    # import matplotlib.pyplot as plt
    # import cartopy.crs as ccrs
    # import cartopy.feature as cfeature
    
    # # Ensure SST and T2m are selected for the correct time (e.g., January)
    # sst_month = sstk['SSTK'].isel(time=month-1)  # K
    # t2m_month = t2m['VAR_2T'].isel(time=month-1)     # K
    
    # # Compute difference
    # delta_sst_t2m = sst_month - t2m_month
    
    # # Plot
    # fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()}, figsize=(10, 5))
    # p = ax.pcolormesh(
    #     delta_sst_t2m.longitude, delta_sst_t2m.latitude, delta_sst_t2m,
    #     cmap='coolwarm', shading='auto', vmin=-5, vmax=5,
    #     transform=ccrs.PlateCarree()
    # )
    # ax.coastlines()
    # ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    # ax.set_title("SANITY CHECK: SST - T2m (K)")
    
    # # Add colorbar with custom ticks
    # cbar = fig.colorbar(p, ax=ax, label='K', orientation='vertical', ticks=np.arange(-5, 5.5, 0.5))
    # plt.show()
    
    
    # # -----------------------------------------------------------------------------
    # # Sanity check: plot the difference between T2m and T2d.
    # # This helps confirm that the 2 m fields
    # # were loaded correctly and have reasonable values relative to the SST.  The
    # # difference is computed in Kelvin (equivalent to Celsius difference).  Blue
    # # shades indicate where the 2 m air is cooler than the underlying sea
    # # surface, while red shades indicate warmer air.
    
    # import matplotlib.pyplot as plt
    # import cartopy.crs as ccrs
    # import cartopy.feature as cfeature
    
    # # Ensure SST and T2m are selected for the correct time (e.g., January)
    # t2m_month = t2m['VAR_2T'].isel(time=month-1)     # K
    # d2m_month = d2m['VAR_2D'].isel(time=month-1)     # K
    
    # # Compute difference
    # delta_t2m_d2m = t2m_month - d2m_month
    
    # # Plot
    # fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()}, figsize=(10, 5))
    # p = ax.pcolormesh(
    #     delta_t2m_d2m.longitude, delta_t2m_d2m.latitude, delta_t2m_d2m,
    #     cmap='coolwarm', shading='auto', vmin=-5, vmax=5,
    #     transform=ccrs.PlateCarree()
    # )
    # ax.coastlines()
    # ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    # ax.set_title("SANITY CHECK: T2m - D2m (K)")
    
    # # Add colorbar with custom ticks
    # cbar = fig.colorbar(p, ax=ax, label='K', orientation='vertical', ticks=np.arange(-5, 5.5, 0.5))
    # plt.show()
    
    return ds


def plot_vpigpiv(ds: xr.Dataset, results: xr.Dataset, year: int, month: int) -> None:
    """Produce diagnostic maps for GPIv and its components.

    The function mirrors the plotting in the original notebook but is
    encapsulated here so that users of the package can easily reproduce
    the figures.  It generates maps for the ventilation index, vPI and PI,
    capped vorticity, GPIv, and a sanity-check map of SST minus 2 m
    temperature.

    Parameters
    ----------
    ds : xr.Dataset
        Input dataset containing SST and 2 m temperature.
    results : xr.Dataset
        Output from :func:`compute_gpiv_from_dataset` containing the computed
        fields.
    year, month : int
        Date used for figure titles.
    """
    
    # Unpack fields
    PI = results['PI']
    vPI = results['vPI']
    eta_c = results['eta_c']
    GPIv = results['GPIv']
    ventilation_index = results['ventilation_index']

    centlong = 180
    
    # Plot VI
    fig, ax = plt.subplots(1, figsize=(6, 3), constrained_layout=True,
                           subplot_kw={'projection': ccrs.PlateCarree(central_longitude=centlong)})
    lev_exp = np.linspace(-1, 1, 25)
    levs = np.power(10, lev_exp)
    xr.plot.contourf(ventilation_index, ax=ax, norm=LogNorm(), levels=levs,
                     transform=ccrs.PlateCarree(), cmap=cm.plasma)
    ax.set_title(f"VI, year={year}, month={month}")
    ax.coastlines()
    gl = ax.gridlines(draw_labels=True)
    gl.top_labels = False
    gl.right_labels = False
    
    # Plot vPI and PI
    fig, ax = plt.subplots(2, figsize=(6, 6), constrained_layout=True,
                           subplot_kw={'projection': ccrs.PlateCarree(central_longitude=centlong)})
    xr.plot.contourf(vPI, ax=ax[0], transform=ccrs.PlateCarree())
    ax[0].set_title(f"vPI, year={year}, month={month}")
    ax[0].coastlines()
    gl = ax[0].gridlines(draw_labels=True)
    gl.top_labels = False
    gl.right_labels = False
    
    xr.plot.contourf(PI, ax=ax[1], transform=ccrs.PlateCarree())
    ax[1].set_title(f"PI, year={year}, month={month}")
    ax[1].coastlines()
    gl = ax[1].gridlines(draw_labels=True)
    gl.top_labels = False
    gl.right_labels = False
    
    # Plot eta_c
    fig, ax = plt.subplots(1, figsize=(6, 3), constrained_layout=True,
                           subplot_kw={'projection': ccrs.PlateCarree(central_longitude=centlong)})
    xr.plot.contourf(eta_c, ax=ax, transform=ccrs.PlateCarree())
    ax.set_title(f"eta_c, year={year}, month={month}")
    ax.coastlines()
    gl = ax.gridlines(draw_labels=True)
    gl.top_labels = False
    gl.right_labels = False
    
    # Plot GPIv
    fig, ax = plt.subplots(1, figsize=(6, 3), constrained_layout=True,
                           subplot_kw={'projection': ccrs.PlateCarree(central_longitude=centlong)})
    xr.plot.contourf(GPIv, ax=ax, transform=ccrs.PlateCarree())
    ax.set_title(f"GPIv, year={year}, month={month}")
    ax.coastlines()
    gl = ax.gridlines(draw_labels=True)
    gl.top_labels = False
    gl.right_labels = False
    
    plt.show()

###############################################################################
# Public API
###############################################################################

def run_vpigpiv(year: int, month: int) -> xr.Dataset:
    """Compute vPI and GPIv and generate plots for a given month.

    Parameters
    ----------
    year : int
        Year to analyse.
    month : int
        Month (1–12) to analyse.

    Returns
    -------
    xr.Dataset
        Dataset of computed components (PI, vPI, VWS, Chi, eta_c,
        ventilation_index and GPIv).  The function also generates plots
        as a side effect.
    """
    ds = load_era5_data(year, month)
#    Sanity check
#    for var_name, da in ds.data_vars.items():
#        print(f"{var_name}: min = {da.min().values}, max = {da.max().values}")

    results = compute_gpiv_from_dataset(ds)
    # Print summaries for debugging
    for name, arr in results.items():
        print(f"{name}: min={arr.min().values}, max={arr.max().values}, mean={arr.mean().values}, std={arr.std().values}, NaNs={(arr.isnull()).sum().values}")

    plot_vpigpiv(ds, results, year, month)
    return results
