# Hikvision NVR Clip Downloader
A robust, flexible Python library for searching and downloading recorded video clips from a Hikvision NVR using the **ISAPI** endpoints.

This library simplifies the process of retrieving video footage by handling authentication, time-based search, and precise trimming, ensuring you get exactly the clip you need.

## ✨ Key Features
* **Robust Authentication:** Utilizes `requests` with `HTTPDigestAuth` for secure communication.

* **Flexible Parameters:** Easily specify the camera channel and stream type (main/sub).

* **Time-Based Downloads:** Search and download clips based on a precise start and end time range.

* **Intelligent Trimming:** The library automatically trims the downloaded video chunks to the exact duration requested by the user, even if the requested clip spans across multiple recording chunks on the NVR.

* **Resilient Downloads:** Supports resumable (idempotent) downloads with built-in retries and exponential backoff for reliable operation.

* **Clean Output:** Converts downloaded video streams to the widely compatible `.mp4` format.

* **Highly Configurable:** Provides sensible defaults while allowing you to override port, scheme, and other parameters.

## 🚀 Getting Started

### Prerequisites
* **Python 3.7**
* **FFmpeg** must be installed and available in your system's PATH. This library uses FFmpeg for video processing.

FFmpeg must be installed and available in your system's PATH. This library uses FFmpeg for video processing.

### Installation
Install the package directly from PyPI using pip:

```Bash```
```
pip install hikvision-nvr-downloader
```

## 💻 Usage
To use the library, simply import the HikvisionNVRClient class into your Python script.

### Basic Example

```Python```
```
from hikvision_nvr_downloader import HikvisionNVRClient
from datetime import datetime, timezone

# Define NVR connection details
HOST = "192.168.1.4"
USERNAME = "admin"
PASSWORD = "yourpassword"

# Define the clip you want to download
START_TIME = datetime(2025, 8, 24, 10, 0, 0, tzinfo=timezone.utc)
END_TIME = datetime(2025, 8, 24, 10, 5, 0, tzinfo=timezone.utc)
CAMERA_NUM = 1
OUTPUT_DIR = "./downloads"

# Create a client instance
client = HikvisionNVRClient(
    host=HOST,
    username=USERNAME,
    password=PASSWORD
)

# Download the clip
try:
    downloaded_path = client.download_by_time(
        camera=CAMERA_NUM,
        start=START_TIME,
        end=END_TIME,
        dest_dir=OUTPUT_DIR
    )
    print(f"Clip successfully downloaded to: {downloaded_path}")
except ValueError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
```

### Command-Line Usage
The package can still be used directly from the command line for quick downloads.

```Bash```
```
python -m hikvision_nvr_downloader.hikvision_nvr_downloader host username password start end
```

### Example:
```
python -m hikvision_nvr_downloader.hikvision_nvr_downloader 192.168.1.4 admin yourpassword 2025-08-24T10:00:00Z 2025-08-24T10:05:00Z
```
[!Note]
All command-line times must be provided in ISO 8601 UTC format, indicated by the Z suffix.

### Command-Line Arguments
These are the arguments passed when running the script from your terminal (e.g., ```python -m hikvision_nvr_downloader ...```).

1. ```--camera```:
    * **Purpose**: Specifies the physical camera number you want to download from.
    * **Usage**: You provide an integer (e.g., ```--camera 1```). The script then converts this to the appropriate ```trackID``` for the Hikvision ISAPI.

2. ```--stream```:
    * **Purpose**: Determines whether to download the main or sub video stream.
    * **Usage**: You provide either ```main``` or ```sub```. Main streams typically offer higher resolution and bitrate, while sub streams are lower quality but require less bandwidth.

3. ```--port```:
    * **Purpose**: Specifies the port number the NVR's ISAPI is listening on.
    * **Usage**: You provide an integer (e.g., ```--port 8000```). The default is ```80``` for HTTP, but many installations use a different port.

4. ```--scheme```:
    * **Purpose**: Specifies the protocol used to communicate with the NVR.
    * **Usage**: You provide either ```http``` or ```https```. Most NVRs use ```http``` by default unless configured for secure communication.

5. ```--out```:
    * **Purpose**: Sets the destination directory for the downloaded video clip.
    * **Usage**: You provide a file path (e.g., ```--out ./my_downloads```). The default is the current directory (```.```).

6. ```--verbose```:
    * **Purpose**: Enables verbose logging.
    * **Usage**: This is a flag, so you just add it to the command. It provides more detailed output, which is useful for debugging connection or download issues.

### Python Library Parameters
These are the parameters used when creating an instance of the HikvisionNVRClient class or calling its methods in your own Python script.

* ```host```, ```username```, ```password```:
    * **Purpose**: Used to initialize the ```HikvisionNVRClient``` class with the NVR's credentials and address.
    * **Usage**: Passed as arguments to the ```HikvisionNVRClient()``` constructor.

* ```port```, ```scheme```:
    * **Purpose**: Configures the network connection for the client.
    * **Usage**: These are optional keyword arguments for the ```HikvisionNVRClient()``` constructor.

* ```camera```:
    * **Purpose**: Specifies the camera number for the download method.
    * **Usage**: Passed as an argument to the ```download_by_time()``` method (e.g., ```client.download_by_time(camera=1, ...```).

* ```stream```:
    * **Purpose**: Defines the video stream to download.
    * **Usage**: Passed as an argument to the ```download_by_time()``` method (e.g., ```client.download_by_time(stream="main", ...```).

* ```dest_dir```:
    * **Purpose**: Sets the destination folder for the downloaded video file.
    * **Usage**: Passed as an argument to the ```download_by_time()``` method (e.g., ```client.download_by_time(dest_dir="./output"```).

* ```logger```:
    * **Purpose**: Allows you to pass a custom Python logger instance to the client for full control over logging output and format.
    * **Usage**: An optional keyword argument for the ```HikvisionNVRClient()``` constructor.

## 🤝 Contributing
We welcome contributions! If you would like to help improve this project, please follow these steps:

* **Fork** the repository.

* **Create a new branch** for your feature or bug fix.

* **Commit** your changes with a clear and descriptive message.

* **Push** your branch to your forked repository.

* **Submit a pull request** describing your changes.

## 📄 License
This project is licensed under the **MIT License**.


