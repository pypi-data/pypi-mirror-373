"""
Test script for the ``vpigpiv_module`` package.

This script demonstrates how to call :func:`run_vpigpiv` with user-defined
year and month values, compute the ventilated Genesis Potential Index
and its components, and summarise the results.  By default it uses
September 2022 as a test case, but you can modify ``YEAR`` and
``MONTH`` below to compute any other monthly mean.

The script adjusts the Python path so that either the installed
``tcvpigpiv`` package or a top-level ``vpigpiv_module.py`` can be imported.
"""

# -----------------------------------------------------------------------------
# User-defined inputs
YEAR = 2022
MONTH = 9
# -----------------------------------------------------------------------------

import os
import sys
import numpy as np  # needed for summary statistics

# Add the project root to Python path so that we can import tcvpigpiv modules
PACKAGE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, PACKAGE_ROOT)

# Try importing run_vgpi from the packaged location; fall back to the top level
try:
    from tcvpigpiv.vpigpiv_module import run_vpigpiv  # type: ignore
except ImportError:
    from vpigpiv_module import run_vpigpiv  # type: ignore


def main() -> None:
    print(f"Running vPI + GPIv computation for {YEAR:04d}-{MONTH:02d}...")
    results = run_vpigpiv(YEAR, MONTH)
    # Print summary statistics for each computed field
    for name, arr in results.items():
        arr_np = arr.values
        print(f"{name}: min={np.nanmin(arr_np):.3f}, max={np.nanmax(arr_np):.3f}, "
              f"mean={np.nanmean(arr_np):.3f}, std={np.nanstd(arr_np):.3f}")

if __name__ == '__main__':
    main()
