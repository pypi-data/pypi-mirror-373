
def print_separator(title: str = None):
    """Print a separator line with optional title for better log readability."""
    width = 80
    if title:
        print(f"\n{'=' * width}\n{title.center(width)}\n{'=' * width}")
    else:
        print(f"\n{'=' * width}")
