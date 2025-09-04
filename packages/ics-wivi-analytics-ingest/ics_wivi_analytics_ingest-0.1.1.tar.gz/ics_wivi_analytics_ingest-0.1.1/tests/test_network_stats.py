import unittest

from analytics_ingest.ingest_client import IcsAnalytics
from analytics_ingest.internal.schemas.configuration_schema import ConfigurationSchema
from analytics_ingest.internal.utils.graphql_executor import GraphQLExecutor
from factories import configuration_factory, network_stats_factory
from tests.test_settings import GRAPHQL_ENDPOINT


class TestAnalyticsNetworkStatsIntegration(unittest.TestCase):
    def setUp(self):
        self.config_data = configuration_factory()
        self.client = IcsAnalytics(
            device_id=self.config_data['device_id'],
            vehicle_id=self.config_data['vehicle_id'],
            fleet_id=self.config_data['fleet_id'],
            org_id=self.config_data['organization_id'],
            batch_size=10,
            graphql_endpoint=GRAPHQL_ENDPOINT,
        )

    def test_add_network_stats_valid(self):
        data = network_stats_factory(self.config_data['vehicle_id'])
        try:
            self.client.add_network_stats(data)
        except Exception:
            self.fail("add_network_stats() raised Exception unexpectedly!")

    def test_add_network_stats_invalid_type(self):
        data = network_stats_factory(self.config_data['vehicle_id'])
        data["rate"] = "not_a_float"
        with self.assertRaises(RuntimeError) as cm:
            self.client.add_network_stats(data)
        self.assertIn("Failed to add network stats", str(cm.exception))

    def test_add_network_stats_missing_variables(self):
        with self.assertRaises(ValueError) as cm:
            self.client.add_network_stats(None)
        self.assertEqual(str(cm.exception), "Missing 'variables' dictionary")


if __name__ == "__main__":
    unittest.main()
