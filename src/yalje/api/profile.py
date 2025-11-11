"""Profile parser for extracting journal metadata from LiveJournal profile pages."""

import html
import json
import re
from datetime import datetime
from typing import Optional

from yalje.core.exceptions import ParsingError
from yalje.utils.logging import get_logger

logger = get_logger("api.profile")

# Multi-language month name to number mapping
# Supports English, Russian, German, French, Spanish, and more
MONTH_NAMES = {
    # English
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7,
    "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,

    # Russian
    "января": 1, "февраля": 2, "марта": 3, "апреля": 4, "мая": 5, "июня": 6,
    "июля": 7, "августа": 8, "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12,
    "янв": 1, "фев": 2, "мар": 3, "апр": 4, "июн": 6, "июл": 7,
    "авг": 8, "сен": 9, "окт": 10, "ноя": 11, "дек": 12,

    # German
    "januar": 1, "februar": 2, "märz": 3, "april": 4, "mai": 5, "juni": 6,
    "juli": 7, "august": 8, "september": 9, "oktober": 10, "november": 11, "dezember": 12,

    # French
    "janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
    "juillet": 7, "août": 8, "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12,

    # Spanish
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
}


class ProfileData:
    """Container for profile metadata."""

    def __init__(
        self,
        post_count: int,
        created_year: int,
        created_month: int,
        updated_year: Optional[int] = None,
        updated_month: Optional[int] = None,
    ):
        """Initialize profile data.

        Args:
            post_count: Total number of journal entries
            created_year: Year journal was created
            created_month: Month journal was created (1-12)
            updated_year: Year of last update (optional)
            updated_month: Month of last update (optional)
        """
        self.post_count = post_count
        self.created_year = created_year
        self.created_month = created_month
        self.updated_year = updated_year or datetime.now().year
        self.updated_month = updated_month or datetime.now().month

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ProfileData(posts={self.post_count}, "
            f"created={self.created_year}-{self.created_month:02d}, "
            f"updated={self.updated_year}-{self.updated_month:02d})"
        )


