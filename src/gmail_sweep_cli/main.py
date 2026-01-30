"""CLI entry point for gmail_sweep_cli."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import click

from gmail_sweep_cli.modules.auth import load_credentials, run_auth_flow
from gmail_sweep_cli.modules.collector import build_gmail_service, collect_emails
from gmail_sweep_cli.modules.deleter import delete_emails_for_addresses, print_delete_results
from gmail_sweep_cli.modules.display import (
    display_delete_confirmation,
    display_detail_screen,
    display_main_screen,
    display_marked_list,
)
from gmail_sweep_cli.modules.models import AppState, CollectedData


def _compute_period(days: int, start: str | None, end: str | None, shift: int = 0):
    """Compute the collection period.

    Args:
        days: Number of days for the period.
        start: Explicit start date (YYYY-MM-DD) or None.
        end: Explicit end date (YYYY-MM-DD) or None.
        shift: Number of period shifts (negative = past, positive = future).

    Returns:
        Tuple of (start_date_str, end_date_str, days).
    """
    today = datetime.now().date()

    if start and end:
        s = datetime.strptime(start, "%Y-%m-%d").date()
        e = datetime.strptime(end, "%Y-%m-%d").date()
        days = (e - s).days
    else:
        e = today
        s = e - timedelta(days=days)

    if shift != 0:
        offset = timedelta(days=days * shift)
        s = s + offset
        e = e + offset
        # Do not go beyond today
        if e > today:
            e = today
            s = e - timedelta(days=days)

    return s.strftime("%Y-%m-%d"), e.strftime("%Y-%m-%d"), days


def _get_data_path(cache_dir: str, email: str) -> Path:
    """Return the JSON data file path for the given email."""
    return Path(cache_dir) / f"{email}_data.json"


def _collect_and_save(service, state: AppState, cache_dir: str) -> None:
    """Collect emails from Gmail API and save to JSON."""
    data = collect_emails(service, state.period_start, state.period_end)
    data_path = _get_data_path(cache_dir, state.email)
    data.save(data_path)
    state.data = data


def _handle_detail(state: AppState, number: int) -> None:
    """Handle the detail view for a specific address number."""
    if not state.data:
        return

    sorted_items = state.data.sorted_addresses()
    idx = number - 1
    if idx < 0 or idx >= len(sorted_items):
        print("Invalid number.")
        return

    address, info = sorted_items[idx]
    display_detail_screen(address, info, state)

    while True:
        cmd = input("> ").strip()
        if cmd == "":
            break
        if cmd == "mark":
            state.marked_addresses.add(address)
            print(f"Marked: {address}")
            break
        print("Invalid input. Press Enter to go back or type 'mark' to mark for deletion.")


def _delete_cache(cache_dir: str, email: str) -> None:
    """Delete the cache JSON file for the given email."""
    data_path = _get_data_path(cache_dir, email)
    if data_path.exists():
        data_path.unlink()


def _run_interactive(state: AppState, service, cache_dir: str) -> None:
    """Run the interactive main loop."""
    while True:
        display_main_screen(state)

        cmd = input("> ").strip()

        if cmd == "q":
            print("Bye!")
            break

        should_exit = _dispatch_command(cmd, state, service, cache_dir)
        if should_exit:
            break


def _dispatch_command(cmd: str, state: AppState, service, cache_dir: str) -> bool:
    """Dispatch a single command from the interactive loop.

    Returns True if the program should exit after this command.
    """
    if cmd == "r":
        _collect_and_save(service, state, cache_dir)
        state.current_page = 1
    elif cmd == "prev":
        state.shift_count -= 1
        period_start, period_end, _ = _compute_period(state.days, None, None, state.shift_count)
        state.period_start = period_start
        state.period_end = period_end
        _collect_and_save(service, state, cache_dir)
        state.current_page = 1
    elif cmd == "next":
        state.shift_count += 1
        period_start, period_end, _ = _compute_period(state.days, None, None, state.shift_count)
        state.period_start = period_start
        state.period_end = period_end
        _collect_and_save(service, state, cache_dir)
        state.current_page = 1
    elif cmd == "<":
        if state.current_page > 1:
            state.current_page -= 1
        else:
            print("Already on the first page.")
    elif cmd == ">":
        if state.current_page < state.total_pages:
            state.current_page += 1
        else:
            print("Already on the last page.")
    elif cmd == "l":
        display_marked_list(state)
        input("Press Enter to continue...")
    elif cmd == "c":
        state.marked_addresses.clear()
        print("All marks cleared.")
    elif cmd == "all-delete":
        confirmed = display_delete_confirmation(state)
        if confirmed:
            results = delete_emails_for_addresses(service, state.marked_addresses)
            print_delete_results(results)
            _delete_cache(cache_dir, state.email)
            print("Cache cleared. Exiting.")
            return True
        if state.marked_addresses:
            print("Cancelled.")
    else:
        try:
            number = int(cmd)
            _handle_detail(state, number)
        except ValueError:
            print("Invalid input.")
    return False


@click.command()
@click.argument("email")
@click.option("--auth", "-a", "run_auth", is_flag=True, default=False, help="Run authentication flow.")
@click.option("--days", "-d", default=30, type=int, help="Collection period in days (default: 30).")
@click.option("--start", "-s", default=None, help="Collection start date (YYYY-MM-DD).")
@click.option("--end", "-e", default=None, help="Collection end date (YYYY-MM-DD).")
@click.option("--credentials", "-c", default="./credentials/client_secret.json", help="Path to client_secret.json.")
@click.option("--token-dir", "-t", default="./credentials/", help="Token storage directory.")
@click.option("--cache-dir", default="./cache/", help="Cache directory for collected data.")
def main(email, run_auth, days, start, end, credentials, token_dir, cache_dir):  # pylint: disable=too-many-positional-arguments
    """Gmail Sweep CLI - Aggregate and clean up Gmail by sender address.

    EMAIL is the target Gmail address (required).
    """
    if run_auth:
        run_auth_flow(email, credentials, token_dir)
        return

    # Load credentials
    creds = load_credentials(email, token_dir)
    service = build_gmail_service(creds)

    # Compute period
    period_start, period_end, computed_days = _compute_period(days, start, end)

    state = AppState(
        email=email,
        period_start=period_start,
        period_end=period_end,
        days=computed_days,
    )

    # Try loading existing data
    data_path = _get_data_path(cache_dir, email)
    existing = CollectedData.load(data_path)
    if existing:
        print(f"Loaded existing data from {data_path}")
        state.data = existing
        state.period_start = existing.period_start
        state.period_end = existing.period_end
    else:
        _collect_and_save(service, state, cache_dir)

    _run_interactive(state, service, cache_dir)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
