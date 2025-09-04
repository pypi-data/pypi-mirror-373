import asyncio
import time
from collections import deque
from threading import Thread
from typing import Optional

from more_itertools import chunked

from analytics_ingest.internal.schemas.ingest_config_schema import IngestConfigSchema
from analytics_ingest.internal.schemas.message_schema import MessageSchema
from analytics_ingest.internal.schemas.signal_schema import SignalSchema
from analytics_ingest.internal.utils.batching import Batcher
from analytics_ingest.internal.utils.configuration import ConfigurationService
from analytics_ingest.internal.utils.dtc import create_dtc
from analytics_ingest.internal.utils.gps import create_gps
from analytics_ingest.internal.utils.graphql_executor import GraphQLExecutor
from analytics_ingest.internal.utils.message import (
    create_message,
    get_cached_message_id,
)
from analytics_ingest.internal.utils.mutations import GraphQLMutations
from analytics_ingest.internal.utils.network import create_network
from analytics_ingest.internal.utils.signal_buffer_manager import SignalBufferManager


class IcsAnalytics:
    def __init__(self, **kwargs):
        self.config = IngestConfigSchema(**kwargs)
        self.executor = GraphQLExecutor(
            self.config.graphql_endpoint, self.config.debug, self.config.jwt_token
        )

        self.configuration_id = ConfigurationService(self.executor).create(
            self.config.model_dump()
        )["data"]["createConfiguration"]["id"]

        self.signal_buffer_manager = SignalBufferManager(
            executor=self.executor,
            configuration_id=self.configuration_id,
            batch_size=self.config.batch_size,
            max_signal_count=self.config.max_signal_count,
            batch_interval_seconds=self.config.batch_interval_seconds,
        )

    def add_signal(self, signal: Optional[dict] = None):
        if not signal or not isinstance(signal, dict):
            raise ValueError("'signal' should be a dict")
        try:
            self.signal_buffer_manager.add_signal(signal)
        except Exception as e:
            raise RuntimeError(f"Failed to add signal: {e}")

    def add_dtc(self, dtc: Optional[dict] = None):
        if not dtc:
            raise ValueError("Missing 'dtc' dict")
        try:
            create_message(self.executor, [dtc])
            create_dtc(executor=self.executor, config_id=self.configuration_id, dtc=dtc)
        except Exception as e:
            raise RuntimeError(f"Failed to add DTC: {e}")

    def add_gps(self, gps: Optional[dict] = None):
        if not gps or not isinstance(gps, dict):
            raise ValueError("Missing or invalid 'gps' dictionary")

        try:
            create_gps(
                executor=self.executor,
                config_id=self.configuration_id,
                gps=gps,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to add GPS: {e}")

    def add_network_stats(self, variables: Optional[dict] = None):
        if not variables:
            raise ValueError("Missing 'variables' dictionary")
        try:
            create_network(
                executor=self.executor,
                config=self.config,
                variables=variables,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to add network stats: {e}")

    def flush(self):
        self.signal_buffer_manager.flush(force=True)
        self.executor.flush_all()

    def close(self):
        time.sleep(self.config.batch_interval_seconds + 0.1)
        try:
            self.signal_buffer_manager.flush(force=True)
            self.executor.flush_all()

        except ValueError as e:
            if "No signals to flush" in str(e) and self.config.debug:
                print("[close] No signals to flush — skipping final flush.")
            else:
                raise ValueError(f"Final flush failed: {e}")
