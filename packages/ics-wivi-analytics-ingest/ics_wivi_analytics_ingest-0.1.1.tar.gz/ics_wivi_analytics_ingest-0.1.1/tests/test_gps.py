import unittest
from copy import deepcopy
from datetime import datetime, timezone

from analytics_ingest.ingest_client import IcsAnalytics
from factories import configuration_factory, gps_factory
from tests.test_settings import GRAPHQL_ENDPOINT


class TestAnalyticsGPSIntegration(unittest.TestCase):
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

    def test_add_gps_valid_objects(self):
        gps_objects = gps_factory(num_entries=10)
        self.assertIsInstance(self.client.configuration_id, int)
        for gps_obj in gps_objects:
            self.client.add_gps(gps_obj)

    def test_add_gps_duplicate_entries(self):
        entry = gps_factory(num_entries=1)[0]
        gps_data = [entry for _ in range(5)]
        for gps_obj in gps_data:
            try:
                self.client.add_gps(gps_obj)
            except Exception as e:
                self.fail(f"Valid input raised unexpected error: {e}")

    def test_add_gps_missing_time(self):
        gps_obj = deepcopy(gps_factory(num_entries=1)[0])
        gps_obj["time"] = None
        with self.assertRaises(Exception) as context:
            self.client.add_gps(gps_obj)
        self.assertIn("time", str(context.exception).lower())

    def test_add_gps_invalid_latitude_type(self):
        gps_obj = deepcopy(gps_factory(num_entries=1)[0])
        gps_obj['latitude'] = "not-a-float"
        with self.assertRaises(Exception) as context:
            self.client.add_gps(gps_obj)
        self.assertIn("latitude", str(context.exception).lower())

    def test_add_gps_empty_list(self):
        with self.assertRaises(ValueError) as context:
            self.client.add_gps(object())
        self.assertIn("missing", str(context.exception).lower())

    def test_add_gps_none_input(self):
        with self.assertRaises(ValueError) as context:
            self.client.add_gps(None)
        self.assertIn("missing", str(context.exception).lower())

    def test_add_gps_time_only(self):
        class DummyGPS:
            def __init__(self, time):
                self.time = time

        try:
            self.client.add_gps({"time": datetime.now(timezone.utc).isoformat()})
        except Exception as e:
            self.fail(f"Minimal GPS input raised unexpected error: {e}")
