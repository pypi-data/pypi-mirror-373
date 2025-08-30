"""Provide ansible integraitons."""

try:
    import ansible
except ImportError:
    raise ImportError(
        "The `ansible` package is required for using the regscale.ansible package. "
        "To install it, run: `pip install regscale-cli[ansible]`"
    )
