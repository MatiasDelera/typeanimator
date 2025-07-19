"""
Utilidades centralizadas para TypeAnimator
"""

import bpy
import logging
from mathutils import Vector
from typing import List, Tuple, Any, Optional

from .constants import (
    LETTER_PROPERTY, ANIMATION_GROUP_PROPERTY, ROOT_SUFFIX, ANIMATION_GROUP_SUFFIX,
    ORIG_LOCATION, ORIG_ROTATION, ORIG_SCALE, ROOT_NAME,
    MESH_TYPE, EMPTY_TYPE, FONT_TYPE, LOG_FILENAME,
    MIN_FRAME, MAX_FRAME, MIN_DURATION, MAX_DURATION, MIN_OVERLAP, MAX_OVERLAP,
    ERROR_MESSAGES, DEFAULT_DURATION
)

# Configurar logger
logger = logging.getLogger(__name__)

def setup_logging():
    """Configura el sistema de logging para typeanimator"""
    if not logger.handlers:
        # Configurar handler para consola
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # Configurar nivel de logging
        logger.setLevel(logging.INFO)

        logger.info("Sistema de logging configurado para typeanimator")

def safe_execute(func):
    """Decorador para ejecutar funciones de manera segura"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error en {func.__name__}: {e}", exc_info=True)
            return None
    return wrapper

def clamp_value(value, min_val, max_val):
    """Clampa un valor entre un mínimo y máximo."""
    return max(min_val, min(value, max_val))

def validate_frame_range(start_frame, end_frame, duration=None):
    """Valida y corrige un rango de frames."""
    start_frame = clamp_value(start_frame, MIN_FRAME, MAX_FRAME)
    end_frame = clamp_value(end_frame, MIN_FRAME, MAX_FRAME)
    
    if start_frame >= end_frame:
        start_frame = MIN_FRAME
        end_frame = start_frame + DEFAULT_DURATION
    
    if duration is not None:
        duration = clamp_value(duration, MIN_DURATION, MAX_DURATION)
        end_frame = start_frame + duration
    
    return start_frame, end_frame, duration

def validate_duration(duration):
    """Valida y corrige la duración de animación."""
    return clamp_value(duration, MIN_DURATION, MAX_DURATION)

def validate_overlap(overlap):
    """Valida y corrige el solapamiento entre letras."""
    return clamp_value(overlap, MIN_OVERLAP, MAX_OVERLAP)

def validate_percentage(value, name="valor"):
    """Valida un valor de porcentaje (0-100)."""
    clamped = clamp_value(value, 0, 100)
    if clamped != value:
        logger.warning(f"{name} ajustado de {value} a {clamped}")
    return clamped

def validate_float_range(value, min_val=0.0, max_val=1.0, name="valor"):
    """Valida un valor float en un rango específico."""
    clamped = clamp_value(value, min_val, max_val)
    if clamped != value:
        logger.warning(f"{name} ajustado de {value} a {clamped}")
    return clamped

def is_valid_object(obj):
    """Verifica si un objeto es válido y no ha sido borrado."""
    try:
        if obj is None:
            return False
        if not hasattr(obj, 'name'):
            return False
        if obj.name not in bpy.data.objects:
            return False
        return True
    except Exception:
        return False

def is_letter_object(obj):
    """Verifica si un objeto es una letra válida."""
    if not is_valid_object(obj):
        return False
    return (obj.type == MESH_TYPE and 
            hasattr(obj, LETTER_PROPERTY) and 
            getattr(obj, LETTER_PROPERTY, False))

def is_root_object(obj):
    """Verifica si un objeto es un root válido."""
    if not is_valid_object(obj):
        return False
    return (obj.type == EMPTY_TYPE and 
            obj.name.endswith(ROOT_SUFFIX))

def is_animation_group(obj):
    """Verifica si un objeto es un grupo de animación válido."""
    if not is_valid_object(obj):
        return False
    return (obj.type == EMPTY_TYPE and 
            hasattr(obj, ANIMATION_GROUP_PROPERTY) and 
            getattr(obj, ANIMATION_GROUP_PROPERTY, False))

def get_valid_letters_from_selection(context):
    """Obtiene letras válidas de la selección actual."""
    valid_letters = []
    for obj in context.selected_objects:
        if is_letter_object(obj):
            valid_letters.append(obj)
        elif is_root_object(obj):
            # Buscar letras hijas del root
            for child in obj.children_recursive:
                if is_letter_object(child):
                    valid_letters.append(child)
    return valid_letters

def get_valid_roots_from_selection(context):
    """Obtiene roots válidos de la selección actual."""
    valid_roots = []
    for obj in context.selected_objects:
        if is_root_object(obj):
            valid_roots.append(obj)
    return valid_roots

def validate_animation_properties(props):
    """Valida y corrige todas las propiedades de animación."""
    if not props:
        return False
    
    try:
        # Validar timing
        if hasattr(props, 'timing'):
            timing = props.timing
            if hasattr(timing, 'start_frame'):
                timing.start_frame = clamp_value(timing.start_frame, MIN_FRAME, MAX_FRAME)
            if hasattr(timing, 'end_frame'):
                timing.end_frame = clamp_value(timing.end_frame, MIN_FRAME, MAX_FRAME)
            if hasattr(timing, 'duration'):
                timing.duration = validate_duration(timing.duration)
            if hasattr(timing, 'overlap'):
                timing.overlap = validate_overlap(timing.overlap)
        
        # Validar motion
        if hasattr(props, 'motion'):
            motion = props.motion
            if hasattr(motion, 'scale_x'):
                motion.scale_x = validate_float_range(motion.scale_x, 0.0, 10.0, "scale_x")
            if hasattr(motion, 'scale_y'):
                motion.scale_y = validate_float_range(motion.scale_y, 0.0, 10.0, "scale_y")
            if hasattr(motion, 'scale_z'):
                motion.scale_z = validate_float_range(motion.scale_z, 0.0, 10.0, "scale_z")
            if hasattr(motion, 'rotation_x'):
                motion.rotation_x = clamp_value(motion.rotation_x, -360, 360)
            if hasattr(motion, 'rotation_y'):
                motion.rotation_y = clamp_value(motion.rotation_y, -360, 360)
            if hasattr(motion, 'rotation_z'):
                motion.rotation_z = clamp_value(motion.rotation_z, -360, 360)
        
        # Validar style
        if hasattr(props, 'style'):
            style = props.style
            if hasattr(style, 'opacity'):
                style.opacity = validate_float_range(style.opacity, 0.0, 1.0, "opacity")
            if hasattr(style, 'blur'):
                style.blur = validate_float_range(style.blur, 0.0, 10.0, "blur")
        
        return True
        
    except Exception as e:
        logger.error(f"Error validando propiedades: {e}")
        return False

def validate_scene_state(context):
    """Valida el estado general de la escena."""
    if not context or not context.scene:
        return False, "Contexto o escena inválida"
    
    # Verificar que las propiedades están inicializadas
    if not hasattr(context.scene, 'ta_letter_anim_props'):
        return False, "Propiedades de TypeAnimator no inicializadas"
    
    return True, "Escena válida"

def validate_text_object(obj):
    """Valida si un objeto es un texto válido para animación."""
    if not is_valid_object(obj):
        return False, "Objeto inválido o borrado"
    
    if obj.type != FONT_TYPE:
        return False, "Objeto no es de tipo texto"
    
    if not obj.data or not obj.data.body:
        return False, "Texto sin contenido"
    
    return True, "Texto válido"

def cleanup_invalid_references():
    """Limpia referencias inválidas en la escena."""
    cleaned_count = 0
    
    # Limpiar referencias a objetos borrados en propiedades
    for scene in bpy.data.scenes:
        if hasattr(scene, 'ta_letter_anim_props'):
            props = scene.ta_letter_anim_props
            if hasattr(props, 'focused_text') and props.focused_text:
                if props.focused_text not in bpy.data.objects:
                    props.focused_text = ""
                    cleaned_count += 1
    
    # Limpiar referencias en WindowManager
    if hasattr(bpy.context.window_manager, 'ta_status'):
        # Resetear estado si es necesario
        pass
    
    logger.info(f"Limpieza completada: {cleaned_count} referencias inválidas removidas")
    return cleaned_count

def repair_scene_properties():
    """Repara propiedades de escena corruptas."""
    repaired_count = 0
    
    for scene in bpy.data.scenes:
        try:
            # Forzar inicialización de propiedades si no existen
            if not hasattr(scene, 'ta_letter_anim_props'):
                # Esto debería ser manejado por el sistema de registro
                logger.warning(f"Propiedades faltantes en escena: {scene.name}")
                continue
            
            # Validar propiedades existentes
            props = scene.ta_letter_anim_props
            if validate_animation_properties(props):
                repaired_count += 1
                
        except Exception as e:
            logger.error(f"Error reparando escena {scene.name}: {e}")
    
    logger.info(f"Reparación completada: {repaired_count} escenas procesadas")
    return repaired_count

def get_scene_diagnostics(context):
    """Obtiene diagnóstico completo del estado de la escena."""
    diagnostics = {
        'scene_valid': False,
        'properties_initialized': False,
        'text_objects': 0,
        'letter_objects': 0,
        'root_objects': 0,
        'animation_groups': 0,
        'errors': [],
        'warnings': []
    }
    
    try:
        # Validar contexto
        if not context or not context.scene:
            diagnostics['errors'].append("Contexto o escena inválida")
            return diagnostics
        
        diagnostics['scene_valid'] = True
        
        # Verificar propiedades
        if hasattr(context.scene, 'ta_letter_anim_props'):
            diagnostics['properties_initialized'] = True
        else:
            diagnostics['errors'].append("Propiedades de TypeAnimator no inicializadas")
        
        # Contar objetos
        for obj in bpy.data.objects:
            if obj.type == FONT_TYPE:
                diagnostics['text_objects'] += 1
            elif is_letter_object(obj):
                diagnostics['letter_objects'] += 1
            elif is_root_object(obj):
                diagnostics['root_objects'] += 1
            elif is_animation_group(obj):
                diagnostics['animation_groups'] += 1
        
        # Verificar consistencia
        if diagnostics['letter_objects'] > 0 and diagnostics['root_objects'] == 0:
            diagnostics['warnings'].append("Letras sin root asociado")
        
        if diagnostics['root_objects'] > 0 and diagnostics['letter_objects'] == 0:
            diagnostics['warnings'].append("Roots sin letras asociadas")
        
    except Exception as e:
        diagnostics['errors'].append(f"Error en diagnóstico: {e}")
    
    return diagnostics

def find_letters(context, search_selected=True, search_scene=False):
    """
    Encuentra empties de letras en el contexto dado.

    Args:
        context: Contexto de Blender
        search_selected: Buscar en objetos seleccionados
        search_scene: Buscar en toda la escena

    Returns:
        List[bpy.types.Object]: Lista de empties de letras
    """
    letters = []

    if search_selected:
        # Buscar en objetos seleccionados
        for obj in context.selected_objects:
            if is_letter_empty(obj):
                letters.append(obj)
            elif obj.type == EMPTY_TYPE and obj.name.endswith(ROOT_SUFFIX):
                # Buscar en hijos del root empty
                letters.extend(find_letter_children(obj))

    if search_scene and not letters:
        # Buscar en toda la escena
        for obj in context.scene.objects:
            if is_letter_empty(obj):
                letters.append(obj)

    # Ordenar por índice de letra si está disponible
    letters.sort(key=lambda x: x.get("letter_index", 0))

    return letters

def find_letter_children(parent_obj):
    """
    Encuentra empties de letras hijos de un objeto padre.

    Args:
        parent_obj: Objeto padre

    Returns:
        List[bpy.types.Object]: Lista de empties de letras hijos
    """
    letters = []

    if not parent_obj:
        return letters

    for child in parent_obj.children_recursive:
        if is_letter_empty(child):
            letters.append(child)

    # Ordenar por índice de letra
    letters.sort(key=lambda x: x.get("letter_index", 0))

    return letters

def is_letter_empty(obj):
    """
    Verifica si un objeto es un empty de letra válido.

    Args:
        obj: Objeto a verificar

    Returns:
        bool: True si es un empty de letra válido
    """
    return (obj and
            obj.type == EMPTY_TYPE and
            obj.get(LETTER_PROPERTY, False))

def get_letter_mesh(letter_empty):
    """
    Obtiene la malla hija de un empty de letra.

    Args:
        letter_empty: Empty de letra

    Returns:
        bpy.types.Object: Malla hija o None si no se encuentra
    """
    if not letter_empty:
        return None

    for child in letter_empty.children:
        if child.type == MESH_TYPE:
            return child

    return None

def mark_as_letter(obj, root_name=None, letter_index=None):
    """
    Marca un objeto como letra y almacena sus propiedades.

    Args:
        obj: Objeto a marcar
        root_name: Nombre del objeto raíz asociado
        letter_index: Índice de la letra
    """
    if not obj:
        return

    obj[LETTER_PROPERTY] = True

    if root_name:
        obj[ROOT_NAME] = root_name

    if letter_index is not None:
        obj["letter_index"] = letter_index

    # Almacenar transformaciones originales
    store_original_transforms(obj)

    logger.debug(f"Marcado {obj.name} como letra")

def store_original_transforms(obj):
    """
    Almacena las transformaciones originales de un objeto.

    Args:
        obj: Objeto del cual almacenar transformaciones
    """
    if not obj:
        return

    if ORIG_LOCATION not in obj:
        obj[ORIG_LOCATION] = list(obj.location[:])

    if ORIG_ROTATION not in obj:
        obj[ORIG_ROTATION] = list(obj.rotation_euler[:])

    if ORIG_SCALE not in obj:
        obj[ORIG_SCALE] = list(obj.scale[:])

def restore_original_transforms(obj: bpy.types.Object) -> None:
    """
    Restaura las transformaciones originales de un objeto.

    Args:
        obj: Objeto a restaurar
    """
    if not obj:
        return

    if ORIG_LOCATION in obj:
        obj.location = tuple(obj[ORIG_LOCATION])

    if ORIG_ROTATION in obj:
        obj.rotation_euler = tuple(obj[ORIG_ROTATION])

    if ORIG_SCALE in obj:
        obj.scale = tuple(obj[ORIG_SCALE])

def geometry_center(obj):
    verts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    return sum(verts, Vector()) / len(verts) if verts else obj.location

def set_origin_to_center(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

def safe_parent_with_transform(child, parent):
    world_matrix = child.matrix_world.copy()
    child.parent = parent
    if parent:
        child.matrix_parent_inverse = parent.matrix_world.inverted()
    child.matrix_world = world_matrix

def create_nla_strips(action_in, action_mid, action_out, obj):
    """Create three NLA strips on the given object."""
    anim = obj.animation_data_create()
    track = anim.nla_tracks.new()
    track.strips.new(action_in.name, action_in.frame_range[0], action_in)
    track = anim.nla_tracks.new()
    track.strips.new(action_mid.name, action_mid.frame_range[0], action_mid)
    track = anim.nla_tracks.new()
    track.strips.new(action_out.name, action_out.frame_range[0], action_out)

def register():
    logger.debug("Utilidades registradas")

def unregister():
    logger.debug("Utilidades desregistradas")

def setup_letter_constraints(letter: bpy.types.Object) -> None:
    """
    Configura constraints para una letra.

    Args:
        letter: Objeto letra a configurar
    """
    # Buscar malla hija
    mesh_child = None
    for child in letter.children:
        if child.type == MESH_TYPE:
            mesh_child = child
            break

    if not mesh_child:
        return

    # Limpiar constraints existentes
    mesh_child.constraints.clear()

    # A&ntilde;adir constraint Copy Transforms
    copy_transform = mesh_child.constraints.new(type='COPY_TRANSFORMS')
    copy_transform.target = letter
    copy_transform.name = "Follow Letter Empty"

    logger.debug(f"Constraints configurados para {letter.name}")
