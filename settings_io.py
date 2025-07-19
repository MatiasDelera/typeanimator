import bpy
import json
from pathlib import Path
from .preferences import TAAddonPreferences
from .presets import safe_json_load

LAST_SETTINGS_FILE = Path(__file__).parent / "last_settings.json"

def save_last_settings():
    addon = bpy.context.preferences.addons.get(__name__)
    prefs = addon.preferences if addon else None
    if not prefs or not prefs.remember_settings:
        return
    scene = bpy.context.scene
    if not hasattr(scene, "ta_letter_anim_props"):
        return
    props = scene.ta_letter_anim_props
    data = {name: getattr(props, name) for name in props.__annotations__.keys()}
    with LAST_SETTINGS_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_last_settings():
    try:
        # Check if context is available
        if not hasattr(bpy.context, 'preferences'):
            return
            
        addon = bpy.context.preferences.addons.get(__name__)
        prefs = addon.preferences if addon else None
        if not prefs or not prefs.remember_settings:
            return
            
        # Check if scene context is available
        if not hasattr(bpy.context, 'scene'):
            return
            
        scene = bpy.context.scene
        if not hasattr(scene, "ta_letter_anim_props") or not LAST_SETTINGS_FILE.exists():
            return
        props = scene.ta_letter_anim_props
        try:
            with LAST_SETTINGS_FILE.open("r", encoding="utf-8") as f:
                data = safe_json_load(f, LAST_SETTINGS_FILE)
            for key, val in data.items():
                if hasattr(props, key):
                    try:
                        setattr(props, key, val)
                    except Exception:
                        pass
        except Exception as e:
            import logging
            logger = logging.getLogger("typeanimator")
            logger.error(f"Failed loading last settings: {e}")
    except Exception as e:
        # Don't fail registration if settings can't be loaded
        import logging
        logger = logging.getLogger("typeanimator")
        logger.warning(f"Could not load last settings during registration: {e}")
