import unittest
from unittest.mock import Mock, patch

from gc_google_services_api.bigquery import execute_query


class TestSuite(unittest.TestCase):
    def _create_bigquery_mock():
        mock = Mock()

        bigquery_client_result_mock = Mock()
        bigquery_client_result_mock.result.return_value = (
            "bigquery_query_result"  # noqa: E501
        )

        bigquery_client_mock = Mock()
        bigquery_client_mock.query.return_value = bigquery_client_result_mock

        mock.Client.return_value = bigquery_client_mock

        return mock

    @patch(
        "gc_google_services_api.bigquery.bigquery", new=_create_bigquery_mock()
    )  # noqa: E501
    def test_execute_query_method_should_returns_bigquery_results_method_when_query_return_successfully(  # noqa: E501
        self,
    ):  # noqa: E501
        expected_result = "bigquery_query_result"
        response = execute_query("BIGQUERY_QUERY")

        self.assertEqual(response, expected_result)
