from google.auth.transport.requests import Request
from google.oauth2 import id_token


def fetch_id_token(audience: str):
    """Fetch ID token using service account credentials.

    The environment variable `GOOGLE_APPLICATION_CREDENTIALS` must be set
    to the path of a valid service account JSON file.
    """
    return id_token.fetch_id_token(audience=audience, request=Request())
