import shutil
from urllib.parse import unquote
import html
from urllib.parse import urlparse, parse_qs
from datetime import datetime

def check_free_space(path=".") -> int:
    """Returns free space in bytes for the given path"""
    usage = shutil.disk_usage(path)
    return usage.free

def getQueryParamFromPlaybackUri(url: str, param: str) -> str:
    """Extracts the value of a query parameter from a URL"""
    if '?' not in url:
        return ''
    decoded_url = html.unescape(url)
    parsed_url = urlparse(decoded_url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get(param, [''])[0]

def get_trimming_params(user_start_dt: datetime, user_end_dt: datetime, chunk_start_dt: datetime, chunk_end_dt: datetime) -> tuple[float, float] | None:
    """
    Calculates the trimming parameters (offset and duration) for a single chunk.

    Args:
        user_start_dt (datetime): The start datetime requested by the user.
        user_end_dt (datetime): The end datetime requested by the user.
        chunk_start_dt (datetime): The start datetime of the recording chunk.
        chunk_end_dt (datetime): The end datetime of the recording chunk.

    Returns:
        tuple[float, float] or None: A tuple containing (offsetInSeconds, durationInSeconds)
                                       if there is an overlap, otherwise None.
    """
    # Find the intersection of the two time intervals
    intersection_start = max(user_start_dt, chunk_start_dt)
    intersection_end = min(user_end_dt, chunk_end_dt)

    # Check for valid overlap
    if intersection_end > intersection_start:
        offset_in_seconds = (intersection_start - chunk_start_dt).total_seconds()
        duration_in_seconds = (intersection_end - intersection_start).total_seconds()
        return offset_in_seconds, duration_in_seconds
    else:
        return None
