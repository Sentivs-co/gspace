import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from gspace.utils.logger import get_logger


class BatchRequestType(Enum):
    """Types of batch requests."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


@dataclass
class BatchRequest:
    """Represents a single request within a batch."""

    request_id: str
    method: BatchRequestType
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    body: dict[str, Any] | None = None
    timeout: int | None = None


@dataclass
class BatchResponse:
    """Represents a response from a batch request."""

    request_id: str
    status_code: int
    headers: dict[str, str]
    body: dict[str, Any] | None = None
    error: str | None = None


class BatchRequestManager:
    """
    Manages batch requests to Google APIs.
    Reduces API quota usage and improves performance for bulk operations.
    """

    def __init__(self, max_batch_size: int = 100):
        """
        Initialize the batch request manager.

        Args:
            max_batch_size: Maximum number of requests per batch
        """
        self.logger = get_logger("gspace.batch")
        self.max_batch_size = max_batch_size
        self.requests: list[BatchRequest] = []

        self.logger.info(
            f"BatchRequestManager initialized with max batch size: {max_batch_size}"
        )

    def add_request(self, request: BatchRequest) -> None:
        """
        Add a request to the batch.

        Args:
            request: BatchRequest object to add
        """
        if len(self.requests) >= self.max_batch_size:
            self.logger.warning(
                f"Batch is full ({self.max_batch_size} requests). Cannot add more requests."
            )
            return

        self.requests.append(request)
        self.logger.debug(f"Added request {request.request_id} to batch")

    def add_get_request(
        self, request_id: str, url: str, headers: dict[str, str] | None = None
    ) -> None:
        """
        Add a GET request to the batch.

        Args:
            request_id: Unique identifier for the request
            url: API endpoint URL
            headers: Optional headers for the request
        """
        request = BatchRequest(
            request_id=request_id,
            method=BatchRequestType.GET,
            url=url,
            headers=headers or {},
        )
        self.add_request(request)

    def add_post_request(
        self,
        request_id: str,
        url: str,
        body: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> None:
        """
        Add a POST request to the batch.

        Args:
            request_id: Unique identifier for the request
            url: API endpoint URL
            body: Request body data
            headers: Optional headers for the request
        """
        request = BatchRequest(
            request_id=request_id,
            method=BatchRequestType.POST,
            url=url,
            body=body,
            headers=headers or {},
        )
        self.add_request(request)

    def add_put_request(
        self,
        request_id: str,
        url: str,
        body: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> None:
        """
        Add a PUT request to the batch.

        Args:
            request_id: Unique identifier for the request
            url: API endpoint URL
            body: Request body data
            headers: Optional headers for the request
        """
        request = BatchRequest(
            request_id=request_id,
            method=BatchRequestType.PUT,
            url=url,
            body=body,
            headers=headers or {},
        )
        self.add_request(request)

    def add_delete_request(
        self, request_id: str, url: str, headers: dict[str, str] | None = None
    ) -> None:
        """
        Add a DELETE request to the batch.

        Args:
            request_id: Unique identifier for the request
            url: API endpoint URL
            headers: Optional headers for the request
        """
        request = BatchRequest(
            request_id=request_id,
            method=BatchRequestType.DELETE,
            url=url,
            headers=headers or {},
        )
        self.add_request(request)

    def add_patch_request(
        self,
        request_id: str,
        url: str,
        body: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> None:
        """
        Add a PATCH request to the batch.

        Args:
            request_id: Unique identifier for the request
            url: API endpoint URL
            body: Request body data
            headers: Optional headers for the request
        """
        request = BatchRequest(
            request_id=request_id,
            method=BatchRequestType.PATCH,
            url=url,
            body=body,
            headers=headers or {},
        )
        self.add_request(request)

    def create_batch_payload(self) -> str:
        """
        Create the multipart/mixed batch payload for Google APIs.

        Returns:
            Formatted batch payload string
        """
        if not self.requests:
            raise ValueError("No requests in batch")

        boundary = "batch_boundary"
        payload_parts = []

        for request in self.requests:
            # Request headers
            headers = "\r\n".join([f"{k}: {v}" for k, v in request.headers.items()])
            if headers:
                headers += "\r\n"

            # Request body
            body = ""
            if request.body:
                body = json.dumps(request.body)

            # Build request part
            part = f"""--{boundary}
Content-Type: application/http

{request.method.value} {request.url} HTTP/1.1
{headers}Content-Length: {len(body)}

