try:
    import watchdog
except ImportError:
    raise ImportError(
        "The 'dev' package is required for using regscale.dev. To install it, run: `pip install regscale-cli[dev]`"
    )
