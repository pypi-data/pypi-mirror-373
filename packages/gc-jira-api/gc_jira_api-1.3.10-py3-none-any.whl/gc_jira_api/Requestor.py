import json
import logging
import time

import requests
from requests.auth import HTTPBasicAuth

from gc_jira_api.exceptions.JiraException import JiraException

JIRA_BASE_ENDPOINT = "rest/api/3"
MAX_RETRIES = 3
BACKOFF_FACTOR = 2
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}
HEADER_RETRY_CODE = 429  # Too Many Requests


class RequestExecutor:
    def __init__(self, jira_username, jira_password, jira_server):
        self.jira_server = jira_server

        self.auth = HTTPBasicAuth(jira_username, jira_password)

    def _dict_to_query_string(self, dictionary: dict):
        query_string = "?"

        for key, value in dictionary.items():
            query_string += f"{key}={value}&"

        if query_string[-1] == "&":
            query_string = query_string[:-1]

        return query_string

    def fetch_data(
        self,
        url: str,
        url_params: dict = {},
        is_absolute_url=False,
        method="GET",
    ):
        if not is_absolute_url:
            url = f"{self.jira_server}/{JIRA_BASE_ENDPOINT}/{url}"

        next_url = url
        all_records = []
        while next_url:
            response = self._make_request(next_url, url_params, 0, method)
            if response:
                data = response.json()
                if isinstance(data, dict) and "values" in data.keys():
                    all_records.extend(data["values"])

                    if "nextPage" in data:
                        next_url = data["nextPage"]

                    elif "isLast" in data and not data["isLast"]:
                        start_at = data.get("startAt", 0) + data.get(
                            "maxResults", 0
                        )
                        next_url = f"{url}?startAt={start_at}"

                    else:
                        next_url = None

                else:
                    next_url = None
                    all_records = data
            else:
                next_url = None

        return all_records

    def _make_request(self, url, url_params, retry_count, method):
        try:
            if method == "PUT":
                response = requests.put(
                    url,
                    headers=HEADERS,
                    # timeout=10,
                    auth=self.auth,
                    json=url_params,
                )
            elif method == "POST":
                response = requests.post(
                    url,
                    headers=HEADERS,
                    # timeout=10,
                    auth=self.auth,
                    # data=url_params,
                    data=json.dumps(url_params),
                )
            elif method == "DELETE":
                response = requests.delete(
                    url,
                    headers=HEADERS,
                    # timeout=10,
                    auth=self.auth,
                    # data=url_params,
                    # data=json.dumps(url_params),
                )
            else:
                response = requests.get(
                    url,
                    headers=HEADERS,
                    # timeout=10,
                    auth=self.auth,
                    params=url_params,
                )

            if response.status_code != 200:
                logging.error(
                    f"[ERROR - _make_request]: Request to {url} failed with status code {response.status_code} and response: {response.text}"  # noqa: E501
                )

            if response.status_code == HEADER_RETRY_CODE:
                retry_after = response.headers.get("Retry-After")
                if retry_after is not None and retry_count < MAX_RETRIES:
                    wait_seconds = int(retry_after)
                    logging.warning(
                        f"[ERROR - _make_request]: Code {response.status_code}. Waiting {wait_seconds} seconds according to Retry-After header"  # noqa: E501
                    )
                    time.sleep(wait_seconds)
                    logging.info(
                        f"[INFO - _make_request]: Retrying request to {url} (retry count: {retry_count + 1})"  # noqa: E501
                    )
                    # Retry the request with incremented retry count
                    return self._make_request(
                        url, url_params, retry_count + 1, method
                    )

            response.raise_for_status()

            return response
        except (
            requests.exceptions.Timeout,
            requests.exceptions.TooManyRedirects,
            requests.exceptions.RequestException,
        ) as e:
            if retry_count >= MAX_RETRIES:
                logging.error(
                    f"[ERROR - _make_request]: Request failed after {MAX_RETRIES} attempts due to: {e}"  # noqa: E501
                )

                raise JiraException(f"Error making Jira request: {e}")
            next_seconds = BACKOFF_FACTOR**retry_count
            logging.warning(
                f"[ERROR - _make_request]: Request timeout or too many redirects, retrying in {next_seconds} seconds ({url})"  # noqa: E501
            )
            time.sleep(next_seconds)

            return self._make_request(url, url_params, retry_count + 1, method)
