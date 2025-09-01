"""
Hikvision NVR Clip Downloader (ISAPI)
------------------------------------

A robust, flexible Python library to search and download recorded clips from a Hikvision NVR
using the ISAPI endpoints:
  - /ISAPI/ContentMgmt/search
  - /ISAPI/ContentMgmt/download

Key features
------------
- Digest authentication (requests + HTTPDigestAuth)
- Parameterized camera (channel) and stream (main/sub track)
- Time range search and direct time-based download
- Safe, resumable (idempotent) downloads with streaming + progress callback
- Automatic XML request/response handling
- Retries with exponential backoff
- Sensible defaults but highly configurable

Tested against multiple DS-7xxx series NVRs. ISAPI implementations vary slightly across firmware;
this library tries to be permissive, and offers fallbacks (e.g., constructing a playbackURI
if search doesn't return one).

Usage
-----
from hikvision_nvr_downloader import HikvisionNVRClient, StreamType
from datetime import datetime, timezone

client = HikvisionNVRClient(
    host="192.168.1.100",
    username="admin",
    password="your_password",
    port=80,  # ISAPI default
)

start = datetime(2025, 8, 24, 10, 0, 0, tzinfo=timezone.utc)
end   = datetime(2025, 8, 24, 10, 5, 0, tzinfo=timezone.utc)

# Option A: search, then download first match
matches = client._search_media(camera=1, start=start, end=end)
if matches:
    client._download_by_playback_uri(matches[0].playback_uri, dest_path="/tmp/cam1_1000-1005.mp4")

# Option B: direct time window download (builds playback URI if needed)
client.download_by_time(camera=2, start=start, end=end, dest_dir="/tmp")

Notes
-----
* Times should be timezone-aware datetimes. If you pass naive datetimes, the library assumes local timezone.
* On most Hikvision NVRs, track IDs follow this convention:
    - main stream:  camera N -> trackID = N*100 + 1  (e.g., cam 1 => 101, cam 4 => 401)
    - sub  stream:  camera N -> trackID = N*100 + 2  (e.g., cam 1 => 102, cam 4 => 402)
* The NVR must be reachable over HTTP (default port 80) on the same network.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Union
from urllib.parse import urlencode
from xml.etree import ElementTree
import uuid
import re
import os

import requests
from requests.auth import HTTPDigestAuth
from .convert import convertAndTrim, get_media_info
from .utils import getQueryParamFromPlaybackUri, check_free_space, get_trimming_params
import subprocess

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore

__all__ = [
    "HikvisionNVRClient",
    "StreamType",
    "SearchMatch",
]

# ----------------------------
# Data models / small helpers
# ----------------------------
class StreamType:
    MAIN = "main"
    SUB = "sub"

    @staticmethod
    def to_track_id(camera: int, stream: str) -> int:
        stream = (stream or StreamType.MAIN).lower()
        if stream not in {StreamType.MAIN, StreamType.SUB}:
            raise ValueError(f"Unsupported stream '{stream}'. Use 'main' or 'sub'.")
        base = camera * 100
        return base + (1 if stream == StreamType.MAIN else 2)


def _ensure_tz(dt: datetime) -> datetime:
    """Ensure datetime has tzinfo. If naive, assume local time."""
    if dt.tzinfo is None:
        try:
            # Best-effort local timezone inference
            return dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
        except Exception:
            return dt.replace(tzinfo=timezone.utc)
    return dt


def _iso8601(dt: datetime) -> str:
    dt = _ensure_tz(dt).astimezone(timezone.utc)
    # Hikvision accepts Z format; some firmwares accept offset as well. We'll use Z.
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class SearchMatch:
    start_time: datetime
    end_time: datetime
    track_id: Optional[int]
    playback_uri: str
    file_path: Optional[str] = None
    size_bytes: Optional[int] = None


# ----------------------------
# Core client
# ----------------------------
class HikvisionNVRClient:
    __BYTES_IN_ONE_GB = 1073741824
    __MIN_BUFFER_SIZE = 2 * __BYTES_IN_ONE_GB
    __SEARCH_MEDIA_URL = "/ISAPI/ContentMgmt/search"
    __DOWNLOAD_MEDIA_URL = "/ISAPI/ContentMgmt/download"

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        *,
        port: int = 80,
        scheme: str = "http",
        timeout: int = 20,
        max_retries: int = 3,
        backoff_factor: float = 0.8,
        session: Optional[requests.Session] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """
        :param host: NVR IP or hostname
        :param username: ISAPI user (typically admin)
        :param password: password
        :param port: ISAPI port (default 80 for HTTP)
        :param scheme: 'http' (default). Use 'https' if your NVR exposes TLS.
        :param timeout: per-request timeout in seconds
        :param max_retries: number of retries for idempotent operations
        :param backoff_factor: exponential backoff base for retries
        :param session: optional custom requests.Session
        :param logger: optional logger; if None, a module-level logger is created
        """
        self.host = host.strip("/")
        self.username = username
        self.password = password
        self.port = int(port)
        self.scheme = scheme
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.log = logger or logging.getLogger(self.__class__.__name__)
        if not self.log.handlers:
            handler = logging.StreamHandler()
            fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(fmt)
            self.log.addHandler(handler)
            self.log.setLevel(logging.INFO)

        self.session = session or requests.Session()
        self.session.auth = HTTPDigestAuth(self.username, self.password)
        # Avoid endless keep-alive sockets in long runs
        self.session.headers.update({"Connection": "close"})

    # ------------------------
    # Public API
    # ------------------------
    def _search_media(
        self,
        *,
        start: datetime,
        end: datetime,
        track_id: Optional[int] = StreamType.MAIN,
        max_results: int = 40,
        position: int = 0,
    ) -> List[SearchMatch]:
        """Search recorded segments spanning [start, end].

        Returns a list of SearchMatch items (may be empty).
        """
            

        start_iso = _iso8601(start)
        end_iso = _iso8601(end)

        # Build CMSearchDescription XML
        xml = f"""<?xml version='1.0' encoding='utf-8'?><CMSearchDescription>
  <searchID>{str(uuid.uuid1()).upper()}</searchID>
  <trackIDList>
    <trackID>{track_id}</trackID>
  </trackIDList>
  <timeSpanList>
    <timeSpan>
      <startTime>{start_iso}</startTime>
      <endTime>{end_iso}</endTime>
    </timeSpan>
  </timeSpanList>
  <maxResults>{int(max_results)}</maxResults>
  <searchResultPosition>{int(position)}</searchResultPosition>
  <metadataList>
    <metadataDescriptor>//recordType.meta.hikvision.com</metadataDescriptor>
  </metadataList>
