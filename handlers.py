import bpy
from .curves import get_or_create_curve_node, evaluate_staged_curve

BLEND_WIDTH = 0.05  # Ancho de mezcla entre etapas
_handler_registered = False

def frame_change_handler(scene):
    props = getattr(scene, 'ta_letter_anim_props', None)
    if not props or not getattr(props, 'enable_live_preview', True):
        return  # Early exit: preview OFF o sin settings
    # Recolectar lista de letras
    letters = getattr(props, 'individual_letters', [])
    if not letters:
        return
    # Curvas por etapa
    curves = {}
    for stage in ['in', 'mid', 'out']:
        node = get_or_create_curve_node(getattr(props, 'base_name', 'DebugObj'), stage)
        if node and hasattr(node, 'mapping') and hasattr(node.mapping, 'curves') and node.mapping.curves:
            curves[stage] = node.mapping.curves[0]
        else:
            import logging
            logging.getLogger(__name__).error(f"No se pudo obtener el nodo de curva para la etapa '{stage}' en frame_change_handler. Node: {node}")
            return  # Early exit si falta alguna curva
    # Settings de timing
    start_at = getattr(props.timing, 'start_frame', 1)
    duration = max(getattr(props.timing, 'duration', 50), 1)
    overlap = getattr(props.timing, 'overlap', 0)
    loop_count = getattr(props.timing, 'loop_count', 1)
    frame_actual = scene.frame_current
    # Normalización de tiempo
    t_global = max(0.0, min(1.0, (frame_actual - start_at) / duration))
    if loop_count > 1:
        frame_local = (frame_actual - start_at) % duration
        t_global = frame_local / duration
    per_char_delay = overlap / max(len(letters), 1)
    in_end = getattr(props.stages, 'in_end', 0.2)
    out_start = getattr(props.stages, 'out_start', 0.8)
    # Caching de transforms iniciales
    for idx, letter in enumerate(letters):
        # Stagger/offset
        t_letra = max(0.0, min(1.0, t_global - (idx * per_char_delay)))
        # Etapa y t_stage
        if t_letra < in_end:
            stage = 'in'
            t_stage = t_letra / in_end if in_end > 0 else 0.0
        elif t_letra > out_start:
            stage = 'out'
            t_stage = (t_letra - out_start) / (1.0 - out_start) if out_start < 1.0 else 0.0
        else:
            stage = 'mid'
            t_stage = (t_letra - in_end) / (out_start - in_end) if out_start > in_end else 0.0
        t_stage = max(0.0, min(1.0, t_stage))
        value = curves[stage].evaluate(t_stage)
        # Aplicar a canales según flags
        base_pos = getattr(letter, 'base_location', letter.location.copy())
        base_rot = getattr(letter, 'base_rotation', letter.rotation_euler.copy())
        base_scale = getattr(letter, 'base_scale', letter.scale.copy())
        if getattr(props, 'flags_loc', True):
            letter.location.x = base_pos.x + value * getattr(props, 'amplitude_loc_x', 1.0)
        if getattr(props, 'flags_rot', False):
            letter.rotation_euler.z = base_rot.z + value * getattr(props, 'amplitude_rot_z', 0.0)
        if getattr(props, 'flags_scale', False):
            letter.scale = base_scale * (1 + value * getattr(props, 'amplitude_scale', 0.0))
        if getattr(props, 'flags_vis', False):
            letter.hide_viewport = value < 0.01
    # No keyframes, solo asignación directa
    # Al cambiar una propiedad relevante, refrescar preview con scene.frame_set(scene.frame_current)

def register_handler():
    global _handler_registered
    if not _handler_registered and frame_change_handler not in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.append(frame_change_handler)
        _handler_registered = True

def unregister_handler():
    try:
        # Ejemplo: solo remover si existe
        if hasattr(bpy.app.handlers, 'persistent_handler'):
            bpy.app.handlers.persistent_handler.remove()
    except Exception as e:
        print(f"[typeanimator] handlers.py error: {e}")
