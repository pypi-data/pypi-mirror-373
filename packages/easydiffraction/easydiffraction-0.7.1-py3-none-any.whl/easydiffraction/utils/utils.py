# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

"""
General utilities and helpers for easydiffraction.
"""

import importlib
import io
import json
import os
import re
import urllib.request
import zipfile
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version
from typing import List
from urllib.parse import urlparse

import numpy as np
import pandas as pd
import pooch
from packaging.version import Version
from tabulate import tabulate

try:
    import IPython
    from IPython.display import HTML
    from IPython.display import display
except ImportError:
    IPython = None

from easydiffraction.utils.formatting import error
from easydiffraction.utils.formatting import paragraph
from easydiffraction.utils.formatting import warning


def _validate_url(url: str) -> None:
    """Validate that a URL uses only safe HTTP/HTTPS schemes.

    Args:
        url: The URL to validate.

    Raises:
        ValueError: If the URL scheme is not HTTP or HTTPS.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        raise ValueError(f"Unsafe URL scheme '{parsed.scheme}'. Only HTTP and HTTPS are allowed.")


# Single source of truth for the data repository branch.
# This can be overridden in CI or development environments.
DATA_REPO_BRANCH = (
    os.environ.get('CI_BRANCH')  # CI/dev override
    or 'master'  # Default branch for the data repository
)


def download_from_repository(
    file_name: str,
    branch: str | None = None,
    destination: str = 'data',
    overwrite: bool = False,
) -> None:
    """Download a data file from the EasyDiffraction repository on GitHub.

    Args:
        file_name: The file name to fetch (e.g., "NaCl.gr").
        branch: Branch to fetch from. If None, uses DATA_REPO_BRANCH.
        destination: Directory to save the file into (created if missing).
        overwrite: Whether to overwrite the file if it already exists. Defaults to False.

    Returns:
        None
    """
    file_path = os.path.join(destination, file_name)
    if os.path.exists(file_path):
        if not overwrite:
            print(warning(f"File '{file_path}' already exists and will not be overwritten."))
            return
        else:
            print(warning(f"File '{file_path}' already exists and will be overwritten."))
            os.remove(file_path)

    base = 'https://raw.githubusercontent.com'
    org = 'easyscience'
    repo = 'diffraction-lib'
    branch = branch or DATA_REPO_BRANCH  # Use the global branch variable if not provided
    path_in_repo = 'tutorials/data'
    url = f'{base}/{org}/{repo}/refs/heads/{branch}/{path_in_repo}/{file_name}'

    pooch.retrieve(
        url=url,
        known_hash=None,
        fname=file_name,
        path=destination,
    )


def package_version(package_name: str) -> str | None:
    """
    Get the installed version string of the specified package.

    Args:
        package_name (str): The name of the package to query.

    Returns:
        str | None: The raw version string (may include local part, e.g., '1.2.3+abc123'),
        or None if the package is not installed.
    """
    try:
        return version(package_name)
    except PackageNotFoundError:
        return None


def stripped_package_version(package_name: str) -> str | None:
    """
    Get the installed version of the specified package, stripped of any local version part.

    Returns only the public version segment (e.g., '1.2.3' or '1.2.3.post4'),
    omitting any local segment (e.g., '+d136').

    Args:
        package_name (str): The name of the package to query.

    Returns:
        str | None: The public version string, or None if the package is not installed.
    """
    v_str = package_version(package_name)
    if v_str is None:
        return None
    try:
        v = Version(v_str)
        return str(v.public)
    except Exception:
        return v_str


def _get_release_info(tag: str | None) -> dict | None:
    """
    Fetch release info from GitHub for the given tag (or latest if None).
    Uses unauthenticated API by default, but includes GITHUB_TOKEN from the environment
    if available to avoid rate limiting.

    Args:
        tag (str | None): The tag of the release to fetch, or None for latest.

    Returns:
        dict | None: The release info dictionary if retrievable, None otherwise.
    """
    if tag is not None:
        api_url = f'https://api.github.com/repos/easyscience/diffraction-lib/releases/tags/{tag}'
    else:
        api_url = 'https://api.github.com/repos/easyscience/diffraction-lib/releases/latest'
    try:
        _validate_url(api_url)
        headers = {}
        token = os.environ.get('GITHUB_TOKEN')
        if token:
            headers['Authorization'] = f'token {token}'

        request = urllib.request.Request(api_url, headers=headers)  # noqa: S310
        with urllib.request.urlopen(request) as response:  # noqa: S310
            return json.load(response)
    except Exception as e:
        if tag is not None:
            print(error(f'Failed to fetch release info for tag {tag}: {e}'))
        else:
            print(error(f'Failed to fetch latest release info: {e}'))
        return None


def _get_tutorial_asset(release_info: dict) -> dict | None:
    """
    Given a release_info dict, return the 'tutorials.zip' asset dict, or None.

    Args:
        release_info (dict): The release info dictionary.

    Returns:
        dict | None: The asset dictionary for 'tutorials.zip' if found, None otherwise.
    """
    assets = release_info.get('assets', [])
    for asset in assets:
        if asset.get('name') == 'tutorials.zip':
            return asset
    return None


def _sort_notebooks(notebooks: list[str]) -> list[str]:
    """
    Sorts the list of notebook filenames.

    Args:
        notebooks (list[str]): List of notebook filenames.

    Returns:
        list[str]: Sorted list of notebook filenames.
    """
    return sorted(notebooks)


def _extract_notebooks_from_asset(download_url: str) -> list[str]:
    """
    Download the tutorials.zip from download_url and return a sorted list of .ipynb file names.

    Args:
        download_url (str): URL to download the tutorials.zip asset.

    Returns:
        list[str]: Sorted list of .ipynb filenames found in the archive.
    """
    try:
        _validate_url(download_url)
        with urllib.request.urlopen(download_url) as response:  # noqa: S310
            with zipfile.ZipFile(io.BytesIO(response.read())) as zip_file:
                notebooks = [
                    os.path.basename(name)
                    for name in zip_file.namelist()
                    if name.endswith('.ipynb') and not name.endswith('/')
                ]
                return _sort_notebooks(notebooks)
    except Exception as e:
        print(error(f"Failed to download or parse 'tutorials.zip': {e}"))
        return []


def fetch_tutorial_list() -> list[str]:
    """
    Return a list of available tutorial notebook filenames from the GitHub release
    that matches the installed version of `easydiffraction`, if possible. If the
    version-specific release is unavailable, falls back to the latest release.

    This function does not fetch or display the tutorials themselves; it only lists
    the notebook filenames (e.g., '01-intro.ipynb', ...) found inside the
    'tutorials.zip' asset of the appropriate GitHub release.

    Returns:
        list[str]: A sorted list of tutorial notebook filenames (without directories)
        extracted from the corresponding release's tutorials.zip, or an empty list
        if unavailable.
    """
    version_str = stripped_package_version('easydiffraction')
    tag = f'v{version_str}' if version_str is not None else None
    release_info = _get_release_info(tag)
    # Fallback to latest if tag fetch failed and tag was attempted
    if release_info is None and tag is not None:
        print(error('Falling back to latest release info...'))
        release_info = _get_release_info(None)
    if release_info is None:
        return []
    tutorial_asset = _get_tutorial_asset(release_info)
    if not tutorial_asset:
        print(error("'tutorials.zip' not found in the release."))
        return []
    download_url = tutorial_asset.get('browser_download_url')
    if not download_url:
        print(error("'browser_download_url' not found for tutorials.zip."))
        return []
    return _extract_notebooks_from_asset(download_url)


def list_tutorials():
    """
    List available tutorial notebooks.

    Args:
        None

    Returns:
        None
    """
    tutorials = fetch_tutorial_list()
    columns_data = [[t] for t in tutorials]
    columns_alignment = ['left']

    released_ed_version = stripped_package_version('easydiffraction')

    print(paragraph(f'📘 Tutorials available for easydiffraction v{released_ed_version}:'))
    render_table(
        columns_data=columns_data,
        columns_alignment=columns_alignment,
        show_index=True,
    )


def fetch_tutorials() -> None:
    """
    Download and extract the tutorials ZIP archive from the GitHub release matching the
    installed version of `easydiffraction`, if available. If the version-specific release
    is unavailable, falls back to the latest release.

    The archive is extracted into the current working directory and then removed.

    Args:
        None

    Returns:
        None
    """
    version_str = stripped_package_version('easydiffraction')
    tag = f'v{version_str}' if version_str is not None else None
    release_info = _get_release_info(tag)
    # Fallback to latest if tag fetch failed and tag was attempted
    if release_info is None and tag is not None:
        print(error('Falling back to latest release info...'))
        release_info = _get_release_info(None)
    if release_info is None:
        print(error('Unable to fetch release info.'))
        return
    tutorial_asset = _get_tutorial_asset(release_info)
    if not tutorial_asset:
        print(error("'tutorials.zip' not found in the release."))
        return
    file_url = tutorial_asset.get('browser_download_url')
    if not file_url:
        print(error("'browser_download_url' not found for tutorials.zip."))
        return
    file_name = 'tutorials.zip'
    # Validate URL for security
    _validate_url(file_url)

    print('📥 Downloading tutorial notebooks...')
    urllib.request.urlretrieve(file_url, file_name)  # noqa: S310

    print('📦 Extracting tutorials to "tutorials/"...')
    with zipfile.ZipFile(file_name, 'r') as zip_ref:
        zip_ref.extractall()

    print('🧹 Cleaning up...')
    os.remove(file_name)

    print('✅ Tutorials fetched successfully.')


def show_version() -> None:
    """
    Print the installed version of the easydiffraction package.

    Args:
        None

    Returns:
        None
    """
    current_ed_version = package_version('easydiffraction')
    print(paragraph(f'📘 Current easydiffraction v{current_ed_version}'))


def is_notebook() -> bool:
    """
    Determines if the current environment is a Jupyter Notebook.

    Returns:
        bool: True if running inside a Jupyter Notebook, False otherwise.
    """
    if IPython is None:
        return False

    if is_pycharm():  # Running inside PyCharm
        return True
    elif is_colab():  # Running inside Google Colab
        return True

    try:
        shell = get_ipython().__class__.__name__  # noqa: F821
        if shell == 'ZMQInteractiveShell':  # Jupyter notebook or qtconsole
            return True
        elif shell == 'TerminalInteractiveShell':  # Terminal running IPython
            return False
        else:  # Other type (unlikely)
            return False
    except NameError:
        return False  # Probably standard Python interpreter


def is_pycharm() -> bool:
    """
    Determines if the current environment is PyCharm.

    Returns:
        bool: True if running inside PyCharm, False otherwise.
    """
    return os.environ.get('PYCHARM_HOSTED') == '1'


def is_colab() -> bool:
    """
    Determines if the current environment is Google Colab.

    Returns:
        bool: True if running in Google Colab PyCharm, False otherwise.
    """
    try:
        return importlib.util.find_spec('google.colab') is not None
    except ModuleNotFoundError:
        return False


def is_github_ci() -> bool:
    """
    Determines if the current process is running in GitHub Actions CI.

    Returns:
        bool: True if the environment variable ``GITHUB_ACTIONS`` is set
        (Always "true" on GitHub Actions), False otherwise.
    """
    return os.environ.get('GITHUB_ACTIONS') is not None


def render_table(
    columns_data,
    columns_alignment,
    columns_headers=None,
    show_index=False,
    display_handle=None,
):
    """
    Renders a table either as an HTML (in Jupyter Notebook) or ASCII (in terminal),
    with aligned columns.

    Args:
        columns_data (list): List of lists, where each inner list represents a row of data.
        columns_alignment (list): Corresponding text alignment for each column (e.g., 'left', 'center', 'right').
        columns_headers (list): List of column headers.
        show_index (bool): Whether to show the index column.
        display_handle: Optional display handle for updating in Jupyter.

    Returns:
        None
    """

    # Use pandas DataFrame for Jupyter Notebook rendering
    if is_notebook():
        # Create DataFrame
        if columns_headers is None:
            df = pd.DataFrame(columns_data)
            df.columns = range(df.shape[1])  # Ensure numeric column labels
            columns_headers = df.columns.tolist()
            skip_headers = True
        else:
            df = pd.DataFrame(columns_data, columns=columns_headers)
            skip_headers = False

        # Force starting index from 1
        if show_index:
            df.index += 1

        # Replace None/NaN values with empty strings
        df.fillna('', inplace=True)

        # Formatters for data cell alignment and replacing None with empty string
        def make_formatter(align):
            return lambda x: f'<div style="text-align: {align};">{x}</div>'

        formatters = {col: make_formatter(align) for col, align in zip(columns_headers, columns_alignment)}

        # Convert DataFrame to HTML
        html = df.to_html(
            escape=False,
            index=show_index,
            formatters=formatters,
            border=0,
            header=not skip_headers,
        )

        # Add inline CSS to align the entire table to the left and show border
        html = html.replace(
            '<table class="dataframe">',
            '<table class="dataframe" '
            'style="'
            'border-collapse: collapse; '
            'border: 1px solid #515155; '
            'margin-left: 0.5em;'
            'margin-top: 0.5em;'
            'margin-bottom: 1em;'
            '">',
        )

        # Manually apply text alignment to headers
        if not skip_headers:
            for col, align in zip(columns_headers, columns_alignment):
                html = html.replace(f'<th>{col}', f'<th style="text-align: {align};">{col}')

        # Display or update the table in Jupyter Notebook
        if display_handle is not None:
            display_handle.update(HTML(html))
        else:
            display(HTML(html))

    # Use tabulate for terminal rendering
    else:
        if columns_headers is None:
            columns_headers = []

        indices = show_index
        if show_index:
            # Force starting index from 1
            indices = range(1, len(columns_data) + 1)

        table = tabulate(
            columns_data,
            headers=columns_headers,
            tablefmt='fancy_outline',
            numalign='left',
            stralign='left',
            showindex=indices,
        )

        print(table)


def render_cif(cif_text, paragraph_title) -> None:
    """
    Display the CIF text as a formatted table in Jupyter Notebook or terminal.

    Args:
        cif_text: The CIF text to display.
        paragraph_title: The title to print above the table.

    Returns:
        None
    """
    # Split into lines and replace empty ones with a '&nbsp;'
    # (non-breaking space) to force empty lines to be rendered in
    # full height in the table. This is only needed in Jupyter Notebook.
    if is_notebook():
        lines: List[str] = [line if line.strip() else '&nbsp;' for line in cif_text.splitlines()]
    else:
        lines: List[str] = [line for line in cif_text.splitlines()]

    # Convert each line into a single-column format for table rendering
    columns: List[List[str]] = [[line] for line in lines]

    # Print title paragraph
    print(paragraph_title)

    # Render the table using left alignment and no headers
    render_table(
        columns_data=columns,
        columns_alignment=['left'],
    )


def tof_to_d(
    tof: np.ndarray,
    offset: float,
    linear: float,
    quad: float,
    quad_eps=1e-20,
) -> np.ndarray:
    """Convert time-of-flight (TOF) to d-spacing using a quadratic calibration.

    Model:
        TOF = offset + linear * d + quad * d²

    The function:
      - Uses a linear fallback when the quadratic term is effectively zero.
      - Solves the quadratic for d and selects the smallest positive, finite root.
      - Returns NaN where no valid solution exists.
      - Expects ``tof`` as a NumPy array; output matches its shape.

    Args:
        tof (np.ndarray): Time-of-flight values (µs). Must be a NumPy array.
        offset (float): Calibration offset (µs).
        linear (float): Linear calibration coefficient (µs/Å).
        quad (float): Quadratic calibration coefficient (µs/Å²).
        quad_eps (float, optional): Threshold to treat ``quad`` as zero. Defaults to 1e-20.

    Returns:
        np.ndarray: d-spacing values (Å), NaN where invalid.

    Raises:
        TypeError: If ``tof`` is not a NumPy array or coefficients are not real numbers.
    """
    # Type checks
    if not isinstance(tof, np.ndarray):
        raise TypeError(f"'tof' must be a NumPy array, got {type(tof).__name__}")
    for name, val in (('offset', offset), ('linear', linear), ('quad', quad), ('quad_eps', quad_eps)):
        if not isinstance(val, (int, float, np.integer, np.floating)):
            raise TypeError(f"'{name}' must be a real number, got {type(val).__name__}")

    # Output initialized to NaN
    d_out = np.full_like(tof, np.nan, dtype=float)

    # 1) If quadratic term is effectively zero, use linear formula:
    #    TOF ≈ offset + linear * d =>
    #    d ≈ (tof - offset) / linear
    if abs(quad) < quad_eps:
        if linear != 0.0:
            d = (tof - offset) / linear
            # Keep only positive, finite results
            valid = np.isfinite(d) & (d > 0)
            d_out[valid] = d[valid]
        # If B == 0 too, there's no solution; leave NaN
        return d_out

    # 2) If quadratic term is significant, solve the quadratic equation:
    #    TOF = offset + linear * d + quad * d² =>
    #    quad * d² + linear * d + (offset - tof) = 0
    discr = linear**2 - 4 * quad * (offset - tof)
    has_real_roots = discr >= 0

    if np.any(has_real_roots):
        sqrt_discr = np.sqrt(discr[has_real_roots])

        root_1 = (-linear + sqrt_discr) / (2 * quad)
        root_2 = (-linear - sqrt_discr) / (2 * quad)

        # Pick smallest positive, finite root per element
        roots = np.stack((root_1, root_2), axis=0)  # Stack roots for comparison
        roots = np.where(np.isfinite(roots) & (roots > 0), roots, np.nan)  # Replace non-finite or negative roots with NaN
        chosen = np.nanmin(roots, axis=0)  # Choose the smallest positive root or NaN if none are valid

        d_out[has_real_roots] = chosen

    return d_out


def twotheta_to_d(twotheta, wavelength):
    """
    Convert 2-theta to d-spacing using Bragg's law.

    Parameters:
        twotheta (float or np.ndarray): 2-theta angle in degrees.
        wavelength (float): Wavelength in Å.

    Returns:
        d (float or np.ndarray): d-spacing in Å.
    """
    # Convert twotheta from degrees to radians
    theta_rad = np.radians(twotheta / 2)

    # Calculate d-spacing using Bragg's law
    d = wavelength / (2 * np.sin(theta_rad))

    return d


def get_value_from_xye_header(file_path, key):
    """
    Extracts a floating point value from the first line of the file, corresponding to the given key.

    Parameters:
        file_path (str): Path to the input file.
        key (str): The key to extract ('DIFC' or 'two_theta').

    Returns:
        float: The extracted value.

    Raises:
        ValueError: If the key is not found.
    """
    pattern = rf'{key}\s*=\s*([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)'

    with open(file_path, 'r') as f:
        first_line = f.readline()

    match = re.search(pattern, first_line)
    if match:
        return float(match.group(1))
    else:
        raise ValueError(f'{key} not found in the header.')