</CMSearchDescription>"""

        url = self._url(self.__SEARCH_MEDIA_URL)
        self.log.debug("search_media POST %s", url)
        request = ElementTree.fromstring(xml)
        request_data = ElementTree.tostring(request, encoding='utf8', method='xml')
        resp = self._request("post", url, data=request_data, headers={"Content-Type": "application/xml"})

        if resp.status_code != 200:
            raise RuntimeError(f"Search failed: HTTP {resp.status_code}: {resp.text}")
        
        print(resp.text)

        return self._parse_search_results(resp.text)
    
    def _concatenate_and_cleanup_in_dir(self, dest_dir: str, filenames: List[str], output_filename: str):
        """
        Concatenates video files from a specified directory using FFmpeg and
        cleans up original files upon successful concatenation.

        Args:
            dest_dir (str): The path to the directory containing the video files.
            filenames (List[str]): A list of filenames (e.g., 'file1') to concatenate.
            output_filename (str): The filename for the final concatenated output file.

        Raises:
            FileNotFoundError: If any of the input files do not exist.
            subprocess.CalledProcessError: If the FFmpeg command fails.
        """
        if not filenames:
            raise RuntimeError("Error: The list of files to concatenate is empty.")

        dest_path = Path(dest_dir)
        if not dest_path.is_dir():
            raise RuntimeError(f"Error: Destination directory '{dest_dir}' does not exist.")

        # Create full paths for input and output files
        input_paths = [dest_path / f for f in filenames]
        output_path = dest_path / output_filename
        
        # Check if all input files exist
        for p in input_paths:
            if not p.exists():
                raise FileNotFoundError(f"Input file not found: {p}")
        
        # Create a temporary list file within the destination directory
        temp_list_file = dest_path / "temp_file_list.txt"
        with temp_list_file.open("w") as f:
            for path in input_paths:
                f.write(f"file '{path.name}'\n")

        self.log.debug(f"Concatenating {len(filenames)} files in '{dest_dir}' into '{output_path}'...")
        
        try:
            # Construct the FFmpeg command
            command = [
                'ffmpeg', 
                '-f', 'concat', 
                '-safe', '0', 
                '-i', str(temp_list_file.name),  # Use the filename, as we'll run the command in the directory
                '-c', 'copy', 
                str(output_path.name)
            ]
            
            # Execute the command in the specified directory
            subprocess.run(command, check=True, cwd=dest_dir, capture_output=True, text=True)
            self.log.debug("Concatenation successful.")

            # --- Cleanup ---
            # Delete the original source files
            self.log.debug("Deleting original files...")
            for p in input_paths:
                os.remove(p)
            
            # Delete the temporary list file
            self.log.debug("Deleting temporary list file...")
            os.remove(temp_list_file)
            
            self.log.debug("Cleanup complete.")
        except subprocess.CalledProcessError as e:
            self.log.debug(f"FFmpeg command failed with error: {e.stderr}")
            raise e
        finally:
            # Ensure the temporary file is deleted even if an error occurs
            if temp_list_file.exists():
                os.remove(temp_list_file)

    def _valid_duration(self, start_dt: datetime, end_dt: datetime) -> bool:
        """
        Checks if the duration between two datetime objects is within 2 hours.

        Args:
            start_dt (datetime): The start datetime object.
            end_dt (datetime): The end datetime object.

        Returns:
            bool: True if the duration is 2 hours or less, False otherwise.
        """
        # Calculate the duration
        duration = end_dt - start_dt

        # Define the maximum allowed duration
        max_duration = timedelta(hours=2)
        min_duration = timedelta(seconds=1)

        # Check if the duration is less than or equal to the maximum
        if duration <= max_duration and duration >= min_duration:
            return True
        else:
            return False

    def download_by_time(
        self,
        *,
        camera: Optional[int] = 1,
        start: datetime,
        end: datetime,
        stream: str = StreamType.MAIN,
        dest_dir: Union[str, Path] = ".",
        chunk_bytes: int = 1024 * 1024,
        progress: Optional[Callable[[int, Optional[int]], None]] = None,
    ) -> Path:
        """Build a playback URI for [start,end] and download it directly.
        If search results exist, uses the first playback URI from search.
        Otherwise, constructs a standard playbackURI for the given track and times.
        Returns the path to the downloaded file.
        """

        if not self._valid_duration(start_dt=start, end_dt=end):
            raise ValueError("Duration between start and end must be positive and less than or equal to 2 hours.")
        
        if camera is None:
            raise ValueError("Camera must be provided.")
        if camera < 1:
            raise ValueError("Camera must be >= 1")
        track_id = StreamType.to_track_id(camera, stream)
        dest_dir = Path(dest_dir)

        if dest_dir.is_dir() is False:
            raise ValueError(f"Destination directory '{dest_dir}' does not exist or is not a directory.")

        metadata = self.generate_meta_data(start = start, end = end, track_id = track_id)
        filename = f"{metadata}.mp4"
        dest_path_final = dest_dir / filename

        matches: List[SearchMatch] = []
        try:
            print(f"Searching for media...{camera} {start} {end} {stream} {track_id}")
            matches = self._search_media(start=start, end=end, track_id=track_id)
        except Exception as e:
            raise RuntimeError("search_media failed (%s), will fall back to constructed playbackURI", e)
        
        self.log.debug("search_media returned %d matches", len(matches))

        if not matches:
            raise RuntimeError("No search matches found; cannot proceed with download. Possibly the NVR does not support search or has no recordings in the specified time range.")
        
        if dest_path_final.exists():
            print(f"File found in drive")
            return dest_path_final
        
        spaceNeeded = self.__MIN_BUFFER_SIZE
        for match in matches:
            spaceNeeded += 2 * match.size_bytes if match.size_bytes else 0
        if check_free_space(dest_dir) - spaceNeeded < 0:
            raise RuntimeError(f"Not enough space available: {check_free_space(dest_dir)} bytes free, {spaceNeeded} bytes needed")
        
        i = 0
        converted_file_names: List[str] = []
        
        for match in matches:
            i += 1
            playback_uri = match.playback_uri
            track_id = match.track_id or track_id
            chunk_filename = f"{metadata}_{i}.mp4"
            converted_filename = f"{metadata}_{i}_converted.mp4"
                
            dest_path = dest_dir / chunk_filename
            converted_dest_path = dest_dir / converted_filename
            self.log.debug("Downloading match %d to %s", i, dest_path)

            self._download_by_playback_uri(
                playback_uri=playback_uri,
                dest_path=dest_path,
                chunk_bytes=chunk_bytes,
                progress=progress,
            )
            self.log.info("Downloaded %s", dest_path)
            mediaInfo = get_media_info(dest_path)
            self.log.info("Downloaded %s: video=%s, audio=%s, duration=%s (%0.2f sec)", dest_path, mediaInfo.video_codec, mediaInfo.audio_codec, mediaInfo.duration_hms, mediaInfo.duration_seconds)
            trim_params = get_trimming_params(user_start_dt=start, user_end_dt=end, chunk_start_dt=match.start_time, chunk_end_dt=match.end_time)
            if trim_params is None:
                raise RuntimeError(f"Unexpected: no overlap between user [{start} - {end}] and chunk [{match.start_time} - {match.end_time}]")
            convertAndTrim(input_file=str(dest_path), output_file=str(converted_dest_path), mediaInfo=mediaInfo, offsetInSeconds=trim_params[0], durationInSeconds=trim_params[1])
            self.log.info("Converted and trimmed to %s", converted_dest_path)
            converted_file_names.append(converted_dest_path)
            os.remove(dest_path)

        
        self._concatenate_and_cleanup_in_dir(dest_dir=str(dest_dir), filenames=converted_file_names, output_filename=filename)

        return dest_path_final

    def _download_by_playback_uri(
        self,
        *,
        playback_uri: str,
        dest_path: Union[str, Path],
        chunk_bytes: int = 1024 * 1024,
        progress: Optional[Callable[[int, Optional[int]], None]] = None,
    ) -> Path:
        """Download using a playback URI (from search or constructed).

        :param playback_uri: Typically like "/ISAPI/ContentMgmt/record/tracks/101?starttime=...&endtime=..."
        :param dest_path: Path where the clip will be saved.
        :param chunk_bytes: Stream chunk size for writing.
        :param progress: Optional callback(bytes_downloaded, total_bytes or None)
        """
        xml = """<?xml version='1.0' encoding='utf-8'?><downloadRequest>
                <playbackURI></playbackURI>
            </downloadRequest>"""
        request = ElementTree.fromstring(xml)
        pb_uri = request.find('playbackURI')
        pb_uri.text = playback_uri
        request_data = ElementTree.tostring(request, encoding='utf8', method='xml')
        dest_path = Path(dest_path)
        if dest_path.exists():
            return dest_path

        # The /download endpoint expects the playbackURI as a URL-encoded query parameter
        url = self._url(self.__DOWNLOAD_MEDIA_URL)
        self.log.info("Downloading to %s", dest_path)

        with self._request("get", url, data=request_data, headers={"Content-Type": "application/xml"}) as r:
            if r.status_code not in (200, 206):
                raise RuntimeError(f"Download failed: HTTP {r.status_code}: {r.text}")
            total = int(r.headers.get("Content-Length") or 0) or None
            bytes_written = 0
            tmp_path = dest_path.with_suffix(dest_path.suffix + ".part")
            with open(tmp_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=max(4096, chunk_bytes)):
                    if not chunk:
                        continue
                    f.write(chunk)
                    bytes_written += len(chunk)
                    if progress:
                        try:
                            progress(bytes_written, total)
                        except Exception:
                            # don't let UI callbacks break download
                            pass
            tmp_path.replace(dest_path)
        return dest_path

    # ------------------------
    # Internals
    # ------------------------
    def _url(self, path: str) -> str:
        path = "/" + path.lstrip("/")
        return f"{self.scheme}://{self.host}:{self.port}{path}"

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        last_exc: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                r: requests.Response = self.session.request(method=method.upper(), url=url, timeout=self.timeout, **kwargs)
                # Some firmwares send 401 once to trigger digest; requests handles it, but we retry to be safe
                if r.status_code in (401, 503) and attempt < self.max_retries:
                    self._sleep_backoff(attempt)
                    continue
                return r
            except (requests.Timeout, requests.ConnectionError) as e:
                last_exc = e
                if attempt >= self.max_retries:
                    break
                self._sleep_backoff(attempt)
        assert last_exc is not None
        raise last_exc

    def _sleep_backoff(self, attempt: int) -> None:
        delay = (self.backoff_factor ** (attempt - 1)) * 1.2
        self.log.debug("Retrying in %.2fs (attempt %d)", delay, attempt + 1)
        time.sleep(delay)

    def _build_playback_uri(self, track_id: int, start: datetime, end: datetime) -> str:
        params = {
            "starttime": _iso8601(start),
            "endtime": _iso8601(end),
        }
        return f"/ISAPI/ContentMgmt/record/tracks/{track_id}?{urlencode(params)}"
    
    def generate_meta_data(self, start: datetime, end: datetime, track_id: int):
        start_iso = _iso8601(start)
        end_iso = _iso8601(end)
        return f"cam_{track_id}_{start_iso}_{end_iso}"


    def _parse_search_results(self, xml_text: str) -> List[SearchMatch]:
        """Lightweight XML parsing that tolerates minor schema differences."""
        try:
            import xml.etree.ElementTree as ET
        except Exception as e:  # pragma: no cover
            raise RuntimeError(f"XML parser unavailable: {e}")

        answer_text = re.sub(' xmlns="[^"]+"', '', xml_text, count=0)
        root = ET.fromstring(answer_text)
        ns = ""  # ISAPI often uses no XML namespace in body

        def _find_text(node, path_list: Iterable[str]) -> Optional[str]:
            for p in path_list:
                el = node.find(p)
                if el is not None and el.text:
                    return el.text.strip()
            return None

        matches: List[SearchMatch] = []
        for item in root.findall(".//searchMatchItem"):
            # Times
            st_txt = _find_text(item, ["timeSpan/startTime", "startTime"])
            et_txt = _find_text(item, ["timeSpan/endTime", "endTime"])
            try:
                st = self._parse_dt(st_txt) if st_txt else None
                et = self._parse_dt(et_txt) if et_txt else None
            except Exception:
                st, et = None, None

            # playback URI
            pb = _find_text(item, ["mediaSegmentDescriptor/playbackURI", "playbackURI"]) or ""
            sz = getQueryParamFromPlaybackUri(url=pb, param="size")

            # track id (best effort)
            tid_txt = _find_text(item, ["trackID", "mediaSegmentDescriptor/trackID"]) or None
            try:
                tid = int(tid_txt) if tid_txt else None
            except Exception:
                tid = None

            # file path (optional)
            file_path = _find_text(item, ["filePath", "mediaSegmentDescriptor/filePath"]) or None

            if pb:
                matches.append(
                    SearchMatch(
                        start_time=st or datetime.fromtimestamp(0, tz=timezone.utc),
                        end_time=et or datetime.fromtimestamp(0, tz=timezone.utc),
                        track_id=tid,
                        playback_uri=pb,
                        file_path=file_path,
                        size_bytes=int(sz) if sz and sz.isdigit() else None,
                    )
                )
        print(matches)
        return matches

    @staticmethod
    def _parse_dt(txt: str) -> datetime:
        # Accept both Z and offset forms
        # Examples: 2025-08-24T10:00:00Z or 2025-08-24T15:30:00+05:30
        try:
            if txt.endswith("Z"):
                dt = datetime.strptime(txt, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            else:
                # Python 3.11: fromisoformat supports offsets like "+05:30"
                dt = datetime.fromisoformat(txt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            # Last resort: treat as UTC naive
            return datetime.strptime(txt[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)


# ----------------------------
# Optional CLI (python -m ...)
# ----------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Hikvision NVR clip downloader (ISAPI)")
    parser.add_argument("host", help="NVR IP/hostname")
    parser.add_argument("username", help="NVR username")
    parser.add_argument("password", help="NVR password")
    parser.add_argument("start", help="Start time (ISO8601, e.g., 2025-08-24T10:00:00Z)")
    parser.add_argument("end", help="End time   (ISO8601, e.g., 2025-08-24T10:05:00Z)")
    parser.add_argument("--camera", type=int, default=1, help="Camera number (1..N)")
    parser.add_argument("--stream", default=StreamType.MAIN, choices=[StreamType.MAIN, StreamType.SUB])
    parser.add_argument("--port", type=int, default=80, help="ISAPI port (default 80)")
    parser.add_argument("--scheme", default="http", choices=["http", "https"])
    parser.add_argument("--out", default=".", help="Output directory")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    log = logging.getLogger("hikvision_cli")
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    log.addHandler(h)
    log.setLevel(logging.DEBUG if args.verbose else logging.INFO)

    def _parse_iso(s: str) -> datetime:
        # Try fromisoformat first
        try:
            if s.endswith("Z"):
                return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)

    start_dt = _parse_iso(args.start)
    end_dt = _parse_iso(args.end)

    client = HikvisionNVRClient(
        host=args.host,
        username=args.username,
        password=args.password,
        port=args.port,
        scheme=args.scheme,
    )

    def progress_cb(done: int, total: Optional[int]) -> None:
        if total:
            pct = done * 100 // total
            print(f"\rDownloaded {done}/{total} bytes ({pct}%)", end="")
        else:
            print(f"\rDownloaded {done} bytes", end="")

    path = client.download_by_time(
        camera=args.camera,
        start=start_dt,
        end=end_dt,
        stream=args.stream,
        dest_dir=args.out,
        progress=progress_cb,
    )
    print(f"\nSaved to {path}")
