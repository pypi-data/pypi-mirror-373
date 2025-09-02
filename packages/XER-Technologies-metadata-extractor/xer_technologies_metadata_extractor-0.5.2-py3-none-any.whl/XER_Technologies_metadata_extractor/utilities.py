from typing import List, Sequence
from importlib import resources
from pathlib import Path

import pandas as pd
from scipy import interpolate  # type: ignore[import-untyped]
from scipy.interpolate import RectBivariateSpline  # type: ignore[import-untyped]


PKG_NAME = "XER_Technologies_metadata_extractor"


def _iter_da120_files(base: Path) -> Sequence[Path]:
    """Return *.csv files sorted by throttle value."""
    files = sorted(p for p in base.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No .csv files found in {base}")
    return files


def throttle_function(da120_data_path: str | None = None) -> RectBivariateSpline:
    """
    Create an interpolated throttle function from DA120 data files.

    Args:
        da120_data_path: Path to the DA120 data folder

    Returns:
        RectBivariateSpline: Interpolated throttle function
    """
    if da120_data_path is None:
        # packaged files
        with resources.as_file(
            resources.files(PKG_NAME).joinpath("DA120")
        ) as data_dir:
            csv_paths = _iter_da120_files(data_dir)
    else:
        csv_paths = _iter_da120_files(Path(da120_data_path))

    # 2) Build 2-D grid (rpm rows × throttle columns)
    throttles: List[float] = []
    df_list: List[pd.DataFrame] = []

    for csv_path in csv_paths:
        throttle = float(csv_path.stem.split("_")[2])  # e.g. DA120_50_xxx.csv
        throttles.append(throttle)

        raw = pd.read_csv(csv_path)
        raw["RPM"] = 7.5 / 9 * raw["RPM"] + 1500

        # Function
        f1d = interpolate.interp1d(
            raw["RPM"],
            raw["power"],
            bounds_error=False,
            fill_value=(raw["power"].iloc[0], raw["power"].iloc[-1]),
        )

        max_rpm = int(raw["RPM"].max())
        rpm_index = list(range(3000, max_rpm + 100, 100))
        df_list.append(
            pd.DataFrame({"power": f1d(rpm_index)}, index=rpm_index)
        )

    # merge columns and create 2-D spline
    grid = pd.concat(df_list, axis=1)
    grid.columns = throttles
    grid = grid.fillna(0.0)

    return RectBivariateSpline(
        grid.index.to_numpy(),       # rpm axis
        grid.columns.to_numpy(),     # throttle axis
        grid.values,                 # power matrix
        kx=2, ky=2,
    )