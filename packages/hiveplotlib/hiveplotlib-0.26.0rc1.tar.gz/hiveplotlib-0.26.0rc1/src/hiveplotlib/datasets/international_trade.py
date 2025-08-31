"""
Tools for working with the international trade dataset from the Harvard Growth Lab.
"""

import json
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

import numpy as np
import pandas as pd


def international_trade_data(
    year: int = 2019, hs92_code: int = 8112, path: Optional[Union[str, Path]] = None
) -> Tuple[pd.DataFrame, Dict]:
    """
    Read in international trade data network from the Harvard Growth Lab.

    .. note::
        Only a limited number of subsets of the data are shipped with ``hiveplotlib``, as each year of trade data is
        roughly 300mb. However, the raw data are available at the
        `Harvard Growth Lab's website <https://doi.org/10.7910/DVN/T4CHWJ>`_, and the runner to produce the necessary
        files to use this reader function is available in the
        `repository <https://gitlab.com/geomdata/hiveplotlib/-/blob/master/runners/make_trade_network_dataset.py>`_
        (``make_trade_network_dataset.py``).

        If you are using the runner to make your own trade datasets that you will read in locally with this
        function, then you will need to specify the local ``path`` accordingly.

    :param year: which year of data to pull. If the year of data is not available, an error will be raised.
    :param hs92_code: which HS 92 code of export data to pull. If the code requested is not available, an error will
        be raised. There are different numbers of digits (e.g. 2, 4), where more digits leads to more specificity of
        trade group. For a reference to what trade groups these codes correspond to, see
        `this resource <https://dataweb.usitc.gov/classification/commodity-description/HTS/4>`_.
    :param path: directory containing both the data and metadata for loading. Default ``None`` assumes you are using one
        of the datasets shipped with ``hiveplotlib``. If you are using the ``make_trade_network_dataset.py``
        runner discussed above to make your own datasets, then you will need to specify the path to the directory where
        you saved both the data and metadata files (which must be in the same directory).
    :return: ``pandas.DataFrame`` of trade data, dictionary of metadata explaining meaning of data's columns,
        data provenance, citations, etc.
    :raises: ``AssertionError`` if the requested files cannot be found.
    """
    # path when grabbing files shipped with hiveplotlib
    internal_path = Path(__file__).parent.joinpath("trade_data_harvard_growth_lab")

    path = internal_path if path is None else Path(path)

    # grab the shipped year, hs92 values to present what's available on failure
    csv_files = [
        i.stem for i in sorted(internal_path.glob("international_exports*.csv"))
    ]
    csv_years = [i.split("_")[2] for i in csv_files]
    csv_hs92 = [i.split("_")[-1] for i in csv_files]
    hiveplotlib_supported_values = pd.DataFrame(
        np.c_[csv_years, csv_hs92], columns=["Year", "Trade Code"]
    )

    # check that our implied data and metadata files exist
    data_path = path.joinpath(f"international_exports_{year}_{hs92_code}.csv")
    metadata_path = path.joinpath(
        f"international_exports_metadata_{year}_{hs92_code}.json"
    )

    if not (data_path.exists() and metadata_path.exists()):
        raise ValueError(
            "Could not find data and / or metadata under specified `path`. If you specified your own path, double "
            "check that the path is correct. Your file names should be "
            "If you are using `hiveplotlib` supported data, note that only the following `year`, "
            f"`hs29_code` values are supported:\n{hiveplotlib_supported_values}"
        )

    data = pd.read_csv(data_path)
    with open(metadata_path, "r") as openfile:
        metadata = json.load(openfile)

    return data, metadata