{body}"""
            payload_parts.append(part)

        # Close boundary
        payload_parts.append(f"--{boundary}--")

        return "\r\n".join(payload_parts)

    def parse_batch_response(self, response_body: str) -> list[BatchResponse]:
        """
        Parse the batch response from Google APIs.

        Args:
            response_body: Raw response body from batch request

        Returns:
            List of BatchResponse objects
        """
        responses = []
        boundary = None

        # Extract boundary from response
        lines = response_body.split("\r\n")
        for line in lines:
            if line.startswith("--") and "boundary" in line:
                boundary = line
                break

        if not boundary:
            self.logger.error("Could not find boundary in batch response")
            return responses

        # Split response by boundary
        parts = response_body.split(boundary)

        for part in parts:
            if not part.strip() or part.strip() == "--":
                continue

            try:
                # Extract HTTP response
                http_start = part.find("HTTP/1.1")
                if http_start == -1:
                    continue

                # Parse status line
                status_line = part[http_start:].split("\r\n")[0]
                status_code = int(status_line.split()[1])

                # Extract headers and body
                header_body = part[http_start:].split("\r\n\r\n", 1)
                if len(header_body) < 2:
                    continue

                headers_text, body_text = header_body

                # Parse headers
                headers = {}
                for line in headers_text.split("\r\n")[1:]:  # Skip status line
                    if ":" in line:
                        key, value = line.split(":", 1)
                        headers[key.strip()] = value.strip()

                # Parse body
                body = None
                error = None
                if body_text.strip():
                    try:
                        body = json.loads(body_text)
                    except json.JSONDecodeError:
                        body = body_text

                # Check for errors
                if status_code >= 400:
                    error = (
                        body.get("error", {}).get("message", "Unknown error")
                        if isinstance(body, dict)
                        else str(body)
                    )

                # Extract request ID from headers or generate one
                request_id = headers.get("X-Request-ID", f"req_{len(responses)}")

                response = BatchResponse(
                    request_id=request_id,
                    status_code=status_code,
                    headers=headers,
                    body=body,
                    error=error,
                )
                responses.append(response)

            except Exception as e:
                self.logger.error(f"Error parsing batch response part: {e}")
                continue

        return responses

    def execute_batch(self, service, batch_url: str = "/batch") -> list[BatchResponse]:
        """
        Execute the batch request using the provided service.

        Args:
            service: Google API service instance
            batch_url: Batch endpoint URL

        Returns:
            List of BatchResponse objects
        """
        if not self.requests:
            self.logger.warning("No requests to execute")
            return []

        try:
            self.logger.info(
                f"Executing batch request with {len(self.requests)} requests"
            )

            # Create batch payload
            self.create_batch_payload()

            # Execute batch request
            batch_request = service.new_batch_http_request()

            for request in self.requests:
                if request.method == BatchRequestType.GET:
                    batch_request.add(
                        service.get(url=request.url),
                        callback=None,
                        request_id=request.request_id,
                    )
                elif request.method == BatchRequestType.POST:
                    batch_request.add(
                        service.post(url=request.url, body=request.body),
                        callback=None,
                        request_id=request.request_id,
                    )
                elif request.method == BatchRequestType.PUT:
                    batch_request.add(
                        service.put(url=request.url, body=request.body),
                        callback=None,
                        request_id=request.request_id,
                    )
                elif request.method == BatchRequestType.DELETE:
                    batch_request.add(
                        service.delete(url=request.url),
                        callback=None,
                        request_id=request.request_id,
                    )
                elif request.method == BatchRequestType.PATCH:
                    batch_request.add(
                        service.patch(url=request.url, body=request.body),
                        callback=None,
                        request_id=request.request_id,
                    )

            # Execute batch
            batch_response = batch_request.execute()

            # Parse responses
            responses = []
            for request_id, response in batch_response.items():
                if isinstance(response, Exception):
                    batch_response = BatchResponse(
                        request_id=request_id,
                        status_code=500,
                        headers={},
                        error=str(response),
                    )
                else:
                    batch_response = BatchResponse(
                        request_id=request_id,
                        status_code=response.status,
                        headers=dict(response.headers),
                        body=response.data if hasattr(response, "data") else None,
                    )
                responses.append(batch_response)

            self.logger.info(f"Batch request completed with {len(responses)} responses")
            return responses

        except Exception as e:
            self.logger.error(f"Error executing batch request: {e}")
            raise

    def clear_requests(self) -> None:
        """Clear all requests from the batch."""
        self.requests.clear()
        self.logger.info("Cleared all batch requests")

    def get_request_count(self) -> int:
        """
        Get the current number of requests in the batch.

        Returns:
            Number of requests
        """
        return len(self.requests)

    def is_full(self) -> bool:
        """
        Check if the batch is full.

        Returns:
            True if batch is full, False otherwise
        """
        return len(self.requests) >= self.max_batch_size

    def get_remaining_capacity(self) -> int:
        """
        Get the remaining capacity in the batch.

        Returns:
            Number of requests that can still be added
        """
        return max(0, self.max_batch_size - len(self.requests))
