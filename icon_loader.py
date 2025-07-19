import logging
from pathlib import Path

import bpy

logger = logging.getLogger(__name__)

try:
    import bpy.utils.previews as _previews
except Exception:  # pragma: no cover - Blender not available
    _previews = None

preview_collections = {}
ICON_IDS: dict[str, int] = {}

def register() -> None:
    """Load preview icons for the UI."""
    if _previews is None:
        logger.debug("bpy.utils.previews not available")
        return

    try:
        pcoll = _previews.new()
        icons_dir = Path(__file__).parent / "icons"

        if not icons_dir.exists():
            logger.warning(f"Icons directory not found: {icons_dir}")
            return

        icon_files = list(icons_dir.glob("*.png"))
        logger.debug(f"Found {len(icon_files)} icon files in {icons_dir}")

        for path in icon_files:
            try:
                icon_name = path.stem.upper()
                pcoll.load(icon_name, str(path), 'IMAGE')
                ICON_IDS[icon_name] = pcoll[icon_name].icon_id
                logger.debug(f"Loaded icon: {icon_name} -> {ICON_IDS[icon_name]}")
            except Exception as e:
                logger.error(f"Failed to load icon {path}: {e}")

        preview_collections["main"] = pcoll
        logger.debug("Loaded %d preview icons: %s", len(ICON_IDS), list(ICON_IDS.keys()))

    except Exception as e:
        logger.error(f"Error in icon_loader.register(): {e}")
        ICON_IDS.clear()

def get_icon_id(icon_name: str) -> int:
    """Get icon ID by name."""
    return ICON_IDS.get(icon_name.upper(), 0)

def unregister() -> None:
    """Unload preview icons."""
    ICON_IDS.clear()
    if _previews is None:
        return
    pcoll = preview_collections.pop("main", None)
    if pcoll:
        _previews.remove(pcoll)
    logger.debug("Unloaded preview icons")
