# Disposable POC fixture

This fixture exists only to prove the engineering-runtime execution chain. It is not production billing code and contains no customer data.

The baseline tests subtotal calculation. The first remote Codex task adds apply_discount_cents with integer-cent arithmetic, basis-point discounts, half-up rounding and strict input validation.

Run baseline tests:

    python -m unittest discover -s examples/poc-fixture/tests -v
