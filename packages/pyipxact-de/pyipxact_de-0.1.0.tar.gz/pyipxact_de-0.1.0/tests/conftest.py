# from tempfile import TemporaryDirectory
# import shutil
import os
import ssl
import urllib.request
import zipfile
from email.utils import parsedate_to_datetime
from pathlib import Path

import pytest

FILE_PATH = Path(__file__).parent


def _cache_base_dir() -> Path:
    """Return the base cache directory under /tmp.

    Returns:
        Path: The cache directory path (e.g., /tmp/pyipxact_leon2_cache).
    """
    base = Path("/tmp") / "pyipxact_leon2_cache"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _download_if_newer(url: str, dest: Path) -> bool:
    """Download a URL to a destination file only if the remote is newer.

    Behavior is similar to `wget --timestamping` using the If-Modified-Since
    request header. If the destination file does not exist, it will be
    downloaded. If it exists, a conditional request is issued; if the server
    responds with 304 Not Modified, the download is skipped.

    Args:
        url: The URL to download.
        dest: The destination file path under the cache directory.

    Returns:
        bool: True if a fresh download occurred, False if skipped.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Use unverified SSL context as in existing flow (server cert may be self-signed)
    ssl._create_default_https_context = ssl._create_unverified_context  # noqa: SLF001

    remote_ts = _remote_last_modified(url)
    if dest.exists() and remote_ts is not None and dest.stat().st_mtime >= remote_ts:
        return False

    # Fallback: if no Last-Modified available and file exists, still skip re-download
    if dest.exists() and remote_ts is None:
        return False

    urllib.request.urlretrieve(url, dest)
    if remote_ts is not None:
        os.utime(dest, (remote_ts, remote_ts))
    return True


def _remote_last_modified(url: str) -> float | None:
    """Return the remote resource Last-Modified timestamp (epoch seconds).

    Performs a HEAD request. If the server doesn't provide the
    Last-Modified header or HEAD fails, returns None.

    Args:
        url: The URL to query.

    Returns:
        float | None: POSIX timestamp if available, else None.
    """
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req) as resp:  # noqa: S310 - trusted host
            last_mod = resp.headers.get("Last-Modified")
            if not last_mod:
                return None
            try:
                dt = parsedate_to_datetime(last_mod)
                if dt is None:
                    return None
                return dt.timestamp()
            except Exception:
                return None
    except Exception:
        return None


def _should_extract(zip_path: Path, extract_dir: Path) -> bool:
    """Determine whether a ZIP should be (re)extracted to the target dir.

    We keep a marker file with the ZIP's mtime to decide if re-extraction is needed.

    Args:
        zip_path: Path to the ZIP file.
        extract_dir: Target extraction directory.

    Returns:
        bool: True if extraction should occur, False to skip.
    """
    if not extract_dir.exists():
        return True

    marker = extract_dir / ".zip_mtime"
    if not marker.exists():
        return True

    try:
        recorded = float(marker.read_text().strip())
    except Exception:
        return True

    return abs(recorded - zip_path.stat().st_mtime) > 1e-6


def _extract_zip(zip_path: Path, extract_dir: Path) -> None:
    """Extract a ZIP file to a directory and update the marker file.

    Args:
        zip_path: Path to the ZIP file.
        extract_dir: Target directory to extract contents into.
    """
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)
    marker = extract_dir / ".zip_mtime"
    marker.write_text(str(zip_path.stat().st_mtime))


def pytest_make_parametrize_id(config, val, argname):
    return f"{argname}={val}"


# def pytest_sessionstart(session):
#     leon2_example_url = "https://www.accellera.org/images/activities/committees/ip-xact/Leon2_1685-2022.zip"

#     td = TemporaryDirectory()
#     tmp_path = Path(td.name)

#     # download Leon2_1685-2022.zip in the temporary directory
#     ssl._create_default_https_context = ssl._create_unverified_context
#     urllib.request.urlretrieve(leon2_example_url, tmp_path / "Leon2_1685-2022.zip")

#     # unzip Leon2_1685-2022.zip in the temporary directory
#     with zipfile.ZipFile(tmp_path / "Leon2_1685-2022.zip", "r") as zip_ref:
#         zip_ref.extractall(tmp_path)

#     print(tmp_path)

#     session.__CACHE = tmp_path


# def pytest_sessionfinish(session, exitstatus):
#     # session.__CACHE.cleanup()
#     print(session.__CACHE)



# Global variables to store download directory and XML files
DOWNLOAD_DIR = None
# XML_FILES_LIST = []
XML_FILES_WITH_MODULE = []

# def pytest_generate_tests(metafunc):
#     """
#     Parametrize tests dynamically based on available XML files,
#     only for test_deserialize.py.
#     """
#     # Check if the test function requires 'xml_file' and is part of 'test_deserialize.py'
#     if "xml_file" in metafunc.fixturenames and metafunc.function.__module__.endswith("test_deserialize"):
#         global DOWNLOAD_DIR, XML_FILES_LIST

