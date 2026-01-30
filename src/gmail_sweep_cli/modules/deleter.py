"""Email deletion (trash) functionality."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Set

from gmail_sweep_cli.utils.gmail_api import execute_with_retry, list_all_message_ids


@dataclass
class DeleteResult:
    """Result of a deletion operation for one address."""

    address: str = ""
    moved: int = 0
    skipped_starred: int = 0
    skipped_important: int = 0
    total: int = 0


def delete_emails_for_addresses(service, addresses: Set[str]) -> List[DeleteResult]:
    """Move all emails from the given addresses to trash.

    Skips starred and important emails.

    Args:
        service: Gmail API service instance.
        addresses: Set of From addresses to delete.

    Returns:
        List of DeleteResult for each address.
    """
    results: List[DeleteResult] = []
    total_addresses = len(addresses)

    print("Deleting emails...")

    for idx, address in enumerate(sorted(addresses), 1):
        result = DeleteResult(address=address)
        # Extract email part for query (handle "Name <email>" format)
        query_addr = address
        if "<" in address and ">" in address:
            query_addr = address[address.index("<") + 1 : address.index(">")]

        query = f"from:{query_addr}"
        all_message_ids = list_all_message_ids(service, query)
        result.total = len(all_message_ids)

        # Process each message
        for msg_idx, msg_id in enumerate(all_message_ids):
            print(f"\r[{idx}/{total_addresses}] {address}: {msg_idx + 1}/{result.total} processing...", end="", flush=True)

            msg_request = (
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=msg_id,
                    format="metadata",
                    metadataHeaders=["From"],
                )
            )
            msg = execute_with_retry(msg_request)
            if msg is None:
                continue

            label_ids = msg.get("labelIds", [])

            if "STARRED" in label_ids:
                result.skipped_starred += 1
                continue
            if "IMPORTANT" in label_ids:
                result.skipped_important += 1
                continue

            # Move to trash
            trash_request = (
                service.users()
                .messages()
                .trash(
                    userId="me",
                    id=msg_id,
                )
            )
            execute_with_retry(trash_request)
            result.moved += 1

        print()  # newline after progress
        results.append(result)

    return results


def print_delete_results(results: List[DeleteResult]) -> None:
    """Print the deletion result summary."""
    print()
    print("=== Delete Result ===")

    total_moved = 0
    total_starred = 0
    total_important = 0

    for r in results:
        print(f"{r.address}: {r.moved} moved, {r.skipped_starred} skipped (starred), {r.skipped_important} skipped (important)")
        total_moved += r.moved
        total_starred += r.skipped_starred
        total_important += r.skipped_important

    print()
    print(f"Total: {total_moved} moved, {total_starred} skipped (starred), {total_important} skipped (important)")
    print()
    input("Press Enter to continue...")
