import boto3
from mypy_boto3_lambda.type_defs import InvocationResponseTypeDef
import json
from typing import Optional, Any, cast
from urllib3.util.url import parse_url


class LambdaHandler:
    ACCEPTABLE_STATUS_CODES = [200, 201, 204]

    def __init__(self) -> None:
        return

    def invoke(
        self,
        url: str,
        header: dict,
        method: str,
        body: Optional[dict] = None,
        query_params: Optional[dict] = None,
    ) -> Any:
        parsed_url = parse_url(url)
        payload = {
            "headers": header,
            "path": parsed_url.path,
            "httpMethod": method.upper(),
            "body": body,
            "queryStringParameters": query_params,
        }

        client = boto3.client("lambda")
        try:
            raw_response = client.invoke(
                FunctionName=cast(str, parsed_url.netloc),
                InvocationType="RequestResponse",
                Payload=json.dumps(payload),
            )
            return self.parse_response(raw_response)

        except RuntimeError as e:
            raise RuntimeError(f"Error invoking lambda for payload {str(payload)}") from e

    def parse_response(self, response: InvocationResponseTypeDef) -> Any:
        raw_payload = response["Payload"].read() if "Payload" in response else None
        invocation_status_code = response.get("StatusCode", None)
        if invocation_status_code not in self.ACCEPTABLE_STATUS_CODES:
            raise RuntimeError(
                f"Error invoking lambda. Invocation status code: {invocation_status_code}. Response: {str(raw_payload)}"
            )

        payload = json.loads(raw_payload)
        lambda_status_code = payload.get("statusCode", None)
        if lambda_status_code not in self.ACCEPTABLE_STATUS_CODES:
            raise RuntimeError(
                f"Error invoking lambda. Lambda status code: {lambda_status_code}. Response: {str(payload)}"
            )

        return json.loads(payload.get("body", "{}"))


class LambdaClient:
    def __init__(self, host: str, default_header: dict):
        self.host = host
        self.default_header = default_header
        self.handler = LambdaHandler()

    def invoke(
        self,
        path: str,
        method: str,
        body: Optional[dict] = None,
        query_params: Optional[dict] = None,
    ):
        if path.startswith("/"):
            path = path[1:]
        endpoint = f"{self.host}/{path}"
        try:
            return self.handler.invoke(endpoint, self.default_header, method, body, query_params)

        except RuntimeError as e:
            raise RuntimeError(f"Error invoking API. Request error: {str(e)}") from e
