"""Extension of the GraphQL supporting retries for data processing use cases."""

import logging
from typing import Any
from typing import Callable

import requests
from gqlclient.base import DefaultParameters
from gqlclient.base import GraphQLClientBase
from gqlclient.request_wrap import wrap_request
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from dkist_processing_common.config import common_configurations

logger = logging.getLogger(__name__)


class GraphQLClient(GraphQLClientBase):
    """Helper class for formatting and executing synchronous GraphQL queries and mutations."""

    adapter = HTTPAdapter(
        max_retries=Retry(
            total=10,
            backoff_factor=1,
            status_forcelist=[502, 503, 404],
            allowed_methods=["POST"],  # all graphql methods are POST
        )
    )

    def execute_gql_call(self, query: dict, **kwargs) -> dict:
        """
        Execute a GraphQL query or mutation using requests.

        :param query: Dictionary formatted graphql query

        :param kwargs: Optional arguments that `requests` takes. e.g. headers

        :return: Dictionary containing the response from the GraphQL endpoint
        """
        logger.debug(f"Executing graphql call: host={self.gql_uri}")
        kwargs["headers"] = {
            **kwargs.get("headers", {}),
            "Service-Name": __name__,
            "Authorization": common_configurations.gql_auth_token,
        }
        with requests.sessions.Session() as http:
            http.mount("http://", self.adapter)
            response = http.post(url=self.gql_uri, json=query, **kwargs)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error executing graphql call: status_code={e.response.status_code}, detail={e.response.text}"
            )
            raise e
        return response.json()

    def execute_gql_query(
        self,
        query_base: str,
        query_response_cls: type,
        query_parameters: object | None = DefaultParameters,
        response_encoder: Callable[[str, list[dict] | dict, type], Any] | None = None,
        **kwargs,
    ) -> Any:
        """Execute gql query with parameters dynamically wrapped."""
        if query_parameters is not None and query_parameters is not DefaultParameters:
            query_parameters = wrap_request(query_parameters)
        return super().execute_gql_query(
            query_base=query_base,
            query_response_cls=query_response_cls,
            query_parameters=query_parameters,
            response_encoder=response_encoder,
            **kwargs,
        )

    def execute_gql_mutation(
        self,
        mutation_base: str,
        mutation_parameters: object,
        mutation_response_cls: type | None = None,
        response_encoder: Callable[[str, list[dict] | dict, type], Any] | None = None,
        **kwargs,
    ) -> Any:
        """Execute gql mutation with parameters dynamically wrapped."""
        mutation_parameters = wrap_request(mutation_parameters)
        return super().execute_gql_mutation(
            mutation_base=mutation_base,
            mutation_parameters=mutation_parameters,
            mutation_response_cls=mutation_response_cls,
            response_encoder=response_encoder,
            **kwargs,
        )
