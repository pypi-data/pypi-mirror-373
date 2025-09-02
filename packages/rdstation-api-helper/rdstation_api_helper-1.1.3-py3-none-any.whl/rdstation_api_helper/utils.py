"""
Utility functions for the RD Station API driver module.
"""
import json
import logging
import os
import re
import requests
import threading
import time

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Optional

from .exceptions import ConfigurationError


def load_credentials(config_path: Optional[str] = None) -> dict[str, Any]:
    """
    Load RD Station API credentials from JSON file.

    Args:
        config_path (Optional[str]): Path to the credentials file. If None, tries default locations.

    Returns:
        dict[str, Any]: Loaded credentials configuration

    Raises:
        FileNotFoundError: If credentials file is not found
        json.JSONDecodeError: If JSON parsing fails
    """
    default_paths = [
        os.path.join("secrets", "fb_business_config.json"),
        os.path.join(os.path.expanduser("~"), ".fb_business_config.json"),
        "fb_business_config.json"
    ]

    if config_path:
        paths_to_try = [config_path]
    else:
        paths_to_try = default_paths

    for path in paths_to_try:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    credentials = json.load(f)

                if not credentials:
                    raise ConfigurationError(f"Credentials file {path} is empty")

                if not isinstance(credentials, dict):
                    raise ConfigurationError(f"Credentials file {path} must contain a JSON dictionary")

                return credentials

            except json.JSONDecodeError as e:
                logging.error(f"Error parsing JSON file {path}: {e}")
                raise ConfigurationError(
                    f"Invalid JSON format in credentials file {path}",
                    original_error=e
                ) from e
            except IOError as e:
                raise ConfigurationError(
                    f"Failed to read credentials file {path}",
                    original_error=e
                ) from e

    raise ConfigurationError(
        f"Could not find credentials file in any of these locations: {paths_to_try}"
    )


def create_output_directory(path: str) -> Path:
    """
    Create output directory if it doesn't exist.

    Args:
        path (str): Directory path to create

    Returns:
        Path: Path object for the created directory
    """
    output_path = Path(path)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def load_from_json_file(filepath: str) -> list[dict[str, Any]]:

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    logging.info(f"Data loaded from `{filepath}`")
    return data  # type: ignore[no-any-return]


def save_to_json_file(json_data: list[dict[str, Any]], filepath: str) -> None:

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2, default=str)

    logging.info(f"Data saved to `{filepath}`")


def append_to_json_file(json_data: list[dict[str, Any]], filepath: str) -> None:
    try:
        if os.path.exists(filepath):
            with open(filepath, "r+", encoding="utf-8") as f:

                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    logging.info(
                        "JSON decode error: File is empty or invalid. Aborting operation."
                    )
                    return

                if not isinstance(data, list):
                    logging.info("Existing JSON structure is not a list. Aborting operation.")
                    return
                logging.info(f"Found {len(data)} records in the file.")

                if isinstance(json_data, list):
                    data.extend(json_data)
                    logging.info(f"Appending {len(json_data)} record(s).")

                else:
                    data.append(json_data)
                    logging.info("Appending 1 record.")

                f.seek(0)
                json.dump(data, f, indent=2)
                f.truncate()
            logging.info(
                f"Records [{len(data):,}] appended successfully to file `{filepath}`."
            )

        else:
            with open(filepath, "w", encoding="utf-8") as f:
                if isinstance(json_data, list):
                    data = json_data
                    logging.info(
                        f"Creating new file `{filepath}` and adding {len(json_data)} record(s)."
                    )
                else:
                    data = [json_data]
                    logging.info(f"Creating new `{filepath}` file and adding 1 record.")
                json.dump(data, f, indent=2)
            logging.info("File created and records added successfully.")

    except Exception as e:
        logging.info("An error occurred:", e)


