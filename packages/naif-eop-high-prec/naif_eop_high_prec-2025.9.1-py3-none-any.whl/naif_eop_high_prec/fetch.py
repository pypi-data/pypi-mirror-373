import argparse
import hashlib
import os

import requests

URL = "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/earth_latest_high_prec.bpc"
FILE = os.path.join(os.path.dirname(__file__), "earth_latest_high_prec.bpc")
MD5_FILE = os.path.join(os.path.dirname(__file__), "earth_latest_high_prec.md5")


def fetch_file(url: str, output_file: str):
    """
    Fetches the file from the given URL and saves it to the output file.

    Parameters
    ----------
    url : str
        The URL to fetch the file from.
    output_file : str
        The path to the output file.

    Raises
    ------
    Exception
        If the status code of the response is not 200.
    """
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(
            f"Failed to fetch file from {url}. Status code: {response.status_code}"
        )
    with open(output_file, "wb") as f:
        f.write(response.content)


def store_md5_hash(file: str, output_file: str):
    """
    Stored the MD5 hash of the given file to the output file.

    Parameters
    ----------
    file : str
        The path to the file.

    Returns
    -------
    str
        The MD5 hash of the file.
    """
    with open(file, "rb") as f:
        contents = f.read()
        with open(output_file, "w") as f_out:
            f_out.write(
                hashlib.md5(contents).hexdigest() + "  " + os.path.basename(file)
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch the NAIF high precision EOP kernel file store its checksum."
    )
    parser.add_argument(
        "--url",
        type=str,
        default=URL,
        help="URL to fetch the NAIF high precision EOP kernel file from.",
    )
    parser.add_argument(
        "--file",
        type=str,
        default=FILE,
        help="Path where to save file.",
    )
    parser.add_argument(
        "--md5_file",
        type=str,
        default=MD5_FILE,
        help="Path where to save MD5 hash file.",
    )
    args = parser.parse_args()

    fetch_file(args.url, args.file)
    store_md5_hash(args.file, args.md5_file)
