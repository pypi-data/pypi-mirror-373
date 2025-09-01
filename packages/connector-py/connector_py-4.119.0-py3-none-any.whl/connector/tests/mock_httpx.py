import typing as t

from graphql import DocumentNode, print_ast
from pytest_httpx import HTTPXMock

from connector.tests.type_definitions import ResponseBodyMap


def mock_graphql_request_body(
    query: DocumentNode, variables: dict[str, t.Any] | None = None
) -> dict[str, t.Any]:
    body: dict[str, t.Any] = {"query": print_ast(query)}

    if variables:
        body.update({"variables": variables})

    return body


def mock_requests(
    response_body_map: ResponseBodyMap, httpx_mock: HTTPXMock, *, host: str | None = None
):
    if not response_body_map:
        # Don't mock any requests, and use the default behavior of
        # httpx_mock which is HTTP 200, empty body
        return

    for method, responses in response_body_map.items():
        if isinstance(responses, dict):
            for request_line, response in responses.items():
                if request_line.startswith("https://"):
                    url = request_line
                else:
                    url = f"{host or ''}{request_line}"

                httpx_mock.add_response(
                    method=method,
                    url=url,
                    json=response.response_body,
                    text=(
                        response.response_body if isinstance(response.response_body, str) else None
                    ),
                    status_code=response.status_code,
                    headers=response.headers if response.headers else None,
                    match_json=response.request_json_body,
                    match_content=response.request_bytes_body,
                )
        elif isinstance(responses, list):
            for response in responses:
                httpx_mock.add_response(
                    method=method,
                    url=(
                        f"{host or ''}{response.request_path}"
                        if response.request_path
                        else host or ""
                    ),
                    json=response.response_body,
                    text=(
                        response.response_body if isinstance(response.response_body, str) else None
                    ),
                    status_code=response.status_code,
                    headers=response.headers if response.headers else None,
                    match_json=response.request_json_body,
                    match_content=response.request_bytes_body,
                )
