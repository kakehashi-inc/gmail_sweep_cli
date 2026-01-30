"""Shared Gmail API utility functions."""

from __future__ import annotations

import time
from typing import List, Optional

from googleapiclient.errors import HttpError

MAX_RETRIES = 3
BACKOFF_BASE = 2


def execute_with_retry(request, retries: int = MAX_RETRIES):
    """Execute a Gmail API request with exponential backoff."""
    for attempt in range(retries):
        try:
            return request.execute()
        except HttpError as e:
            if e.resp.status in (429, 500, 503):
                wait = BACKOFF_BASE ** (attempt + 1)
                reason = "Rate limited" if e.resp.status == 429 else "Server error"
                print(f"  {reason}. Waiting {wait}s...")
                time.sleep(wait)
            else:
                raise
        except Exception:
            if attempt < retries - 1:
                wait = BACKOFF_BASE ** (attempt + 1)
                print(f"  Network error. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise
    return None


def list_all_message_ids(service, query: str) -> List[str]:
    """Fetch all message IDs matching a Gmail query.

    Args:
        service: Gmail API service instance.
        query: Gmail search query string.

    Returns:
        List of message ID strings.
    """
    page_token: Optional[str] = None
    message_ids: List[str] = []

    while True:
        request = (
            service.users()
            .messages()
            .list(
                userId="me",
                q=query,
                maxResults=500,
                pageToken=page_token,
            )
        )
        result = execute_with_retry(request)
        if result is None:
            break
        messages = result.get("messages", [])
        if not messages:
            break
        message_ids.extend(m["id"] for m in messages)
        page_token = result.get("nextPageToken")
        if not page_token:
            break

    return message_ids


def get_message_metadata(service, msg_id: str, metadata_headers: Optional[List[str]] = None):
    """Fetch a single message's metadata.

    Args:
        service: Gmail API service instance.
        msg_id: Message ID.
        metadata_headers: List of header names to fetch (e.g. ["From", "Subject", "Date"]).

    Returns:
        Message resource dict, or None on failure.
    """
    kwargs = {
        "userId": "me",
        "id": msg_id,
        "format": "metadata",
    }
    if metadata_headers:
        kwargs["metadataHeaders"] = metadata_headers

    request = service.users().messages().get(**kwargs)
    return execute_with_retry(request)
