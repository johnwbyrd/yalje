"""Utility functions for parsers."""

from typing import Optional


def clean_html_content(html: Optional[str]) -> Optional[str]:
    """Clean HTML content while preserving structure.

    Args:
        html: HTML string

    Returns:
        Cleaned HTML or None
    """
    if html is None:
        return None

    # TODO: Implement any necessary HTML cleaning
    # For now, just strip leading/trailing whitespace
    return html.strip()


def extract_cdata(text: Optional[str]) -> Optional[str]:
    """Extract content from CDATA section.

    Args:
        text: Text that may contain CDATA

    Returns:
        Content without CDATA markers
    """
    if text is None:
        return None

    # lxml typically handles CDATA automatically,
    # but this is here for manual parsing if needed
    if text.startswith("<![CDATA[") and text.endswith("]]>"):
        return text[9:-3]

    return text
