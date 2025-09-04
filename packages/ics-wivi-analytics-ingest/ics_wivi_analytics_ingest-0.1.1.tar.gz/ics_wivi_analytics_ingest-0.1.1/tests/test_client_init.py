import os
import unittest

from analytics_ingest.ingest_client import IcsAnalytics
from factories.init_schema_factory import init_schema_factory


class TestAnalyticsIngestClientInit(unittest.TestCase):
    def test_init_with_valid_config(self):
        config_data = init_schema_factory()
        client = IcsAnalytics(**config_data)

        self.assertEqual(client.config.device_id, config_data["device_id"])
        self.assertIsNotNone(client.executor)
        self.assertIsInstance(client.configuration_id, int)

    def test_missing_each_required_param(self):
        required_keys = ["device_id", "vehicle_id", "fleet_id", "org_id"]
        for key in required_keys:
            with self.subTest(key=key):
                config_data = init_schema_factory()
                config_data.pop(key)
                with self.assertRaises(ValueError) as ctx:
                    IcsAnalytics(**config_data)
                self.assertIn(key, str(ctx.exception))

    def test_invalid_type_for_int_fields(self):
        int_fields = ["device_id", "vehicle_id", "fleet_id", "org_id"]
        for key in int_fields:
            with self.subTest(key=key):
                config_data = init_schema_factory(**{key: "not-an-int"})
                with self.assertRaises(ValueError) as ctx:
                    IcsAnalytics(**config_data)
                self.assertIn(key, str(ctx.exception))

    def test_missing_graphql_endpoint_raises_when_not_in_env(self):
        config_data = init_schema_factory(graphql_endpoint=None)
        if "GRAPH_ENDPOINT" in os.environ:
            del os.environ["GRAPH_ENDPOINT"]

        with self.assertRaises(ValueError) as ctx:
            IcsAnalytics(**config_data)

        self.assertIn("graphql_endpoint", str(ctx.exception))

    def test_config_schema_object_is_attached(self):
        config_data = init_schema_factory()
        client = IcsAnalytics(**config_data)
        self.assertEqual(client.config.device_id, config_data["device_id"])

    def test_executor_is_set(self):
        config_data = init_schema_factory()
        client = IcsAnalytics(**config_data)
        self.assertIsNotNone(client.executor)

    def test_invalid_batch_size_negative(self):
        config_data = init_schema_factory(batch_size=-5)
        with self.assertRaises(ValueError) as ctx:
            IcsAnalytics(**config_data)
        self.assertIn("batch_size", str(ctx.exception))

    from unittest.mock import patch

    @patch("analytics_ingest.ingest_client.GraphQLExecutor.execute")
    def test_env_fallbacks(self, mock_execute):
        os.environ["SEC_AUTH_TOKEN"] = "env-token"
        os.environ["GRAPH_ENDPOINT"] = "http://env-graphql"

        mock_execute.return_value = {"data": {"createConfiguration": {"id": 123}}}

        config_data = init_schema_factory()
        config_data.pop("graphql_endpoint")

        client = IcsAnalytics(**config_data)

        self.assertEqual(client.config.graphql_endpoint, "http://env-graphql")
