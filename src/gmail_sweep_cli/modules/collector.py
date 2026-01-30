"""Email collection from Gmail API."""

from __future__ import annotations

import email.utils
from datetime import datetime
from typing import Dict, List

from googleapiclient.discovery import build

from gmail_sweep_cli.modules.models import AddressInfo, CollectedData
from gmail_sweep_cli.utils.gmail_api import get_message_metadata, list_all_message_ids


def build_gmail_service(credentials):
    """Build the Gmail API service."""
    return build("gmail", "v1", credentials=credentials)


def _parse_from_header(headers: List[Dict]) -> str:
    """Extract the From address from message headers."""
    for header in headers:
        if header["name"].lower() == "from":
            return header["value"]
    return "unknown"


def _parse_subject(headers: List[Dict]) -> str:
    """Extract the Subject from message headers."""
    for header in headers:
        if header["name"].lower() == "subject":
            return header["value"]
    return "(no subject)"


def _parse_date(headers: List[Dict]) -> str:
    """Extract and parse the Date from message headers."""
    for header in headers:
        if header["name"].lower() == "date":
            raw = header["value"]
            try:
                parsed = email.utils.parsedate_to_datetime(raw)
                return parsed.strftime("%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                return raw
    return ""


def collect_emails(service, period_start: str, period_end: str) -> CollectedData:
    """Collect emails from Gmail API for the given period.

    Args:
        service: Gmail API service instance.
        period_start: Start date in YYYY-MM-DD format.
        period_end: End date in YYYY-MM-DD format.

    Returns:
        CollectedData with aggregated address information.
    """
    query = f"after:{period_start} before:{period_end}"
    addresses: Dict[str, AddressInfo] = {}
    total_fetched = 0

    print(f"Collecting emails from {period_start} to {period_end}...")

    message_ids = list_all_message_ids(service, query)
    if not message_ids:
        print("  No messages found.")

    for msg_id in message_ids:
        msg = get_message_metadata(service, msg_id, ["From", "Subject", "Date"])
        if msg is None:
            continue

        headers = msg.get("payload", {}).get("headers", [])
        from_addr = _parse_from_header(headers)
        subject = _parse_subject(headers)
        date_str = _parse_date(headers)

        if from_addr not in addresses:
            addresses[from_addr] = AddressInfo(
                count=0,
                frequency_days=0.0,
                subjects=[],
                received_dates=[],
            )

        info = addresses[from_addr]
        info.count += 1
        if subject not in info.subjects:
            info.subjects.append(subject)
        if date_str:
            info.received_dates.append(date_str)

        total_fetched += 1
        if total_fetched % 100 == 0:
            print(f"  {total_fetched} emails processed...")

    # Calculate frequency_days for each address
    for info in addresses.values():
        info.received_dates.sort(reverse=True)
        if info.count >= 2 and len(info.received_dates) >= 2:
            try:
                first = datetime.strptime(info.received_dates[-1], "%Y-%m-%d %H:%M:%S")
                last = datetime.strptime(info.received_dates[0], "%Y-%m-%d %H:%M:%S")
                span = (last - first).total_seconds() / 86400
                info.frequency_days = round(span / (info.count - 1), 1) if info.count > 1 else 0.0
            except (ValueError, TypeError):
                info.frequency_days = 0.0
        else:
            info.frequency_days = 0.0

    print(f"Collection complete: {len(addresses)} addresses, {total_fetched} emails.")

    return CollectedData(
        collected_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        period_start=period_start,
        period_end=period_end,
        addresses=addresses,
    )
