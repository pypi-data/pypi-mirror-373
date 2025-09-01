from typing import Optional, List
from urllib.parse import urlparse, urlunparse, ParseResult


def join_url(base_uri: str, *parts: str) -> str:
    base_uri = base_uri.rstrip("/")

    cleaned_parts: List[str] = [
        part.strip("/") for part in parts if part is not None and part.strip("/")
    ]
    uri_parts: List[str] = [base_uri, *cleaned_parts]

    return "/".join(uri_parts)


def modify_url(original_url: str, path_url: str) -> str:
    """
    Removes the previous path segment from a URL and appends a new path.

    :param original_url: The input URL string (e.g., "https://demo.jfrog.io/artifactory").

    :return:
        The modified URL string with the base URL (e.g. https://demo.jfrog.io) and the new path appended.
    """
    # 1. Parse the original URL into its components
    # urlparse returns a ParseResult named tuple: (scheme, netloc, path, params, query, fragment)
    parsed_url: ParseResult = urlparse(original_url)

    # 2. Extract the base URL (scheme and netloc), discard the existing params, query, and fragment.
    # Replace the path with provided path_url
    new_full_url: ParseResult = parsed_url._replace(
        path=path_url, params="", query="", fragment=""
    )

    return urlunparse(new_full_url)


def assemble_artifact_url(uri: Optional[str]) -> str:
    if uri is None:
        raise Exception("Artifactory URI is required")

    parsed_url = urlparse(uri)
    if parsed_url.scheme not in ["http", "https"]:
        raise Exception(
            f"Not a valid Artifactory URI: {uri}. "
            f"Artifactory URI example: `https://frogger.jfrog.io/artifactory/ml-local`"
        )

    return f"{parsed_url.scheme}://{parsed_url.netloc}/artifactory"