def parallel_decorator(max_workers: int = 5, sleep_time: float = 10, key_parameter: str = "uuid") -> Any:
    """
    Decorator to parallelize a functions that fetches data for a single item (uuid).
    The decorated function should return (status_code, data).
    The decorated function can be called with a list of dicts (each with key_parameter),
    and will return a list of results, handling 429/5xx/network errors with a barrier.
    """
    def decorator(inner_method: Any) -> Any:
        @wraps(inner_method)
        def wrapper(self: Any, key_list: list[str], *args: Any, **kwargs: Any) -> tuple[None, list[Any]]:
            """
            key_list: list of key values (e.g., uuids or emails)
            """
            all_results = []
            item_count = 0
            list_length = len(key_list)

            # Shared event and lock for barrier
            sleep_event = threading.Event()
            sleep_lock = threading.Lock()
            sleep_until: list[float] = [0.0]  # mutable container for timestamp

            def barrier(wait_time: float) -> None:
                with sleep_lock:
                    now = time.time()
                    target = now + wait_time
                    if target > sleep_until[0]:
                        sleep_until[0] = target
                    sleep_event.set()
                while True:
                    now = time.time()
                    remaining = sleep_until[0] - now
                    if remaining <= 0:
                        break
                    time.sleep(min(1, remaining))
                sleep_event.clear()

            def fetch(key_value: str) -> Any:
                while True:
                    try:
                        code, data = inner_method(self, key_value, *args, **kwargs)
                        status_code = int(code)
                    except requests.exceptions.RequestException as e:
                        logging.warning(
                            f"Network error for {key_value}: {e}. Sleeping all workers for {sleep_time} sec."
                        )
                        barrier(sleep_time)
                        continue
                    except Exception as e:
                        logging.warning(f"Unexpected error for {key_value}: {e}")
                        return None

                    if status_code == 200:
                        if data:
                            if isinstance(data, dict):
                                data[key_parameter] = key_value
                            elif isinstance(data, list):
                                for item in data:
                                    if isinstance(item, dict):
                                        item[key_parameter] = key_value
                        return data

                    elif status_code == 429 or (500 <= status_code < 600):
                        logging.warning(
                            f"Worker for {key_value} got status {status_code}, sleeping all workers for {sleep_time} sec."  # noqa
                        )
                        barrier(sleep_time)
                    else:
                        logging.info(
                            f"Failed to fetch {key_value}, HTTP {status_code}. Skipping."
                        )
                        return None

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(fetch, str(key_value)): key_value for key_value in key_list}
                for future in as_completed(futures):
                    result = future.result()

                    contact_id = None

                    if result:
                        if isinstance(result, dict):
                            all_results.append(result)
                            contact_id = result.get(key_parameter, 'N/A')
                        elif isinstance(result, list):
                            all_results.extend(result)
                            contact_id = result[0].get(key_parameter, 'N/A')

                    item_count += 1

                    logging.info(
                        f"{item_count}/{list_length} - fetched {inner_method.__name__} for contact '{contact_id}'")

            logging.info(f"Fetched {len(all_results)} total items.")

            return None, all_results
        return wrapper
    return decorator


def get_webhook_events(start_date: str, end_date: Optional[str], conn,  # psycopg2 connection
                       table_name: str = 'rd_webhook_v1', schema: str = 'public',
                       api_version: str = 'v1') -> list[dict[str, Any]]:
    """
    Fetch webhook events from SQL Table within a specified date range.
    Parameters:
        start_date (str): Start date in ISO format (YYYY-MM-DD).
        end_date (Optional[str]): End date in ISO format (YYYY-MM-DD). If None, uses today's date.
    Returns:
        list[dict[str, Any]]: List of webhook event objects.
    """
    if api_version == 'v1':
        # For v1, extract 'created_at' from the JSONB column 'last_conversion'->'content'->>'created_at'
        timestamp_column = "(last_conversion->'content'->>'created_at')"
    else:
        timestamp_column = 'event_timestamp'

    # Validate table_name if user input (security)
    if not re.match(r'^[A-Za-z0-9_]+$', table_name):
        raise ValueError("Invalid table name.")

    if end_date is None:
        end_date = datetime.today().strftime("%Y-%m-%d")

    # Check if start_date and end_date are valid ISO date strings (YYYY-MM-DD)
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("start_date or end_date is not a valid ISO date (YYYY-MM-DD).")

    # Add time boundaries to start_date and end_date
    start_datetime = f"{start_date} 00:00:00"
    end_datetime = f"{end_date} 23:59:59"

    # Build query string
    query = (
        f"SELECT * FROM {schema}.{table_name} "
        f"WHERE {timestamp_column}::timestamp >= %s AND {timestamp_column}::timestamp <= %s "
    )

    # Use start_datetime and end_datetime as parameters
    with conn.cursor() as cur:
        cur.execute(query, (start_datetime, end_datetime))
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        results = [dict(zip(columns, row)) for row in rows]
    return results
