"""Data models for gmail_sweep_cli."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


@dataclass
class AddressInfo:
    """Aggregated information for a single sender address."""

    count: int = 0
    frequency_days: float = 0.0
    subjects: List[str] = field(default_factory=list)
    received_dates: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "count": self.count,
            "frequency_days": self.frequency_days,
            "subjects": self.subjects,
            "received_dates": self.received_dates,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AddressInfo:
        """Create from dictionary."""
        return cls(
            count=data.get("count", 0),
            frequency_days=data.get("frequency_days", 0.0),
            subjects=data.get("subjects", []),
            received_dates=data.get("received_dates", []),
        )


@dataclass
class CollectedData:
    """Collected email data for an account."""

    collected_at: str = ""
    period_start: str = ""
    period_end: str = ""
    addresses: Dict[str, AddressInfo] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "collected_at": self.collected_at,
            "period": {
                "start": self.period_start,
                "end": self.period_end,
            },
            "addresses": {addr: info.to_dict() for addr, info in self.addresses.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CollectedData:
        """Create from dictionary."""
        period = data.get("period", {})
        addresses_raw = data.get("addresses", {})
        addresses = {addr: AddressInfo.from_dict(info) for addr, info in addresses_raw.items()}
        return cls(
            collected_at=data.get("collected_at", ""),
            period_start=period.get("start", ""),
            period_end=period.get("end", ""),
            addresses=addresses,
        )

    def save(self, path: Path) -> None:
        """Save collected data to JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: Path) -> Optional[CollectedData]:
        """Load collected data from JSON file. Returns None if not found."""
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def sorted_addresses(self) -> List[tuple]:
        """Return addresses sorted by count descending."""
        return sorted(self.addresses.items(), key=lambda x: x[1].count, reverse=True)

    @property
    def total_emails(self) -> int:
        """Total number of emails across all addresses."""
        return sum(info.count for info in self.addresses.values())


@dataclass
class AppState:  # pylint: disable=too-many-instance-attributes
    """Application runtime state."""

    email: str = ""
    period_start: str = ""
    period_end: str = ""
    days: int = 30
    data: Optional[CollectedData] = None
    marked_addresses: Set[str] = field(default_factory=set)
    current_page: int = 1
    page_size: int = 20
    shift_count: int = 0

    @property
    def total_pages(self) -> int:
        """Total number of pages."""
        if not self.data:
            return 0
        total = len(self.data.addresses)
        return max(1, (total + self.page_size - 1) // self.page_size)

    def get_page_items(self) -> List[tuple]:
        """Get items for the current page."""
        if not self.data:
            return []
        sorted_items = self.data.sorted_addresses()
        start = (self.current_page - 1) * self.page_size
        end = start + self.page_size
        return sorted_items[start:end]

    def page_start_index(self) -> int:
        """1-based start index for current page."""
        return (self.current_page - 1) * self.page_size + 1
