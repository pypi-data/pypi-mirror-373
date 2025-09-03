import json
import unittest
from unittest.mock import Mock, patch

from requests.auth import HTTPBasicAuth
from requests.models import Response

from gc_jira_api.Requestor import HEADERS, JIRA_BASE_ENDPOINT, RequestExecutor


class TestRequestExecutor(unittest.TestCase):
    def setUp(self):
        self.jira_username = "username"
        self.jira_password = "password"
        self.jira_server = "https://jira.example.com"
        self.executor = RequestExecutor(
            self.jira_username, self.jira_password, self.jira_server
        )

    def test_dict_to_query_string(self):
        query_dict = {"key1": "value1", "key2": "value2"}
        result = self.executor._dict_to_query_string(query_dict)
        expected = "?key1=value1&key2=value2"

        self.assertEqual(result, expected)

    @patch("gc_jira_api.Requestor.requests.get")
    def test_fetch_data(self, mock_get):
        mock_response = Mock(spec=Response)
        mock_response.json.return_value = {
            "values": [{"id": "1"}, {"id": "2"}],
            "nextPage": None,
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        url = "issue/createmeta"
        result = self.executor.fetch_data(url)
        expected = [{"id": "1"}, {"id": "2"}]

        self.assertEqual(result, expected)

    @patch("gc_jira_api.Requestor.requests.get")
    def test_fetch_data_absolute_url(self, mock_get):
        mock_response = Mock(spec=Response)
        mock_response.json.return_value = {
            "values": [{"id": "1"}, {"id": "2"}],
            "nextPage": None,
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        url = "https://jira.example.com/rest/api/3/issue/createmeta"
        result = self.executor.fetch_data(url, is_absolute_url=True)
        expected = [{"id": "1"}, {"id": "2"}]

        self.assertEqual(result, expected)

    @patch("gc_jira_api.Requestor.requests.get")
    def test_make_request_get(self, mock_get):
        mock_response = Mock(spec=Response)
        mock_response.json.return_value = {"id": "1"}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        url = f"{self.jira_server}/{JIRA_BASE_ENDPOINT}/issue/createmeta"
        result = self.executor._make_request(url, {}, 0, "GET")

        self.assertEqual(result, mock_response)

    @patch("gc_jira_api.Requestor.requests.post")
    def test_make_request_post(self, mock_post):
        mock_response = Mock(spec=Response)
        mock_response.json.return_value = {"id": "1"}
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        url = f"{self.jira_server}/{JIRA_BASE_ENDPOINT}/issue"
        data = {"fields": {"summary": "Test issue"}}
        result = self.executor._make_request(url, data, 0, "POST")

        self.assertEqual(result, mock_response)
        mock_post.assert_called_once_with(
            url,
            headers=HEADERS,
            auth=HTTPBasicAuth(self.jira_username, self.jira_password),
            data=json.dumps(data),
        )

    @patch("gc_jira_api.Requestor.requests.put")
    def test_make_request_put(self, mock_put):
        mock_response = Mock(spec=Response)
        mock_response.json.return_value = {"id": "1"}
        mock_response.status_code = 200
        mock_put.return_value = mock_response

        url = f"{self.jira_server}/{JIRA_BASE_ENDPOINT}/issue/1"
        data = {"fields": {"summary": "Updated issue"}}
        result = self.executor._make_request(url, data, 0, "PUT")

        self.assertEqual(result, mock_response)
        mock_put.assert_called_once_with(
            url,
            headers=HEADERS,
            auth=HTTPBasicAuth(self.jira_username, self.jira_password),
            json=data,
        )

    @patch("gc_jira_api.Requestor.requests.delete")
    def test_make_request_delete(self, mock_delete):
        mock_response = Mock(spec=Response)
        mock_response.status_code = 204
        mock_delete.return_value = mock_response

        url = f"{self.jira_server}/{JIRA_BASE_ENDPOINT}/issue/1"
        result = self.executor._make_request(url, {}, 0, "DELETE")

        self.assertEqual(result, mock_response)
        mock_delete.assert_called_once_with(
            url,
            headers=HEADERS,
            auth=HTTPBasicAuth(self.jira_username, self.jira_password),
        )
