"""
RD Station API Helper
"""
import logging
import base64
import json
import os
import re
import requests
import time

from dotenv import load_dotenv
from typing import Optional, Any
from urllib.parse import unquote

from .utils import save_to_json_file, parallel_decorator

load_dotenv()


class RDStationAPI:
    """
    Main interface for interacting with the RD Station API.

    Provides methods for authentication, fetching segmentations, contacts, events, and funnel status,
    as well as utilities for batch processing and decoding data.
    """

    def __init__(self) -> None:
        """
        Initialize the RDStationAPI instance and load credentials from environment variables.
        Automatically fetches an access token for API requests.
        """
        self.RD_CLIENT_ID = os.getenv("RDSTATION_CLIENT_ID")
        self.RD_CLIENT_SECRET = os.getenv("RDSTATION_CLIENT_SECRET")
        self.RD_REFRESH_TOKEN = os.getenv("RDSTATION_REFRESH_TOKEN")
        self.RD_API_TOKEN = self.get_access_token()

    def get_access_token(self) -> str:
        """
        Obtain a new access token from RD Station using the refresh token.

        Returns:
            str: The new access token.

        Raises:
            AuthenticationError: If authentication fails or the API returns an error.
            APIError: For other API-related errors.
        """
        import requests
        from .exceptions import AuthenticationError, APIError

        url = "https://api.rd.services/auth/token"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        data = {
            "client_id": self.RD_CLIENT_ID,
            "client_secret": self.RD_CLIENT_SECRET,
            "refresh_token": self.RD_REFRESH_TOKEN,
            "grant_type": "refresh_token",
        }

        try:
            response = requests.post(url, headers=headers, json=data)
        except requests.exceptions.RequestException as e:
            raise APIError("Failed to connect to RD Station API for token refresh.", original_error=e)

        if response.status_code == 200:
            token = response.json().get("access_token")
            if not token:
                raise AuthenticationError("No access_token found in RD Station API response.")
            return str(token)

        elif response.status_code == 400:
            raise AuthenticationError(f"Authentication failed: {response.text}")

        else:
            raise APIError(f"Unexpected error from RD Station API: {response.status_code} - {response.text}")

    def get_segmentations(self, save_json_file: bool = False) -> list[dict[str, Any]]:
        """
        Fetch all segmentations from the RD Station API.

        Parameters:
            save_json_file (bool): If True, saves the results to 'rd_segmentations.json'.

        Returns:
            list[dict[str, Any]]: List of segmentation objects.
        """
        logging.info("Fetching segmentations...")

        url = "https://api.rd.services/platform/segmentations"
        params: dict[str, int] = {"page": 1, "page_size": 100}
        headers = {"Authorization": f"Bearer {self.RD_API_TOKEN}"}

        all_results = []

        while True:
            response = requests.get(url, headers=headers, params=params)

            if response.status_code != 200:
                logging.info(f"Error: {response.status_code}")
                break

            data = response.json()
            segmentations = data.get("segmentations", [])
            num_items = len(segmentations)

            logging.info(f"Page {params['page']} - Found {num_items} items")

            # Add current page's data to the results
            all_results.extend(segmentations)

            current_page = params["page"]
            params["page"] = current_page + 1  # Increment the page number

            if num_items < 100:  # Break if no items was less than a full page
                break

        logging.info(f"Fetched {len(all_results)} total items.")

        if save_json_file:
            save_to_json_file(all_results, "rd_segmentations.json")

        return all_results

    def get_segmentation_contacts(self, segmentation_list: list[dict[str, Any]],
                                  limit: int = 100, sleep_time: float = 0.6,
                                  save_json_file: bool = False) -> list[dict[str, Any]]:
        """
        Fetch contacts for each segmentation from the RD Station API.

        Parameters:
            segmentation_list (list[dict[str, Any]]): List of segmentations to fetch contacts for.
            limit (int): Number of contacts per page (default 100).
            sleep_time (float): Time to sleep between requests to avoid rate limits (default 0.6s).
            save_json_file (bool): If True, saves the results to 'rd_segmentation_contacts.json'.

        Returns:
            list[dict[str, Any]]: List of segmentation contact objects.
        """
        dict_count = 0
        dict_length = len(segmentation_list)

        all_results = []

        for item in segmentation_list:
            logging.info(f"Processing segmentation: {item['id']} - {item['name']}")

            dict_count += 1
            contact_count = 0

            segmentation_id = item["id"]
            segmentation_name = item["name"]

            url = f"https://api.rd.services/platform/segmentations/{segmentation_id}/contacts"
            params: dict[str, Any] = {"page": 1, "page_size": limit, "order": "last_conversion_date"}
            headers = {"Authorization": f"Bearer {self.RD_API_TOKEN}"}

            while True:
                req = requests.Request("GET", url, headers=headers, params=params).prepare()
                logging.debug(f"Requesting: {req.url}")

                response = requests.get(url, headers=headers, params=params)

                if response.status_code != 200:
                    logging.info(f"Error: {response.status_code}")
                    break

                data = response.json()

                contacts = data.get("contacts", [])
                num_items = len(contacts)
                contact_count += num_items

                logging.info(
                    f"{dict_count}/{dict_length} - id: {segmentation_id}, p.{params['page']}, found {contact_count} items"  # noqa
                )

                # Append segmentation_id and segmentation_name to each contact
                for contact in contacts:
                    contact["segmentation_id"] = segmentation_id
                    contact["segmentation_name"] = segmentation_name

                # Add current page's data to the results
                all_results.extend(contacts)

                current_page = params["page"]
                params["page"] = current_page + 1  # Increment the page number

                if num_items < limit:  # Break if no items was less than a full page
                    break

                # Sleep for 0.5 seconds to respect 2 requests per second
                time.sleep(sleep_time)

        logging.info(f"Fetched {len(all_results)} total items.")

        if save_json_file:
            save_to_json_file(all_results, "rd_segmentation_contacts.json")

        return all_results

    def get_contact_data(self, uuid_value: str) -> tuple[int, Optional[list[dict[str, Any]]]]:
        """
        Fetch a single contact's data from the RD Station API.

        Parameters:
            uuid_value (str): The UUID of the contact to fetch.

        Returns:
            tuple[int, Optional[list[dict[str, Any]]]]: Status code and contact data (as a list or None).
        """
        url = f"https://api.rd.services/platform/contacts/{uuid_value}"
        headers = {"Authorization": f"Bearer {self.RD_API_TOKEN}"}

        try:
            response = requests.get(url, headers=headers)

            return response.status_code, response.json()

        except requests.exceptions.RequestException as e:
            logging.info(f"Request failed for {uuid_value}: {e}.")
            raise

    @parallel_decorator(max_workers=3, sleep_time=20, key_parameter="uuid")
    def get_contact_data_parallel(self, uuid_value: str) -> tuple[int, Optional[list[dict[str, Any]]]]:
        """
        Parallelized version of get_contact_data for batch processing.

        Parameters:
            uuid_value (str): The UUID of the contact to fetch.

        Returns:
            tuple[int, Optional[list[dict[str, Any]]]]: Status code and contact data.
        """
        return self.get_contact_data(uuid_value)

    def get_contact_events(self, uuid_value: str) -> tuple[int, Optional[list[dict[str, Any]]]]:
        """
        Fetch conversion events for a single contact and process traffic_source and UTM parameters.

        Parameters:
            uuid_value (str): The UUID of the contact to fetch events for.

        Returns:
            tuple[int, Optional[list[dict[str, Any]]]]: Status code and processed event data.
        """
        url = f"https://api.rd.services/platform/contacts/{uuid_value}/events?event_type=CONVERSION"
        headers = {"Authorization": f"Bearer {self.RD_API_TOKEN}"}

        def decode_traffic_source(encoded_str: str) -> Optional[dict[str, Any]]:
            try:
                # Remove 'encoded_' prefix if present
                if encoded_str.startswith("encoded_"):
                    encoded_str = encoded_str[len("encoded_"):]
                # Add padding if needed
                missing_padding = len(encoded_str) % 4
                if missing_padding:
                    encoded_str += '=' * (4 - missing_padding)
                decoded_bytes = base64.b64decode(encoded_str)
                decoded_str = decoded_bytes.decode("utf-8")
                decoded_data = json.loads(decoded_str)
                return decoded_data if isinstance(decoded_data, dict) else None
            except Exception as e:
                logging.info(f"Failed to decode traffic_source: {e}")
                return None

        def extract_utm_params(traffic_source_string: Optional[str]) -> dict[str, Optional[str]]:
            utm_keys = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"]
            utm_dict: dict[str, Optional[str]] = {k: None for k in utm_keys}
            if not traffic_source_string:
                return utm_dict
            # Split by '&', then '='
            for part in traffic_source_string.split('&'):
                if '=' in part:
                    k, v = part.split('=', 1)
                    if k in utm_dict:
                        utm_dict[k] = v
            return utm_dict

        try:
            response = requests.get(url, headers=headers)
            status_code = response.status_code
            data = response.json()

            if not isinstance(data, list):
                data = [data]

            processed = []
            for item in data:
                payload = item.get("payload", {})
                traffic_source_encoded = payload.pop("traffic_source", None)
                traffic_source_decoded = (
                    decode_traffic_source(traffic_source_encoded)
                    if traffic_source_encoded else None
                )
                if traffic_source_decoded:
                    item["traffic_source"] = traffic_source_decoded
                    # Extract UTM params from current_session.value
                    current_session = traffic_source_decoded.get("current_session", {})
                    utm_values = extract_utm_params(current_session.get("value"))
                    for k, v in utm_values.items():
                        if v is not None:
                            item[k] = self.decode_if_needed(v)

                processed.append(item)

            return status_code, processed

        except requests.exceptions.RequestException as e:
            logging.info(f"Request failed for {uuid_value}: {e}.")
            raise

    @parallel_decorator(max_workers=3, sleep_time=20, key_parameter="uuid")
    def get_contact_events_parallel(self, uuid_value: str) -> tuple[int, Optional[list[dict[str, Any]]]]:
        """
        Parallelized version of get_contact_events for batch processing.

        Parameters:
            uuid_value (str): The UUID of the contact to fetch events for.

        Returns:
            tuple[int, Optional[list[dict[str, Any]]]]: Status code and processed event data.
        """
        return self.get_contact_events(uuid_value)

    def get_contact_funnel_status(self, uuid_value: str) -> tuple[int, Optional[list[dict[str, Any]]]]:
        """
        Fetch the funnel status for a single contact from the RD Station API.

        Parameters:
            uuid_value (str): The UUID of the contact to fetch funnel status for.

        Returns:
            tuple[int, Optional[list[dict[str, Any]]]]: Status code and funnel status data.
        """
        url = f"https://api.rd.services/platform/contacts/{uuid_value}/funnels/default"
        headers = {"Authorization": f"Bearer {self.RD_API_TOKEN}"}

        try:
            response = requests.get(url, headers=headers)

            return response.status_code, response.json()

        except requests.exceptions.RequestException as e:
            logging.info(f"Request failed for {uuid_value}: {e}.")
            raise

    @parallel_decorator(max_workers=3, sleep_time=20, key_parameter="uuid")
    def get_contact_funnel_status_parallel(self, uuid_value: str) -> tuple[int, Optional[list[dict[str, Any]]]]:
        """
        Parallelized version of get_contact_funnel_status for batch processing.

        Parameters:
            uuid_value (str): The UUID of the contact to fetch funnel status for.

        Returns:
            tuple[int, Optional[list[dict[str, Any]]]]: Status code and funnel status data.
        """
        return self.get_contact_funnel_status(uuid_value)

    @staticmethod
    def process_in_batches(all_data: list, batch_size: int = 500) -> Any:
        """
        Generator to yield batches of data for processing.

        Parameters:
            all_data (list): The complete list of data to batch.
            batch_size (int): The size of each batch (default 500).

        Yields:
            list: A batch of data.
        """
        for i in range(0, len(all_data), batch_size):
            yield all_data[i: i + batch_size]

    @staticmethod
    def decode_if_needed(text_string: str) -> str:
        """
        Decode a string that may be percent-encoded and/or contain Unicode escape sequences.

        Parameters:
            text_string (str): The input string that may be encoded.

        Returns:
            str: The fully decoded string.
        """
        # Decode percent-encoded sequences if present.
        if re.search(r"%[0-9A-Fa-f]{2}", text_string):
            text_string = unquote(text_string)

        # Decode Unicode escapes if the literal "\u" is found.
        if "\\u" in text_string:
            try:
                text_string = text_string.encode("utf-8").decode("unicode_escape")
            except Exception as e:
                logging.info("Unicode escape decoding failed:", e)

        return text_string
