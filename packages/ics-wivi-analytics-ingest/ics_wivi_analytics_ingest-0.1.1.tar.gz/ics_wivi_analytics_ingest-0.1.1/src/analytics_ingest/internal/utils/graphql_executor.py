import asyncio
from concurrent.futures import ThreadPoolExecutor

import requests
from graphql import parse, print_ast
from graphql.error import GraphQLSyntaxError
from requests.exceptions import RequestException


class GraphQLExecutor:
    def __init__(self, graphql_endpoint, debug=False, jwt_token=None):
        self.graphql_endpoint = graphql_endpoint
        self.debug = debug
        self.jwt_token = jwt_token
        self._semaphore = asyncio.Semaphore(1)
        self._pending_requests = []
        self._executor_pool = ThreadPoolExecutor(max_workers=10)

    async def execute_async(self, query: str, variables: dict = None):
        async with self._semaphore:
            return self._execute(query, variables)

    def _execute(self, query: str, variables: dict = None):
        """Normal execution — still one by one."""
        self._pending_requests.append((query, variables))
        try:
            res = self._send_request(query, variables)
            self._pending_requests.remove((query, variables))
            return res
        except Exception:
            raise

    def _send_request(self, query: str, variables: dict = None):
        try:
            parsed_query = print_ast(parse(query))
            headers = {"Content-Type": "application/json"}

            if self.jwt_token:
                headers["Authorization"] = f"Bearer {self.jwt_token}"

            request_data = {"query": parsed_query, "variables": variables}

            if self.debug:
                print("request data", request_data)
                print("request headers", headers)

            response = requests.post(
                self.graphql_endpoint, json=request_data, headers=headers, verify=False
            )

            if not response.text:
                raise RuntimeError("Empty response received from GraphQL endpoint.")

            response_data = response.json()
            if "errors" in response_data:
                raise RuntimeError(
                    f"GraphQL request failed with errors: {response_data['errors']}"
                )

            res = {"data": response_data["data"]}
            if self.debug:
                print("response ===> ", res)
            return res

        except (RequestException, GraphQLSyntaxError) as e:
            raise RuntimeError(f"GraphQL request failed: {e}")

    def execute(self, query: str, variables: dict = None):
        return self._execute(query, variables)

    def flush_all(self):
        """Send all remaining requests in parallel, without one-by-one waiting."""
        if not self._pending_requests:
            if self.debug:
                print("[flush_all] No pending requests.")
            return

        if self.debug:
            print(
                f"[flush_all] Sending {len(self._pending_requests)} pending requests..."
            )

        futures = []
        for query, variables in list(self._pending_requests):
            futures.append(
                self._executor_pool.submit(self._send_request, query, variables)
            )

        for f in futures:
            try:
                f.result()
            except Exception as e:
                print(f"[flush_all] Request failed: {e}")

        self._pending_requests.clear()