#         if not XML_FILES_LIST:
#             leon2_example_url = "https://www.accellera.org/images/activities/committees/ip-xact/Leon2_1685-2022.zip"
#             DOWNLOAD_DIR = tempfile.mkdtemp(prefix="leon2_test_")
#             download_path = Path(DOWNLOAD_DIR)
#             print(f"  ➤ Downloading and extracting 'Leon2_1685-2022.zip' to {download_path}...")

#             # Disable SSL verification for the download
#             ssl._create_default_https_context = ssl._create_unverified_context

#             # Define paths
#             zip_path = download_path / "Leon2_1685-2022.zip"

#             try:
#                 # Download the ZIP file
#                 urllib.request.urlretrieve(leon2_example_url, zip_path)
#                 print(f"    ➤ Downloaded ZIP to {zip_path}")
#             except Exception as e:
#                 pytest.exit(f"Failed to download ZIP file: {e}")

#             try:
#                 # Extract the ZIP file
#                 with zipfile.ZipFile(zip_path, "r") as zip_ref:
#                     zip_ref.extractall(download_path)
#                 print(f"    ➤ Extracted ZIP to {download_path}")
#             except Exception as e:
#                 pytest.exit(f"Failed to extract ZIP file: {e}")

#             # Collect all XML files
#             XML_FILES_LIST = list(download_path.rglob("*.xml"))
#             print(f"    ➤ Found {len(XML_FILES_LIST)} XML files.")

#             if not XML_FILES_LIST:
#                 pytest.exit("No XML files found in the extracted directory.")

#         # Generate test case IDs based on relative file paths
#         ids = [str(p.relative_to(DOWNLOAD_DIR)) for p in XML_FILES_LIST]

#         metafunc.parametrize(
#             "xml_file",
#             XML_FILES_LIST,
#             ids=ids
#         )





