"""Text formatting utilities."""


def format_price(amount: int) -> str:
    """Format price with thousand separators: 1234567 -> 1 234 567"""
    return f"{amount:,}".replace(",", " ")


def format_subscribers(count: int) -> str:
    """Format subscriber count: 12500 -> 12.5K"""
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M"
    elif count >= 1_000:
        return f"{count / 1_000:.1f}K"
    return str(count)


def truncate(text: str, max_len: int = 100) -> str:
    """Truncate text with ellipsis."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."
