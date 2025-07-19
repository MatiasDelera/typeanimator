import logging

logger = logging.getLogger(__name__)

STYLE_PRESETS = {
    "BOLD": {"weight": 700, "italic": False},
    "ITALIC": {"weight": 400, "italic": True},
}

def get_style(name: str) -> dict:
    """Retrieve a style preset by name."""
    return STYLE_PRESETS.get(name, {})

def register() -> None:
    logger.debug("styles module registered")

def unregister() -> None:
    logger.debug("styles module unregistered")
