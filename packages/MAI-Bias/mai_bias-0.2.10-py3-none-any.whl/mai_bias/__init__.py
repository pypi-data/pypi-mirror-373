import logging

logging.getLogger().setLevel(logging.ERROR)


try:
    from mai_bias import states
    from mai_bias import backend
except ImportError:
    print(
        "Failed to import MAI-Bias frontend (you are probably lacking a graphics environment).\n"
        "`python -m mai_bias.cli` still works to get an interactive console, but `python -m mai_bias.app` does not."
    )
