import json


class PixelBadRequestError(Exception):
    """Exception raised when a bad request is made to the Pixel API."""

    def __init__(
        self,
        response_json: dict,
        status_code: int,
        method: str,
        url: str,
        request_id: str | None = None,
        body: str | None = None,
    ):
        # Pretty print the response json
        self.json_resp_msg = json.dumps(response_json, indent=4)
        self.status_code = status_code
        self.method = method
        self.url = url
        self.body = body
        self.message = f"Bad request {self.status_code} for {self.method} {self.url} (request ID: {request_id})"
        if body:
            self.message += f"\nPayload:\n{self.body}"
        self.message += f"\nResponse: \n{self.json_resp_msg}"
        # Catch validation errors from pydantic
        super().__init__(self.message)


class PixelUploadJobError(Exception):
    """
    Exception raised when an upload job fails.
    """

    def __init__(self, job_id: int, status: str, detail: str):
        self.job_id = job_id
        self.detail = detail
        self.status = status
        message = (
            f"Upload job {job_id} failed with status '{status}', detail: \n{detail}"
        )
        super().__init__(message)


class PixelMultipleUploadJobError(Exception):
    """
    Exception raised when multiple upload jobs fail.
    """

    def __init__(self, errors: list[PixelUploadJobError]):
        self.errors = errors
        error_messages = "\n".join(str(e) for e in errors)
        message = f"Multiple upload jobs failed:\n{error_messages}"
        super().__init__(message)
