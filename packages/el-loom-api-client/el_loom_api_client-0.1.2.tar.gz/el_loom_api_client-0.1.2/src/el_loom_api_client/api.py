import logging
from typing import Optional

from httpx import HTTPStatusError, Response

logger = logging.getLogger(__package__)


class ApiError(HTTPStatusError):
    """Exception raised for API errors."""

    def __init__(
        self,
        http_status_error: HTTPStatusError,
    ):
        response = http_status_error.response

        # Build the error message
        http_error_message = _format_http_status_error_message(response)
        # Try parse the message from the response
        message_detail = _try_parse_api_error_message(response)

        if message_detail:
            message = f"{message_detail}\n\n{http_error_message}"
        else:
            message = http_error_message

        super().__init__(
            message,
            request=http_status_error.request,
            response=response,
        )

        self._http_status_error = http_status_error

    @property
    def http_status_error(self) -> HTTPStatusError:
        return self._http_status_error


# Format the message the same way as in the original code, excluding the more information link
def _format_http_status_error_message(response: Response) -> str:
    status_class = response.status_code // 100
    error_types = {
        1: "Informational response",
        3: "Redirect response",
        4: "Client error",
        5: "Server error",
    }
    error_type = error_types.get(status_class, "Invalid status code")

    return f"{error_type} '{response.status_code} {response.reason_phrase}' for url '{response.url}'"


def _try_parse_api_error_message(response: Response) -> Optional[str]:
    """Attempts to extract the detailed error message from the API response."""

    content_type = response.headers.get("content-type", "").lower()

    # Check if the response type is JSON
    if content_type.startswith("application/json"):
        # Attempt to extract the error detail
        try:
            data = response.json()
            # Check if dict and contains 'message' or 'detail'
            if isinstance(data, dict):
                # Check message
                if "message" in data and isinstance(data["message"], str):
                    return data["message"]

                # Check detail
                if "detail" in data:
                    # Return as string
                    return str(data["detail"])

            logger.debug("Unexpected error format in API response: %s", data)
        except Exception:
            pass

    return None
