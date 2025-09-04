import time
import unittest
from unittest.mock import MagicMock, patch

from analytics_ingest.internal.utils.signal_buffer_manager import SignalBufferManager
from factories import configuration_factory, message_factory, signal_factory


class TestSignalBufferManager(unittest.TestCase):
    def setUp(self):
        self.mock_executor = MagicMock()
        self.config_id = 123
        self.batch_size = 2
        self.max_signals = 3
        self.vehicle_id = "test_vehicle"
        self.manager = SignalBufferManager(
            executor=self.mock_executor,
            configuration_id=self.config_id,
            batch_size=self.batch_size,
            max_signal_count=self.max_signals,
            batch_interval_seconds=1,
        )

    @patch("analytics_ingest.internal.utils.signal_buffer_manager.create_message")
    def test_add_signal_triggers_flush_on_max_count(self, _):
        signals = [
            signal_factory(vehicle_id=self.vehicle_id) for _ in range(self.max_signals)
        ]
        self.manager.flush = MagicMock()
        for signal in signals:
            self.manager.add_signal(signal)
        self.manager.flush.assert_called()

    @patch("analytics_ingest.internal.utils.signal_buffer_manager.create_message")
    def test_add_signal_does_not_flush_below_threshold(self, _):
        signal = signal_factory(vehicle_id=self.vehicle_id)
        signal["data"] = signal["data"][:1]
        self.manager.flush = MagicMock()
        self.manager.add_signal(signal)
        self.manager.flush.assert_not_called()

    @patch(
        "analytics_ingest.internal.utils.signal_buffer_manager.get_cached_message_id",
        return_value=456,
    )
    @patch(
        "analytics_ingest.internal.utils.signal_buffer_manager.generate_message_cache_key",
        return_value="cache_key",
    )
    @patch("analytics_ingest.internal.utils.signal_buffer_manager.SignalSchema")
    @patch(
        "analytics_ingest.internal.utils.signal_buffer_manager.Batcher.create_batches"
    )
    @patch(
        "analytics_ingest.internal.utils.signal_buffer_manager.GraphQLMutations.upsert_signal_data",
        return_value="mutation_string",
    )
    def test_flush_calls_executor_with_valid_signals(
        self, mock_mutation, mock_batcher, mock_signal_schema, _, __
    ):
        signals = [signal_factory(vehicle_id=self.vehicle_id)]
        self.manager.buffer = signals
        mock_batcher.return_value = [signals]
        mock_signal_schema.from_variables.return_value.dict.return_value = {
            "mock": "data"
        }

        self.manager.flush()
        self.mock_executor.execute.assert_called_with(
            "mutation_string", {"input": {"signals": [{"mock": "data"}]}}
        )


if __name__ == "__main__":
    unittest.main()