def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Parametrize tests dynamically based on available XML files,
    only for test_deserialize.py.
    """

    # Check if the test function requires 'xml_file' and 'module_name'
    if (
        {"xml_file", "module_name"}.issubset(metafunc.fixturenames)
        and metafunc.function.__module__.endswith("test_deserialize")
    ):
        global DOWNLOAD_DIR, XML_FILES_WITH_MODULE

        if not XML_FILES_WITH_MODULE:
            # Define the list of (ZIP URL, associated module)
            leon2_zips = [
                (
                    "https://www.accellera.org/images/activities/committees/ip-xact/Leon2_1685-2014.zip",
                    "v1685_2014",
                    "1685_2014",
                ),
                (
                    "https://www.accellera.org/images/activities/committees/ip-xact/Leon2_1685-2022.zip",
                    "v1685_2022",
                    "1685_2022",
                ),
            ]

            # Use shared cache directory under /tmp
            cache_dir = _cache_base_dir()
            DOWNLOAD_DIR = str(cache_dir)
            print(
                f" ➤ Ensuring Leon2 ZIPs exist and are extracted under cache: {cache_dir}"
            )

            # Disable SSL verification for the download (use with caution)
            ssl._create_default_https_context = ssl._create_unverified_context

            for zip_url, module_suffix, folder_name in leon2_zips:
                zip_filename = Path(zip_url).name
                zip_path = cache_dir / zip_filename
                extract_dir = cache_dir / folder_name

                try:
                    # Download the ZIP file if needed
                    print(f"  ➤ Checking '{zip_filename}' for updates…")
                    downloaded = _download_if_newer(zip_url, zip_path)
                    if downloaded:
                        print(f"    • Downloaded to '{zip_path}'")
                    else:
                        print(f"    • Using cached ZIP at '{zip_path}'")
                except Exception as e:
                    pytest.exit(
                        f"Failed to download ZIP file '{zip_filename}': {e}"
                    )

                try:
                    # Extract the ZIP file
                    if _should_extract(zip_path, extract_dir):
                        print(
                            f"  ➤ Extracting '{zip_filename}' to '{extract_dir}'…"
                        )
                        _extract_zip(zip_path, extract_dir)
                        print(f"      • Extracted to '{extract_dir}'")
                    else:
                        print(
                            f"      • Using existing extracted directory: '{extract_dir}'"
                        )
                except zipfile.BadZipFile:
                    pytest.exit(f"Bad ZIP file '{zip_filename}'.")
                except Exception as e:
                    pytest.exit(
                        f"Failed to extract ZIP file '{zip_filename}': {e}"
                    )

                # Collect all XML files and associate them with the module suffix
                xml_files = list(extract_dir.rglob("*.xml"))
                if not xml_files:
                    pytest.exit(f"No XML files found in ZIP file '{zip_filename}'.")

                for xml_file in xml_files:
                    XML_FILES_WITH_MODULE.append((xml_file, module_suffix))
                print(f"      • Found {len(xml_files)} XML files in '{zip_filename}'.")

        if not XML_FILES_WITH_MODULE:
            pytest.exit("No XML files available for testing.")

        # Generate test case IDs with module information
        ids = [
            f"{xml_file.relative_to(DOWNLOAD_DIR)} ({module_name})"
            for xml_file, module_name in XML_FILES_WITH_MODULE
        ]

        # Parametrize 'xml_file' and 'module_name' together
        metafunc.parametrize(
            ("xml_file", "module_name"),
            XML_FILES_WITH_MODULE,
            ids=ids
        )

    # Check if the test function requires 'xml_file' and 'standard', "version"
    if (
        {"standard", "version", "xml_file"}.issubset(metafunc.fixturenames)
        and metafunc.function.__module__.endswith("test_xml")
    ):

        xml_dir_path = FILE_PATH / "xml"
        xml_files = list(xml_dir_path.rglob("*.xml"))

        print(f"\nFound {len(xml_files)} xml files under {xml_dir_path}")

        param_values = []
        for xml_file in xml_files:
            xml_file_relative = xml_file.relative_to(xml_dir_path)
            standard = xml_file_relative.parts[0]
            version = xml_file_relative.parts[1]
            param_values.append((standard, version, xml_file))

        # Generate test case IDs based on relative file paths
        ids = [
            f"{standard} - {version} - xml/{xml_file.relative_to(xml_dir_path)}"
            for standard, version, xml_file in param_values
        ]

        metafunc.parametrize(
            ("standard", "version", "xml_file"),
            param_values,
            ids=ids
        )


def pytest_sessionfinish(session, exitstatus):
    """
    Notify the user of the download directory location after tests complete.
    """
    global DOWNLOAD_DIR
    if DOWNLOAD_DIR:
        print(f"\n➤ Temporary download directory retained at: {DOWNLOAD_DIR}")
        print("➤ You can inspect the downloaded and extracted files there.")
        # If you prefer to clean up the directory after tests, uncomment the following lines:
        # shutil.rmtree(DOWNLOAD_DIR)
        # print("➤ Cleaned up temporary directory.")
