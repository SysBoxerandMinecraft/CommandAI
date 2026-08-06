"""Utility helpers for CommandAI.

Keep this module small — other modules may import logging helpers from here.
"""
import logging


def setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


__all__ = ["setup_logging"]

