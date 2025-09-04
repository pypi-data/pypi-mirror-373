import asyncio
import time
import unittest
from unittest.mock import MagicMock, patch

from analytics_ingest.internal.utils.graphql_executor import GraphQLExecutor
from tests.test_settings import GRAPHQL_ENDPOINT


class TestGraphQLExecutorConcurrency(unittest.TestCase):
    def setUp(self):
        self.executor = GraphQLExecutor(GRAPHQL_ENDPOINT, True)

    @patch("analytics_ingest.internal.utils.graphql_executor.requests.post")
    def test_concurrent_requests_execute_serially(self, mock_post):
        def delayed_post(*args, **kwargs):
            time.sleep(0.5)
            mock_response = MagicMock()
            mock_response.text = '{"data": {"ok": true}}'
            mock_response.json.return_value = {"data": {"ok": True}}
            return mock_response

        mock_post.side_effect = delayed_post

        request_count = 5
        execution_times = []

        async def run_query(i):
            start = time.monotonic()
            await self.executor.execute_async("query { dummy }")
            end = time.monotonic()
            execution_times.append((i, start, end))

        async def main():
            tasks = [run_query(i) for i in range(request_count)]
            await asyncio.gather(*tasks)

        asyncio.run(main())

        self.assertEqual(mock_post.call_count, request_count)

        for i in range(1, len(execution_times)):
            prev_end = execution_times[i - 1][2]
            curr_start = execution_times[i][1]
            self.assertGreaterEqual(
                curr_start,
                prev_end,
                f"Request {i} started before previous finished — Semaphore failed",
            )

        total_duration = execution_times[-1][2] - execution_times[0][1]
        self.assertGreaterEqual(total_duration, 0.5 * request_count - 0.1)

    @patch("analytics_ingest.internal.utils.graphql_executor.requests.post")
    def test_10_concurrent_requests_execute_serially(self, mock_post):
        def delayed_post(*args, **kwargs):
            time.sleep(0.01)
            mock_response = MagicMock()
            mock_response.text = '{"data": {"ok": true}}'
            mock_response.json.return_value = {"data": {"ok": True}}
            return mock_response

        mock_post.side_effect = delayed_post

        request_count = 10
        execution_times = []

        async def run_query(i):
            start = time.monotonic()
            await self.executor.execute_async("query { dummy }")
            end = time.monotonic()
            execution_times.append((i, start, end))

        async def main():
            tasks = [run_query(i) for i in range(request_count)]
            await asyncio.gather(*tasks)

        asyncio.run(main())

        self.assertEqual(mock_post.call_count, request_count)

        for i in range(1, len(execution_times)):
            prev_end = execution_times[i - 1][2]
            curr_start = execution_times[i][1]
            self.assertGreaterEqual(
                curr_start,
                prev_end,
                f"Request {i} started before previous finished — Semaphore failed",
            )

        total_duration = execution_times[-1][2] - execution_times[0][1]
        self.assertGreaterEqual(total_duration, 0.01 * request_count - 1)


if __name__ == "__main__":
    unittest.main()
