import time
from datetime import datetime, timezone
from threading import Thread
from typing import List

from analytics_ingest.internal.schemas.signal_schema import SignalSchema
from analytics_ingest.internal.utils.batching import Batcher
from analytics_ingest.internal.utils.graphql_executor import GraphQLExecutor
from analytics_ingest.internal.utils.message import (
    create_message,
    generate_message_cache_key,
    get_cached_message_id,
)
from analytics_ingest.internal.utils.mutations import GraphQLMutations


class SignalBufferManager:
    def __init__(
        self,
        executor: GraphQLExecutor,
        configuration_id: int,
        batch_size: int,
        max_signal_count: int,
        batch_interval_seconds: int = 1,
    ):
        self.executor = executor
        self.configuration_id = configuration_id
        self.batch_size = batch_size
        self.max_signal_count = max_signal_count
        self.batch_interval_seconds = batch_interval_seconds

        self.buffer: List[dict] = []
        self.last_flush_time = time.time()

        self._start_background_flush()

    def _start_background_flush(self):
        thread = Thread(target=self._background_flush_loop, daemon=True)
        thread.start()

    def _background_flush_loop(self):
        while True:
            time.sleep(max(self.batch_interval_seconds, 0.05))
            if self.buffer and (
                time.time() - self.last_flush_time >= self.batch_interval_seconds
            ):
                try:
                    self.flush(force=True)
                except Exception as e:
                    raise ValueError(f"[SignalBufferManager] Flush error: {e}")

    def add_signal(self, signal: dict):
        try:
            create_message(self.executor, [signal])
        except Exception as e:
            raise ValueError(f"[add_signal] Failed to create message: {e}")

        self.buffer.append(signal)
        total_data_points = sum(len(sig.get("data", [])) for sig in self.buffer)

        if len(self.buffer) >= self.max_signal_count:
            self.flush(force=True)
        elif total_data_points >= self.batch_size:
            self.flush(force=True)

    def flush(self, force=False):
        if not self.buffer:
            if force:
                print("[flush] Forced flush but nothing to send.")
            return
        signals_to_flush = self.buffer
        self.buffer = []
        self.last_flush_time = time.time()

        batches = Batcher.create_batches(signals_to_flush, self.batch_size)

        for idx, batch in enumerate(batches):
            valid_signals = []
            for signal in batch:
                message_key = generate_message_cache_key(signal)
                message_id = get_cached_message_id(message_key)

                if message_id is None:
                    raise ValueError(
                        f"[flush] WARNING: Missing message_id for key {message_key}"
                    )

                for d in signal.get("data", []):
                    if isinstance(d.get("time"), (float, int)):
                        d["time"] = self._convert_float_time(d["time"])

                try:
                    signal_input = SignalSchema.from_variables(
                        self.configuration_id,
                        int(message_id),
                        signal.get("data", []),
                        signal,
                    )
                    valid_signals.append(signal_input.dict())
                except Exception as e:
                    raise ValueError(f"[flush] SignalSchema validation failed: {e}")

            if valid_signals:
                self.executor.execute(
                    GraphQLMutations.upsert_signal_data(),
                    {"input": {"signals": valid_signals}},
                )

    def _convert_float_time(self, ts: float) -> str:
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()

    def _chunk_signals(self, signals: List[dict]) -> List[List[dict]]:
        return [
            signals[i : i + self.max_signal_count]
            for i in range(0, len(signals), self.max_signal_count)
        ]
