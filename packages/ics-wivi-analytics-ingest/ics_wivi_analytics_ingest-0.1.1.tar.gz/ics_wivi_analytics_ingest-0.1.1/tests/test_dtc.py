import unittest

from analytics_ingest.ingest_client import IcsAnalytics
from factories import configuration_factory, dtc_factory, message_factory
from tests.test_settings import GRAPHQL_ENDPOINT


class TestAnalyticsDTCIntegration(unittest.TestCase):
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

    def build_test_entry(self, dtc_data, message_data):
        return {
            "configurationId": 1,
            "fileId": "File_8",
            "messageId": "Msg_123",
            "messageDate": "2025-06-05T03:07:07Z",
            "data": dtc_data,
            "name": message_data["name"],
            "networkName": message_data["networkName"],
            "name": message_data["name"],
            **{k: v for k, v in message_data.items() if k not in ["name"]},
        }

    def test_add_dtc_valid(self):
        dtc_obj = dtc_factory(num_dtc_entries=1, items_per_dtc=5)[0]
        message_data = message_factory(self.config_data['vehicle_id'])[0]
        entry = self.build_test_entry(dtc_obj["data"], message_data)

        try:
            self.client.add_dtc(entry)
        except Exception as e:
            self.fail(f"Valid input raised unexpected error: {e}")

    def test_add_dtc_missing_description(self):
        dtc_obj = dtc_factory(num_dtc_entries=1, items_per_dtc=3)[0]
        del dtc_obj["data"][0]["description"]
        message_data = message_factory(self.config_data['vehicle_id'])[0]
        entry = self.build_test_entry(dtc_obj["data"], message_data)

        with self.assertRaises(Exception) as context:
            self.client.add_dtc(entry)
        self.assertIn("description", str(context.exception).lower())

    def test_add_dtc_invalid_time_format(self):
        dtc_obj = dtc_factory(num_dtc_entries=1, items_per_dtc=1)[0]
        dtc_obj["data"][0]["time"] = "not-a-time"
        message_data = message_factory(self.config_data['vehicle_id'])[0]
        entry = self.build_test_entry(dtc_obj["data"], message_data)

        with self.assertRaises(Exception) as context:
            self.client.add_dtc(entry)
        self.assertIn("time", str(context.exception).lower())

    def test_add_dtc_empty_data_list(self):
        message_data = message_factory(self.config_data['vehicle_id'])[0]
        entry = self.build_test_entry([], message_data)

        try:
            self.client.add_dtc(entry)
        except Exception as e:
            self.fail(
                f"Empty DTC data list should not raise an exception, but got: {e}"
            )

    def test_add_dtc_missing_data_key(self):
        message_data = message_factory(self.config_data['vehicle_id'])[0]
        entry = self.build_test_entry(None, message_data)
        entry.pop("data", None)

        try:
            self.client.add_dtc(entry)
        except Exception as e:
            self.fail(f"Missing 'data' key should not raise exception, but got: {e}")
