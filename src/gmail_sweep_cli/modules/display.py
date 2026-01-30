"""Console display and interactive UI for gmail_sweep_cli."""

from __future__ import annotations

import os

from gmail_sweep_cli.modules.models import AppState


def clear_screen() -> None:
    """Clear the console screen."""
    os.system("cls" if os.name == "nt" else "clear")


def display_main_screen(state: AppState) -> None:
    """Display the main screen with the address list."""
    clear_screen()

    if not state.data:
        print("No data loaded.")
        return

    data = state.data
    total_addresses = len(data.addresses)
    total_emails = data.total_emails

    print("=== Gmail Sweep CLI ===")
    print(f"Account: {state.email}")
    print(f"Period: {data.period_start} ~ {data.period_end} ({state.days} days)")
    print(f"Total: {total_addresses} addresses, {total_emails} emails")
    print()

    # Table header
    print(f" {'No.':>4} | {'Address':<34} | {'Count':>5} | {'Freq(days)':>10} | Subject")
    print("-" * 5 + "+" + "-" * 36 + "+" + "-" * 7 + "+" + "-" * 12 + "+" + "-" * 21)

    # Page items
    items = state.get_page_items()
    start_idx = state.page_start_index()

    for i, (addr, info) in enumerate(items):
        no = start_idx + i
        display_addr = _truncate(addr, 34)
        subject = _truncate(info.subjects[0], 19) if info.subjects else ""
        print(f" {no:>4} | {display_addr:<34} | {info.count:>5} | {info.frequency_days:>10.1f} | {subject}")

    print()
    total_items = len(data.addresses)
    page_end = min(start_idx + state.page_size - 1, total_items)
    print(f"Page {state.current_page}/{state.total_pages} ({start_idx}-{page_end} of {total_items})")
    print()
    print("[r]Re-collect [prev/next]Period [</>]Page [q]Quit [l]List marked [c]Clear marks")
    print(f"[all-delete]Execute delete [{start_idx}-{page_end}]Detail")


def display_detail_screen(address: str, info, state: AppState) -> None:
    """Display the detail screen for a single address."""
    clear_screen()

    marked = address in state.marked_addresses
    mark_label = " [MARKED]" if marked else ""

    print("=== Address Detail ===")
    print(f"Address: {address}{mark_label}")
    print(f"Count: {info.count} emails")
    print(f"Frequency: {info.frequency_days} days (average interval)")
    print()

    print("--- Received Dates ---")
    for date_str in info.received_dates[:20]:
        print(date_str)
    if len(info.received_dates) > 20:
        print(f"  ... and {len(info.received_dates) - 20} more")
    print()

    print("--- Subjects (distinct) ---")
    for subject in info.subjects[:20]:
        print(f"- {subject}")
    if len(info.subjects) > 20:
        print(f"  ... and {len(info.subjects) - 20} more")
    print()

    print("[Enter]Back [mark]Mark for deletion")


def display_marked_list(state: AppState) -> None:
    """Display the list of marked addresses."""
    clear_screen()
    if not state.marked_addresses:
        print("No addresses marked for deletion.")
    else:
        print("=== Marked Addresses ===")
        for i, addr in enumerate(sorted(state.marked_addresses), 1):
            count = 0
            if state.data and addr in state.data.addresses:
                count = state.data.addresses[addr].count
            print(f"  {i}. {addr} ({count} emails in current period)")
    print()


def display_delete_confirmation(state: AppState) -> bool:
    """Display the delete confirmation screen. Returns True if user confirms."""
    if not state.marked_addresses:
        print("No addresses marked for deletion.")
        return False

    clear_screen()
    print("=== Delete Confirmation ===")
    print("The following addresses are marked for deletion:")
    print()

    for i, addr in enumerate(sorted(state.marked_addresses), 1):
        count = 0
        if state.data and addr in state.data.addresses:
            count = state.data.addresses[addr].count
        print(f"  {i}. {addr} ({count} emails in current period)")

    print()
    print("WARNING: All emails from these addresses (across ALL periods) will be moved to Trash.")
    print("NOTE: Starred and Important emails will be skipped.")
    print()
    print("All emails from marked addresses will be moved to Trash.")
    print("(Starred and Important emails will be skipped)")

    answer = input("Are you sure? [Y/other]: ").strip()
    return answer == "Y"


def _truncate(text: str, max_len: int) -> str:
    """Truncate text with ellipsis if it exceeds max_len."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."
