"""Small deterministic pricing fixture for the remote-worker POC."""


def subtotal_cents(lines: list[tuple[int, int]]) -> int:
    """Return the total for (quantity, unit_price_cents) lines."""
    total = 0
    for quantity, unit_price_cents in lines:
        if type(quantity) is not int or quantity <= 0:
            raise ValueError("quantity must be a positive integer")
        if type(unit_price_cents) is not int or unit_price_cents < 0:
            raise ValueError("unit_price_cents must be a non-negative integer")
        total += quantity * unit_price_cents
    return total
