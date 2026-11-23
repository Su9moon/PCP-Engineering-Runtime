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


def apply_discount_cents(subtotal_cents: int, discount_basis_points: int) -> int:
    """Apply a basis-point discount and round half-up to the nearest cent."""
    if type(subtotal_cents) is not int or subtotal_cents < 0:
        raise ValueError("subtotal_cents must be a non-negative integer")
    if type(discount_basis_points) is not int or not 0 <= discount_basis_points <= 10000:
        raise ValueError("discount_basis_points must be an integer from 0 to 10000")
    return (subtotal_cents * (10000 - discount_basis_points) + 5000) // 10000
