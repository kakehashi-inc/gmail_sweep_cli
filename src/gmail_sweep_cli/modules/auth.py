"""OAuth2 authentication for Gmail API."""

from __future__ import annotations

import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]


def get_token_path(token_dir: str, email: str) -> Path:
    """Return the token file path for the given email."""
    return Path(token_dir) / f"{email}.json"


def run_auth_flow(email: str, credentials_path: str, token_dir: str) -> None:
    """Run the OAuth2 authentication flow and save the token."""
    cred_path = Path(credentials_path)
    if not cred_path.exists():
        print(f"Error: Credentials file not found: {credentials_path}")
        print("Please download client_secret.json from Google Cloud Console.")
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(str(cred_path), SCOPES)
    creds = flow.run_local_server(port=0)

    token_path = get_token_path(token_dir, email)
    token_path.parent.mkdir(parents=True, exist_ok=True)
    with open(token_path, "w", encoding="utf-8") as f:
        f.write(creds.to_json())

    print(f"Authentication successful. Token saved to {token_path}")


def load_credentials(email: str, token_dir: str) -> Credentials:
    """Load and refresh credentials from the token file."""
    token_path = get_token_path(token_dir, email)

    if not token_path.exists():
        print(f"Error: Token file not found: {token_path}")
        print(f"Please run: gmail-sweep-cli --auth {email}")
        sys.exit(1)

    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    if not creds.valid:
        print("Error: Token is invalid. Please re-authenticate.")
        print(f"Run: gmail-sweep-cli --auth {email}")
        sys.exit(1)

    return creds
