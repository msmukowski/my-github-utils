class GhUtilsError(Exception):
    pass


class ConfigError(GhUtilsError):
    pass


class GitHubAPIError(GhUtilsError):
    def __init__(self, message: str, status_code: int | None = None, response_body: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body
