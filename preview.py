"""Create a temporary preview of the animated text and manage preview animation timer."""

import bpy
import logging

logger = logging.getLogger(__name__)

# --- Preview Object Utilities ---
def create_preview(text: str) -> bpy.types.Object:
    """Create a new text object in the scene for preview purposes."""
    font_curve = bpy.data.curves.new(name="PreviewText", type='FONT')
    font_curve.body = text
    obj = bpy.data.objects.new("PreviewText", font_curve)
    bpy.context.collection.objects.link(obj)
    logger.debug("Preview object created")
    return obj

def remove_preview(obj: bpy.types.Object) -> None:
    """Remove the preview object from the scene."""
    bpy.data.objects.remove(obj, do_unlink=True)
    logger.debug("Preview object removed")

# --- Preview Animation Timer ---
_timer = None

def _timer_callback():
    scene = bpy.context.scene
    props = getattr(scene, 'ta_letter_anim_props', None)
    if props is not None and hasattr(props, 'preview_frame'):
        props.preview_frame += 1
        scene.frame_set(props.preview_frame)
    return 0.1

def start_preview():
    global _timer
    if _timer is None:
        _timer = bpy.app.timers.register(_timer_callback)

def stop_preview():
    global _timer
    if _timer is not None:
        try:
            bpy.app.timers.unregister(_timer_callback)
        except Exception:
            pass
        _timer = None

def register() -> None:
    logger.debug("preview module registered")
    # No es necesario iniciar el timer al registrar el módulo

def unregister() -> None:
    logger.debug("preview module unregistered")
    # Asegura que el timer se detenga al desregistrar el módulo
    stop_preview()