class ProfileParser:
    """Parser for LiveJournal profile pages."""

    @staticmethod
    def parse_profile_data(html: str) -> ProfileData:
        """Extract profile metadata from HTML.

        This method uses a multi-strategy approach:
        1. Try to extract post count from Site.remote JSON (most reliable)
        2. Try to extract creation date from HTML
        3. Fall back to defaults if parsing fails

        Args:
            html: HTML content from profile page

        Returns:
            ProfileData object with extracted metadata

        Raises:
            ParsingError: If critical data cannot be extracted
        """
        logger.debug("Parsing profile data from HTML")

        # Extract post count from JSON
        post_count = ProfileParser._extract_post_count_json(html)
        if post_count is None:
            # Fallback: try HTML statistics section
            post_count = ProfileParser._extract_post_count_html(html)

        if post_count is None:
            raise ParsingError("Could not extract post count from profile page")

        # Extract creation date
        created_year, created_month = ProfileParser._extract_creation_date(html)

        # Extract update date (optional)
        updated_year, updated_month = ProfileParser._extract_update_date(html)

        logger.debug(
            f"Parsed profile: {post_count} posts, "
            f"created {created_year}-{created_month:02d}"
        )

        return ProfileData(
            post_count=post_count,
            created_year=created_year,
            created_month=created_month,
            updated_year=updated_year,
            updated_month=updated_month,
        )

    @staticmethod
    def _extract_post_count_json(html: str) -> Optional[int]:
        """Extract post count from Site.remote JSON.

        Args:
            html: HTML content

        Returns:
            Post count or None if not found
        """
        try:
            # Find Site.remote = {...};
            match = re.search(r"Site\.remote\s*=\s*(\{.*?\});", html, re.DOTALL)
            if not match:
                logger.debug("Site.remote JSON not found in profile page")
                return None

            # Parse JSON
            data = json.loads(match.group(1))

            # Extract post count (it's a string in the JSON)
            post_count_str = data.get("number_of_posts")
            if post_count_str:
                post_count = int(post_count_str)
                logger.debug(f"Extracted post count from JSON: {post_count}")
                return post_count

            return None
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.debug(f"Failed to parse post count from JSON: {e}")
            return None

    @staticmethod
    def _extract_post_count_html(html: str) -> Optional[int]:
        """Extract post count from HTML statistics section.

        Looks for the pattern:
        <div class="b-profile-stat-value">358</div>
        ...
        <div class="b-profile-stat-title">...Journal entries...</div>

        Args:
            html: HTML content

        Returns:
            Post count or None if not found
        """
        try:
            # Find stat value associated with "entrycount" class
            match = re.search(
                r'class="b-profile-stat-item\s+b-profile-stat-entrycount"[^>]*>.*?'
                r'class="b-profile-stat-value">(\d+)</div>',
                html,
                re.DOTALL,
            )
            if match:
                post_count = int(match.group(1))
                logger.debug(f"Extracted post count from HTML: {post_count}")
                return post_count

            return None
        except (ValueError, AttributeError) as e:
            logger.debug(f"Failed to parse post count from HTML: {e}")
            return None

    @staticmethod
    def _extract_creation_date(html_content: str) -> tuple[int, int]:
        """Extract journal creation date (language-agnostic).

        Looks for pattern:
        "Journal created: on  5 January 2011&nbsp;(#33401138)"

        Supports multiple languages via MONTH_NAMES mapping.

        Args:
            html_content: HTML content

        Returns:
            Tuple of (year, month)

        Raises:
            ParsingError: If creation date cannot be found
        """
        try:
            # Decode HTML entities (&nbsp; etc)
            decoded_html = html.unescape(html_content)

            # Find the creation date pattern
            # Pattern: "on  DD MONTH YYYY" followed by anything then "(#ID)"
            match = re.search(r"on\s+(\d+)\s+([а-яА-ЯёЁa-zA-Zäöüß]+)\s+(\d{4})", decoded_html)
            if not match:
                raise ParsingError("Could not find journal creation date in profile")

            _day, month_name, year = match.groups()

            # Look up month number from multi-language mapping
            month_lower = month_name.lower()
            month_num = MONTH_NAMES.get(month_lower)

            if not month_num:
                raise ParsingError(
                    f"Unknown month name '{month_name}'. "
                    f"Supported languages: English, Russian, German, French, Spanish"
                )

            year_int = int(year)

            logger.debug(f"Extracted creation date: {year_int}-{month_num:02d}")

            return (year_int, month_num)

        except (ValueError, AttributeError) as e:
            raise ParsingError(f"Failed to parse journal creation date: {e}")

    @staticmethod
    def _extract_update_date(html_content: str) -> tuple[Optional[int], Optional[int]]:
        """Extract journal last update date (language-agnostic).

        Looks for pattern in:
        <span class="tooltip" title='18 hours ago'>11 November 2025</span>

        Supports multiple languages via MONTH_NAMES mapping.

        Args:
            html_content: HTML content

        Returns:
            Tuple of (year, month) or (None, None) if not found
        """
        try:
            # Decode HTML entities
            decoded_html = html.unescape(html_content)

            # Find update date in tooltip
            match = re.search(
                r'<span class="tooltip"[^>]*>(\d+)\s+([а-яА-ЯёЁa-zA-Zäöüß]+)\s+(\d{4})</span>',
                decoded_html
            )
            if match:
                _day, month_name, year = match.groups()

                # Look up month number from multi-language mapping
                month_lower = month_name.lower()
                month_num = MONTH_NAMES.get(month_lower)

                if not month_num:
                    logger.debug(f"Unknown month name in update date: '{month_name}'")
                    return (None, None)

                year_int = int(year)

                logger.debug(f"Extracted update date: {year_int}-{month_num:02d}")
                return (year_int, month_num)

            # Fallback: current date
            return (None, None)

        except (ValueError, AttributeError) as e:
            logger.debug(f"Could not parse update date: {e}")
            return (None, None)
