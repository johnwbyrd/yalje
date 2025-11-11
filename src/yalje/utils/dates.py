"""Date utilities."""

from datetime import datetime
from typing import Iterator, Tuple


def generate_month_range(
    start_year: int, start_month: int, end_year: int, end_month: int
) -> Iterator[Tuple[int, int]]:
    """Generate (year, month) tuples for a date range.

    Args:
        start_year: Starting year
        start_month: Starting month (1-12)
        end_year: Ending year
        end_month: Ending month (1-12)

    Yields:
        (year, month) tuples
    """
    current = datetime(start_year, start_month, 1)
    end = datetime(end_year, end_month, 1)

    while current <= end:
        yield (current.year, current.month)

        # Move to next month
        if current.month == 12:
            current = datetime(current.year + 1, 1, 1)
        else:
            current = datetime(current.year, current.month + 1, 1)


def format_month(year: int, month: int) -> str:
    """Format year and month as YYYY-MM string.

    Args:
        year: Year
        month: Month (1-12)

    Returns:
        Formatted string (e.g., "2023-01")
    """
    return f"{year:04d}-{month:02d}"
