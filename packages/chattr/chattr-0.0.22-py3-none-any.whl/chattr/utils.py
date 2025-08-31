"""This module contains utility functions for the Chattr app."""

from pathlib import Path

from m3u8 import M3U8, load
from pydantic import HttpUrl, ValidationError
from pydub import AudioSegment
from requests import Session

from chattr.settings import logger


def is_url(value: str) -> bool:
    """
    Check if a string is a valid URL.

    Args:
        value: The string to check. Can be None.

    Returns:
        bool: True if the string is a valid URL, False otherwise.
    """
    if value is None:
        return False

    try:
        HttpUrl(value)
        return True
    except ValidationError:
        return False


def download_file(url: HttpUrl, path: Path) -> None:
    """
    Download a file from a URL and save it to a local path.

    Args:
        url: The URL to download the file from.
        path: The local file path where the downloaded file will be saved.

    Returns:
        None

    Raises:
        requests.RequestException: If the HTTP request fails.
        IOError: If file writing fails.
    """
    if str(url).endswith(".m3u8"):
        _playlist: M3U8 = load(url)
        url: str = str(url).replace("playlist.m3u8", _playlist.segments[0].uri)
    print(url)
    session = Session()
    response = session.get(url, stream=True, timeout=30)
    response.raise_for_status()
    with open(path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)


def convert_audio_to_wav(input_path: Path, output_path: Path) -> None:
    """
    Convert an audio file from aac to WAV format.

    Args:
        input_path: The path to the input aac file.
        output_path: The path to the output WAV file.

    Returns:
        None
    """
    logger.info(f"Converting {input_path} to WAV format")
    audio = AudioSegment.from_file(input_path, "aac")
    audio.export(output_path, "wav")
    logger.info(f"Converted {input_path} to {output_path}")
