import requests
from typing import Dict, Callable

from sgqlc.operation import Operation
from sgqlc.endpoint.requests import RequestsEndpoint
from requests.exceptions import HTTPError
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from stigg.generated.operations import Operations

PRODUCTION_API_URL = "https://api.stigg.io/graphql"
PRODUCTION_EDGE_API_URL = "https://edge.api.stigg.io"

STIGG_REQUESTS_RETRY_COUNT = 3

RETRY_KWARGS = {
    "retry": retry_if_exception_type(HTTPError),
    "stop": stop_after_attempt(STIGG_REQUESTS_RETRY_COUNT),
    "reraise": True,
}


class StiggClient:
    def __init__(self, endpoint: RequestsEndpoint, enable_edge: bool, edge_api_url: str):
        self._endpoint: RequestsEndpoint = endpoint

        self._enable_edge = enable_edge
        self._edge_url = edge_api_url

        self._EDGE_QUERIES: Dict[Operation, Callable[[Dict], Dict]] = {
            Operations.query.get_entitlements: self.get_entitlements,
            Operations.query.get_paywall: self.get_paywall,
        }

    @retry(**RETRY_KWARGS)
    def _get_entitlements(self, variables: Dict[str, Dict]) -> Dict:
        params = variables.get("query")
        if params is None:
            raise ValueError('Variables do not include required key "query".')

        customer_id = params.pop("customerId")

        url = f"{self._edge_url}/v1/c/{customer_id}/entitlements.json"

        data = requests.get(url, headers=self._endpoint.base_headers, params=params, timeout=self._endpoint.timeout)
        data.raise_for_status()

        return data.json()

    def get_entitlements(self, variables: Dict[str, Dict]) -> Dict:
        if self._enable_edge is False:
            return self.request(Operations.query.get_entitlements, variables, raw_response=True)

        return self._get_entitlements(variables)

    @retry(**RETRY_KWARGS)
    def _get_paywall(self,variables: Dict[str, Dict]) -> Dict:
        params = variables.get("input")
        if params is None:
            raise ValueError('Variables do not include required key "input".')

        if params.get("productId") is not None:
            url = f"{self._edge_url}/v1/p/{params['productId']}/paywall.json"
            params.pop("productId")
        else:
            url = f"{self._edge_url}/v1/paywall.json"

        data = requests.get(url, headers=self._endpoint.base_headers, params=params, timeout=self._endpoint.timeout)
        data.raise_for_status()

        return data.json()

    def get_paywall(self, variables: Dict[str, Dict]) -> Dict:
        if self._enable_edge is False:
            return self.request(Operations.query.get_paywall, variables, raw_response=True)

        return self._get_paywall(variables)

    @retry(**RETRY_KWARGS)
    def request(self, operation: Operation, variables: Dict, raw_response: bool = False):
        data = self._endpoint(operation, variables)
        if raw_response:
            return data

        # clean up data to so an exception will be raised
        errors = data.get('errors')
        if errors and data.get('data') is not None:
            data.pop('data')

        # interpret results into native Python objects
        return operation + data


class Stigg(Operations):
    @staticmethod
    def create_client(
        api_key: str,
        api_url: str = PRODUCTION_API_URL,
        enable_edge: bool = True,
        edge_api_url: str = PRODUCTION_EDGE_API_URL,
        request_timeout: int = 30,
    ) -> StiggClient:
        headers = {'X-API-KEY': f'{api_key}', 'X-API-VERSION': '1'}
        endpoint = RequestsEndpoint(url=api_url, base_headers=headers, timeout=request_timeout)
        return StiggClient(endpoint, enable_edge, edge_api_url)
