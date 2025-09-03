import hashlib
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def generate_etag(file_path, chunk_size=128 * hashlib.md5().block_size):
    file_hash = hashlib.md5()

    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                file_hash.update(chunk)
        return file_hash.hexdigest()
    except IOError as e:
        raise IOError(f"Error reading file {file_path}: {e}")


def upload_part(i, file_path, url, part_size, total_parts, progress_tracker, prefix_message, max_retries=3):
    """Uploads a single part, creating a new session for each request, updating progress with retry and delay."""
    percent_complete = (progress_tracker["completed_parts"] / total_parts) * 100
    print(f"\x1b[1K\r{prefix_message}: {percent_complete:.2f}% complete", end="", flush=True)
    retries = 0

    while retries <= max_retries:
        try:
            with open(file_path, "rb") as f:
                f.seek(i * part_size)
                part_data = f.read(part_size)

            # Create a new session for each request
            with requests.Session() as session:
                response = session.put(url, data=part_data)
                response.raise_for_status()  # Raise an exception for any HTTP error

            e_tag = response.headers["ETag"]
            progress_tracker["completed_parts"] += 1
            percent_complete = (progress_tracker["completed_parts"] / total_parts) * 100
            print(f"\x1b[1K\r{prefix_message}: {percent_complete:.2f}% complete", end="", flush=True)
            return {"partNumber": i + 1, "eTag": e_tag}

        except requests.RequestException as e:
            if retries == max_retries:
                raise Exception(f"Failed to upload part {i+1} after {retries} attempts. Error: {e}")

            print(f"\n\033[91m{prefix_message}: Attempt {retries + 1} failed with error", flush=True)
            print(f"{e}. ", flush=True)
            print("Retrying in 30 seconds...\033[0m", flush=True)
            time.sleep(30)  # Wait 30 seconds before retrying
            retries += 1


def multipart_upload_file(file_path, part_size, urls, prefix_message):
    if len(urls) > 0:
        parts = []
        total_parts = len(urls)
        progress_tracker = {"completed_parts": 0}

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = []
            for i, url in enumerate(urls):
                futures.append(
                    executor.submit(
                        upload_part, i, file_path, url, part_size, total_parts, progress_tracker, prefix_message
                    )
                )

            for future in as_completed(futures):
                parts.append(future.result())

        print(f"\x1b[1K\r{prefix_message}: upload complete.", end="", flush=True)
        return parts
    else:
        with open(file_path, "rb") as filebytes:
            files = {"file": filebytes}
            url = urls[0]
            response = requests.put(url, files=files)
            if response.status_code != 204:
                raise Exception(f"Failed to upload, with status code: {response.status_code}")
        print(f"\x1b[1K\r{prefix_message}: upload complete.", end="", flush=True)
        return []
