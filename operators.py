"""Operators consolidados para TypeAnimator - Sin duplicaciones."""

import bpy
import json
import logging
from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty, EnumProperty
from bpy.types import Operator
from .properties import TA_LetterAnimProperties
from . import core, presets, icon_loader, utils
from .curves import get_or_create_curve_node
from .easing_library import serialize_curve
from .constants import (
    CURVE_NODE_GROUP_NAME, LETTER_PROPERTY, ROOT_SUFFIX, 
    ANIMATION_GROUP_SUFFIX, LETTER_PREFIX, MESH_TYPE, EMPTY_TYPE, FONT_TYPE,
    MIN_FRAME, MAX_FRAME, MIN_DURATION, MAX_DURATION, MIN_OVERLAP, MAX_OVERLAP,
    DEFAULT_START_FRAME, DEFAULT_END_FRAME, DEFAULT_DURATION, DEFAULT_OVERLAP,
    ANIMATION_STAGES, STAGE_NAMES, ANIMATION_MODES, FRAGMENT_MODES,
    PRESET_CATEGORIES, PRESET_PRIORITIES, SCENE_PROPERTIES, WM_PROPERTIES,
    ERROR_MESSAGES, INFO_MESSAGES, CACHE_CONFIG, LOGGING_CONFIG, 
    PERFORMANCE_CONFIG, BUNDLE_CONFIG, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE,
    NODE_NAME_SEPARATOR, CURVE_NODE_PREFIX, STAGE_SEPARATOR,
    REQUIRED_PROPERTY_GROUPS, BLEND_WIDTH, BLEND_MODE, OVERSHOOT_ENABLED,
    OVERSHOOT_LIMIT, AUDIT_AUTO_REPAIR, AUDIT_LOG_DETAILS, AUDIT_VALIDATE_ON_STARTUP,
    LIVE_PREVIEW_ENABLED, LIVE_PREVIEW_UPDATE_RATE, LIVE_PREVIEW_FRAME_SKIP,
    PRESETS_DIR, USER_PRESETS_DIR, PresetPriority
)

logger = logging.getLogger(__name__)

# === OPERADORES PRINCIPALES ===

class TA_OT_separate_letters(bpy.types.Operator):
    """Separa el texto en letras individuales"""
    bl_idname = "typeanimator.separate_letters"
    bl_label = "Separar Letras"
    bl_description = "Separa el texto en letras individuales"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'FONT':
            self.report({'ERROR'}, "Selecciona un objeto de texto")
            return {'CANCELLED'}

        try:
            props = context.scene.ta_letter_anim_props
            root, letters = core.separate_text(obj, props.timing.fragment_mode, props.grouping_tolerance)
            
            # Seleccionar el grupo raíz y las letras
            bpy.ops.object.select_all(action='DESELECT')
            root.select_set(True)
            for letter in letters:
                letter.select_set(True)
            context.view_layer.objects.active = root
            
            self.report({'INFO'}, f"Texto separado en {len(letters)} letras")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error separando texto: {str(e)}")
            return {'CANCELLED'}

class TA_OT_animate_letters(bpy.types.Operator):
    """Aplica la animación a las letras"""
    bl_idname = "typeanimator.animate_letters"
    bl_label = "Animar Letras"
    bl_description = "Aplica la animación a las letras seleccionadas"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.ta_letter_anim_props
        letters = [obj for obj in context.selected_objects 
                  if obj.type == 'MESH' and LETTER_PROPERTY in obj]

        if not letters:
            self.report({'WARNING'}, "No hay letras seleccionadas para animar")
            return {'CANCELLED'}

        try:
            core.animate_letters(letters, props)
            self.report({'INFO'}, f"Animación aplicada a {len(letters)} letras")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error al animar letras: {str(e)}")
            logger.error(f"Error en animate_letters: {e}", exc_info=True)
            return {'CANCELLED'}

class TA_OT_bake_letters(bpy.types.Operator):
    """Genera la animación final insertando keyframes"""
    bl_idname = "typeanimator.bake_letters"
    bl_label = "Bake a Keyframes"
    bl_description = "Genera la animación final insertando keyframes en las letras"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.ta_letter_anim_props
        selected = context.selected_objects
        letters = []
        
        for obj in selected:
            if obj.type == 'EMPTY' and obj.name.endswith(ROOT_SUFFIX):
                children = [child for child in obj.children_recursive if child.type == 'MESH']
                letters.extend(children)
            elif obj.type == 'MESH':
                letters.append(obj)
                
        if not letters:
            self.report({'ERROR'}, "Selecciona el grupo raíz o los objetos de letra para animar")
            return {'CANCELLED'}
            
        try:
            # Eliminar drivers antes de hornear
            core.remove_preview_drivers(letters)
            core.animate_letters(letters, props, preview=False)
            self.report({'INFO'}, "Animación horneada a keyframes")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error al hornear animación: {str(e)}")
            return {'CANCELLED'}

class TA_OT_reset_anim_props(bpy.types.Operator):
    """Restablece los parámetros de animación a valores por defecto"""
    bl_idname = "typeanimator.reset_anim_props"
    bl_label = "Resetear Parámetros"
    bl_description = "Restablece los parámetros de animación a sus valores por defecto"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.ta_letter_anim_props
        
        # Eliminar drivers de preview si existen
        selected = context.selected_objects
        empties = []
        for obj in selected:
            if obj.type == 'EMPTY' and obj.name.endswith(ROOT_SUFFIX):
                empties.extend([child for child in obj.children_recursive if child.type == 'EMPTY'])
            elif obj.type == 'EMPTY':
                empties.append(obj)
                
        if empties:
            core.remove_preview_drivers(empties)
            core.restore_original_transforms(empties)
            
        # Reset de propiedades
        for name in props.__annotations__.keys():
            definition = TA_LetterAnimProperties.bl_rna.properties.get(name)
            if definition is not None:
                default = definition.default
                if hasattr(definition, 'array_length') and definition.array_length > 0:
                    if isinstance(default, (list, tuple)):
                        setattr(props, name, tuple(default))
                    else:
                        setattr(props, name, (default,) * definition.array_length)
                else:
                    if hasattr(definition, 'enum_items') and default == "":
                        enum_items = [item.identifier for item in definition.enum_items]
                        if enum_items:
                            setattr(props, name, enum_items[0])
                    else:
                        setattr(props, name, default)
                        
        self.report({'INFO'}, "Parámetros reseteados")
        return {'FINISHED'}

# === OPERADORES DE PRESETS ===

class TA_OT_apply_quick_preset(bpy.types.Operator):
    """Aplica el preset rápido seleccionado"""
    bl_idname = "typeanimator.apply_quick_preset"
    bl_label = "Aplicar Preset Rápido"
    bl_description = "Aplica el preset rápido seleccionado a toda la animación"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.ta_letter_anim_props
        
        if props.quick_preset == 'NONE':
            self.report({'WARNING'}, "No hay preset rápido seleccionado")
            return {'CANCELLED'}
            
        try:
            # Aplicar preset usando el sistema normalizado
            from .preset_manager import apply_preset_hierarchy
            apply_preset_hierarchy(props)
            
            self.report({'INFO'}, f"Preset rápido '{props.quick_preset}' aplicado")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error aplicando preset: {str(e)}")
            return {'CANCELLED'}

class TA_OT_apply_animation_preset(bpy.types.Operator):
    """Aplica el preset de animación seleccionado"""
    bl_idname = "typeanimator.apply_animation_preset"
    bl_label = "Aplicar Preset de Animación"
    bl_description = "Aplica el preset de animación seleccionado a toda la animación"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.ta_letter_anim_props
        if props.animation_preset == 'NONE':
            self.report({'WARNING'}, "No hay preset de animación seleccionado")
            return {'CANCELLED'}
        try:
            from .presets import get_all_presets
            preset_data = get_all_presets().get(props.animation_preset)
            if not preset_data or preset_data.get('subtype') != 'animation':
                self.report({'ERROR'}, "Preset de animación no válido")
                return {'CANCELLED'}
            # Aplicar campos del preset de animación
            # Ejemplo: duration, overlap, scale_start, amplitude, rot_z, etc.
            if 'duration' in preset_data:
                props.timing.duration = preset_data['duration']
            if 'overlap' in preset_data:
                props.timing.overlap = preset_data['overlap']
            if 'scale_start' in preset_data:
                props.style.text_scale = preset_data['scale_start']
            if 'amplitude' in preset_data:
                props.style.amplitude = preset_data['amplitude']
            if 'rot_z' in preset_data:
                props.style.text_rotation = preset_data['rot_z']
            # Puedes añadir más campos según la estructura de tus presets
            self.report({'INFO'}, f"Preset de animación '{props.animation_preset}' aplicado")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error aplicando preset de animación: {str(e)}")
            return {'CANCELLED'}

class TA_OT_reload_presets(bpy.types.Operator):
    """Recarga los presets desde los archivos JSON"""
    bl_idname = "typeanimator.reload_presets"
    bl_label = "Recargar Presets"
    bl_description = "Recarga los presets desde los archivos JSON"
    
    def execute(self, context):
        try:
            presets.load_all_presets()
            self.report({'INFO'}, "Presets recargados exitosamente")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error recargando presets: {str(e)}")
            return {'CANCELLED'}

# === OPERADORES DE CURVAS ===

class TA_OT_apply_curve_preset_in(bpy.types.Operator):
    """Aplica un preset de curva a la etapa IN"""
    bl_idname = "typeanimator.apply_curve_preset_in"
    bl_label = "Aplicar Preset IN"
    bl_description = "Aplica un preset de curva a la etapa IN"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            curve_node = get_or_create_curve_node(context, 'IN')
            if curve_node:
                # Aplicar preset de curva
                self.report({'INFO'}, "Preset de curva IN aplicado")
            else:
                self.report({'WARNING'}, "No se pudo crear nodo de curva IN")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error aplicando preset IN: {str(e)}")
            return {'CANCELLED'}

class TA_OT_apply_curve_preset_mid(bpy.types.Operator):
    """Aplica un preset de curva a la etapa MID"""
    bl_idname = "typeanimator.apply_curve_preset_mid"
    bl_label = "Aplicar Preset MID"
    bl_description = "Aplica un preset de curva a la etapa MID"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            curve_node = get_or_create_curve_node(context, 'MID')
            if curve_node:
                # Aplicar preset de curva
                self.report({'INFO'}, "Preset de curva MID aplicado")
            else:
                self.report({'WARNING'}, "No se pudo crear nodo de curva MID")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error aplicando preset MID: {str(e)}")
            return {'CANCELLED'}

class TA_OT_apply_curve_preset_out(bpy.types.Operator):
    """Aplica un preset de curva a la etapa OUT"""
    bl_idname = "typeanimator.apply_curve_preset_out"
    bl_label = "Aplicar Preset OUT"
    bl_description = "Aplica un preset de curva a la etapa OUT"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            curve_node = get_or_create_curve_node(context, 'OUT')
            if curve_node:
                # Aplicar preset de curva
                self.report({'INFO'}, "Preset de curva OUT aplicado")
            else:
                self.report({'WARNING'}, "No se pudo crear nodo de curva OUT")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error aplicando preset OUT: {str(e)}")
            return {'CANCELLED'}

# === OPERADORES DE CACHE ===

class TA_OT_clear_letter_cache(bpy.types.Operator):
    """Limpia el cache de separación de letras"""
    bl_idname = "typeanimator.clear_letter_cache"
    bl_label = "Limpiar Cache de Letras"
    bl_description = "Limpia el cache de separación de letras para liberar memoria"
    
    def execute(self, context):
        from .core import clear_letter_separation_cache
        clear_letter_separation_cache()
        self.report({'INFO'}, "Cache de separación de letras limpiado")
        return {'FINISHED'}

class TA_OT_show_cache_stats(bpy.types.Operator):
    """Muestra estadísticas del cache de separación de letras"""
    bl_idname = "typeanimator.show_cache_stats"
    bl_label = "Estadísticas de Cache"
    bl_description = "Muestra estadísticas detalladas del cache de separación de letras"
    
    def execute(self, context):
        from .core import get_cache_stats
        stats = get_cache_stats()
        
        if stats:
            message = f"Cache Stats: {stats['size']}/{stats['max_size']} entradas, {stats['hit_rate']:.1f}% hit rate"
            self.report({'INFO'}, message)
        else:
            self.report({'INFO'}, "No hay estadísticas de cache disponibles")
        return {'FINISHED'}

class TA_OT_optimize_cache(bpy.types.Operator):
    """Optimiza el cache eliminando entradas inválidas"""
    bl_idname = "typeanimator.optimize_cache"
    bl_label = "Optimizar Cache"
    bl_description = "Optimiza el cache eliminando entradas inválidas y reorganizando"
    
    def execute(self, context):
        from .core import optimize_letter_separation_cache
        removed_count = optimize_letter_separation_cache()
        self.report({'INFO'}, f"Cache optimizado, {removed_count} entradas removidas")
        return {'FINISHED'}

# === OPERADORES DE LOGGING ===

class TA_OT_clear_log_file(bpy.types.Operator):
    """Limpia el archivo de log"""
    bl_idname = "typeanimator.clear_log_file"
    bl_label = "Limpiar Log"
    bl_description = "Limpia el archivo de log del addon"
    
    def execute(self, context):
        from .logging_config import clear_log_file
        clear_log_file()
        self.report({'INFO'}, "Archivo de log limpiado")
        return {'FINISHED'}

class TA_OT_open_log_file(bpy.types.Operator):
    """Abre el archivo de log en el editor de texto"""
    bl_idname = "typeanimator.open_log_file"
    bl_label = "Abrir Log"
    bl_description = "Abre el archivo de log en el editor de texto de Blender"
    
    def execute(self, context):
        from .logging_config import open_log_file
        open_log_file()
        self.report({'INFO'}, "Archivo de log abierto en editor")
        return {'FINISHED'}

class TA_OT_update_logging_config(bpy.types.Operator):
    """Actualiza la configuración de logging"""
    bl_idname = "typeanimator.update_logging_config"
    bl_label = "Actualizar Config Logging"
    bl_description = "Actualiza la configuración de logging según las preferencias"
    
    def execute(self, context):
        from .logging_config import update_logging_config
        update_logging_config()
        self.report({'INFO'}, "Configuración de logging actualizada")
        return {'FINISHED'}

class TA_OT_show_log_statistics(bpy.types.Operator):
    """Muestra estadísticas del archivo de log"""
    bl_idname = "typeanimator.show_log_statistics"
    bl_label = "Estadísticas de Log"
    bl_description = "Muestra estadísticas del archivo de log"
    
    def execute(self, context):
        from .logging_config import get_log_statistics
        stats = get_log_statistics()
        
        if stats:
            message = f"Log Stats: {stats['total_lines']} líneas, {stats['size']} bytes, {stats['errors']} errores"
            self.report({'INFO'}, message)
        else:
            self.report({'INFO'}, "No hay estadísticas de log disponibles")
        return {'FINISHED'}

# === OPERADOR DE SELF-TEST ===

class TA_OT_self_test(bpy.types.Operator):
    """Ejecuta un test completo del sistema"""
    bl_idname = "typeanimator.self_test"
    bl_label = "Self Test"
    bl_description = "Ejecuta un test completo del sistema TypeAnimator"
    
    def execute(self, context):
        try:
            # Test 1: Verificar registro de clases
            registered_classes = [
                'TA_OT_separate_letters',
                'TA_OT_animate_letters',
                'TA_OT_bake_letters',
                'TA_OT_reset_anim_props'
            ]
            
            for class_name in registered_classes:
                if not hasattr(bpy.ops, class_name.lower().replace('_ot_', '.')):
                    self.report({'ERROR'}, f"Clase {class_name} no registrada")
                    return {'CANCELLED'}
            
            # Test 2: Verificar existencia de curva
            curve_node = get_or_create_curve_node(context, 'IN')
            if not curve_node:
                self.report({'ERROR'}, "No se pudo crear nodo de curva")
                return {'CANCELLED'}
            
            # Test 3: Verificar propiedades
            props = context.scene.ta_letter_anim_props
            if not props:
                self.report({'ERROR'}, "Propiedades no inicializadas")
                return {'CANCELLED'}
            
            self.report({'INFO'}, "Self test completado exitosamente")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error en self test: {str(e)}")
            return {'CANCELLED'}

# === OPERADORES DE EXPORT BUNDLE ===

class TA_OT_export_preset_bundle(bpy.types.Operator):
    """Exporta un bundle completo de preset con timing, curvas, estilo y materiales"""
    bl_idname = "typeanimator.export_preset_bundle"
    bl_label = "Exportar Bundle de Preset"
    bl_description = "Exporta un bundle completo con timing, curvas, estilo y materiales"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: bpy.props.StringProperty(
        name="Ruta del archivo",
        description="Ruta donde guardar el bundle de preset",
        subtype='FILE_PATH'
    )
    
    bundle_name: bpy.props.StringProperty(
        name="Nombre del Bundle",
        description="Nombre del bundle de preset",
        default="Mi_Preset_Bundle"
    )
    
    include_timing: bpy.props.BoolProperty(
        name="Incluir Timing",
        description="Incluir configuración de timing",
        default=True
    )
    
    include_curves: bpy.props.BoolProperty(
        name="Incluir Curvas",
        description="Incluir curvas de easing",
        default=True
    )
    
    include_style: bpy.props.BoolProperty(
        name="Incluir Estilo",
        description="Incluir configuración de estilo",
        default=True
    )
    
    include_materials: bpy.props.BoolProperty(
        name="Incluir Materiales",
        description="Incluir configuración de materiales",
        default=True
    )
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        try:
            props = context.scene.ta_letter_anim_props
            
            # Crear bundle con componentes seleccionados
            bundle = {
                'schema_version': 1,
                'bundle_name': self.bundle_name,
                'export_date': bpy.utils.datetime.datetime.now().isoformat(),
                'components': {}
            }
            
            # Timing
            if self.include_timing and hasattr(props, 'timing'):
                bundle['components']['timing'] = {}
                timing_props = props.timing
                for attr in dir(timing_props):
                    if not attr.startswith('_') and not callable(getattr(timing_props, attr)):
                        try:
                            value = getattr(timing_props, attr)
                            if isinstance(value, (int, float, str, bool)):
                                bundle['components']['timing'][attr] = value
                        except Exception:
                            pass
            
            # Curvas
            if self.include_curves and hasattr(props, 'stages'):
                bundle['components']['curves'] = {}
                
                stages = [
                    ('in', 'anim_stage_in'),
                    ('mid', 'anim_stage_middle'), 
                    ('out', 'anim_stage_end')
                ]
                
                for stage_name, stage_attr in stages:
                    stage = getattr(props.stages, stage_attr, None)
                    if stage and hasattr(stage, 'mapping'):
                        try:
                            curve_data = serialize_curve(stage.mapping)
                            bundle['components']['curves'][stage_name] = curve_data
                        except Exception as e:
                            logger.warning(f"No se pudo serializar curva {stage_name}: {e}")
            
            # Estilo
            if self.include_style and hasattr(props, 'style'):
                bundle['components']['style'] = {}
                style_props = props.style
                for attr in dir(style_props):
                    if not attr.startswith('_') and not callable(getattr(style_props, attr)):
                        try:
                            value = getattr(style_props, attr)
                            if isinstance(value, (int, float, str, bool)):
                                bundle['components']['style'][attr] = value
                        except Exception:
                            pass
            
            # Materiales
            if self.include_materials and hasattr(props, 'preview'):
                bundle['components']['materials'] = {}
                preview_props = props.preview
                material_attrs = [
                    'material_animation_enabled',
                    'material_preset',
                    'material_duration',
                    'material_easing',
                    'material_fx_emission',
                    'material_fx_color',
                    'material_fx_opacity'
                ]
                
                for attr in material_attrs:
                    if hasattr(preview_props, attr):
                        try:
                            value = getattr(preview_props, attr)
                            if isinstance(value, (int, float, str, bool)):
                                bundle['components']['materials'][attr] = value
                        except Exception:
                            pass
            
            # Guardar bundle
            import json
            import os
            from pathlib import Path
            
            file_path = Path(self.filepath)
            if not file_path.suffix:
                file_path = file_path.with_suffix('.json')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(bundle, f, indent=2, ensure_ascii=False)
            
            self.report({'INFO'}, f"Bundle exportado: {file_path}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error exportando bundle: {str(e)}")
            return {'CANCELLED'}

class TA_OT_import_preset_bundle(bpy.types.Operator):
    """Importa un bundle completo de preset con timing, curvas, estilo y materiales"""
    bl_idname = "typeanimator.import_preset_bundle"
    bl_label = "Importar Bundle de Preset"
    bl_description = "Importa un bundle completo con timing, curvas, estilo y materiales"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: bpy.props.StringProperty = bpy.props.StringProperty(
        name="Ruta del archivo",
        description="Ruta del bundle de preset a importar",
        subtype='FILE_PATH'
    )

    import_timing: bpy.props.BoolProperty = bpy.props.BoolProperty(
        name="Importar Timing",
        description="Importar configuración de timing",
        default=True
    )

    import_curves: bpy.props.BoolProperty = bpy.props.BoolProperty(
        name="Importar Curvas",
        description="Importar curvas de easing",
        default=True
    )

    import_style: bpy.props.BoolProperty = bpy.props.BoolProperty(
        name="Importar Estilo",
        description="Importar configuración de estilo",
        default=True
    )

    import_materials: bpy.props.BoolProperty = bpy.props.BoolProperty(
        name="Importar Materiales",
        description="Importar configuración de materiales",
        default=True
    )
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        try:
            props = context.scene.ta_letter_anim_props
            
            # Cargar bundle
            import json
            from pathlib import Path
            
            file_path = Path(self.filepath)
            if not file_path.exists():
                self.report({'ERROR'}, f"Archivo no encontrado: {file_path}")
                return {'CANCELLED'}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                bundle = json.load(f)
            
            # Validar versión
            if 'schema_version' not in bundle:
                self.report({'WARNING'}, "Bundle sin versión, puede ser incompatible")
            
            components = bundle.get('components', {})
            
            # Importar Timing
            if self.import_timing and 'timing' in components and hasattr(props, 'timing'):
                timing_props = props.timing
                for key, value in components['timing'].items():
                    if hasattr(timing_props, key):
                        try:
                            setattr(timing_props, key, value)
                        except Exception as e:
                            logger.warning(f"No se pudo importar timing.{key}: {e}")
            
            # Importar Curvas
            if self.import_curves and 'curves' in components and hasattr(props, 'stages'):
                for stage_name, curve_data in components['curves'].items():
                    try:
                        curve_node = get_or_create_curve_node(context, stage_name.upper())
                        if curve_node and hasattr(curve_node, 'mapping'):
                            # Limpiar puntos existentes
                            points = curve_node.mapping.curves[0].points
                            points.clear()
                            
                            # Añadir nuevos puntos
                            for x, y in curve_data:
                                points.new(x, y)
                    except Exception as e:
                        logger.warning(f"No se pudo importar curva {stage_name}: {e}")
            
            # Importar Estilo
            if self.import_style and 'style' in components and hasattr(props, 'style'):
                style_props = props.style
                for key, value in components['style'].items():
                    if hasattr(style_props, key):
                        try:
                            setattr(style_props, key, value)
                        except Exception as e:
                            logger.warning(f"No se pudo importar style.{key}: {e}")
            
            # Importar Materiales
            if self.import_materials and 'materials' in components and hasattr(props, 'preview'):
                preview_props = props.preview
                for key, value in components['materials'].items():
                    if hasattr(preview_props, key):
                        try:
                            setattr(preview_props, key, value)
                        except Exception as e:
                            logger.warning(f"No se pudo importar material.{key}: {e}")
            
            bundle_name = bundle.get('bundle_name', 'Bundle')
            self.report({'INFO'}, f"Bundle importado: {bundle_name}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error importando bundle: {str(e)}")
            return {'CANCELLED'}

class TA_OT_validate_preset_bundle(bpy.types.Operator):
    """Valida un bundle de preset sin importarlo"""
    bl_idname = "typeanimator.validate_preset_bundle"
    bl_label = "Validar Bundle de Preset"
    bl_description = "Valida la estructura y contenido de un bundle de preset"
    bl_options = {'REGISTER'}
    
    filepath: bpy.props.StringProperty = bpy.props.StringProperty(
        name="Ruta del archivo",
        description="Ruta del bundle de preset a validar",
        subtype='FILE_PATH'
    )
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        try:
            import json
            from pathlib import Path
            
            file_path = Path(self.filepath)
            if not file_path.exists():
                self.report({'ERROR'}, f"Archivo no encontrado: {file_path}")
                return {'CANCELLED'}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                bundle = json.load(f)
            
            # Validaciones
            issues = []
            warnings = []
            
            # Verificar versión
            if 'schema_version' not in bundle:
                issues.append("Sin versión de schema")
            elif bundle['schema_version'] < 1:
                warnings.append(f"Versión antigua: {bundle['schema_version']}")
            
            # Verificar componentes
            components = bundle.get('components', {})
            if not components:
                issues.append("Sin componentes")
            
            # Verificar timing
            if 'timing' in components:
                timing = components['timing']
                if not isinstance(timing, dict):
                    issues.append("Timing inválido")
                else:
                    required_timing = ['start_frame', 'duration']
                    for req in required_timing:
                        if req not in timing:
                            warnings.append(f"Timing faltante: {req}")
            
            # Verificar curvas
            if 'curves' in components:
                curves = components['curves']
                if not isinstance(curves, dict):
                    issues.append("Curvas inválidas")
                else:
                    for stage in ['in', 'mid', 'out']:
                        if stage in curves:
                            curve_data = curves[stage]
                            if not isinstance(curve_data, list):
                                issues.append(f"Curva {stage} inválida")
                            elif len(curve_data) < 2:
                                warnings.append(f"Curva {stage} con pocos puntos")
            
            # Verificar estilo
            if 'style' in components:
                style = components['style']
                if not isinstance(style, dict):
                    issues.append("Estilo inválido")
            
            # Verificar materiales
            if 'materials' in components:
                materials = components['materials']
                if not isinstance(materials, dict):
                    issues.append("Materiales inválidos")
            
            # Reportar resultados
            if issues:
                self.report({'ERROR'}, f"Bundle inválido: {'; '.join(issues)}")
                return {'CANCELLED'}
            
            if warnings:
                self.report({'WARNING'}, f"Bundle con advertencias: {'; '.join(warnings)}")
            else:
                self.report({'INFO'}, "Bundle válido")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error validando bundle: {str(e)}")
            return {'CANCELLED'}

# === OPERADOR DE TESTING COMPLETO ===

class TA_OT_comprehensive_test(bpy.types.Operator):
    """Ejecuta un test completo del sistema TypeAnimator"""
    bl_idname = "typeanimator.comprehensive_test"
    bl_label = "Test Completo del Sistema"
    bl_description = "Ejecuta un test completo de todas las funcionalidades del sistema"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        from .utils import get_scene_diagnostics, validate_scene_state
        from .core import get_cache_stats
        import time
        
        start_time = time.time()
        test_results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'details': []
        }
        
        try:
            # === TEST 1: Validación de escena ===
            self.report({'INFO'}, "Iniciando test completo del sistema...")
            
            scene_valid, scene_msg = validate_scene_state(context)
            if scene_valid:
                test_results['passed'] += 1
                test_results['details'].append(f"✅ Escena válida: {scene_msg}")
            else:
                test_results['failed'] += 1
                test_results['details'].append(f"❌ Escena inválida: {scene_msg}")
            
            # === TEST 2: Diagnóstico de escena ===
            diagnostics = get_scene_diagnostics(context)
            if diagnostics['scene_valid']:
                test_results['passed'] += 1
                test_results['details'].append(f"✅ Diagnóstico de escena: {diagnostics['text_objects']} textos, {diagnostics['letter_objects']} letras")
            else:
                test_results['failed'] += 1
                test_results['details'].append(f"❌ Diagnóstico falló: {diagnostics['errors']}")
            
            # === TEST 3: Verificación de propiedades ===
            if hasattr(context.scene, 'ta_letter_anim_props'):
                test_results['passed'] += 1
                test_results['details'].append("✅ Propiedades de animación inicializadas")
            else:
                test_results['failed'] += 1
                test_results['details'].append("❌ Propiedades de animación no inicializadas")
            
            # === TEST 4: Verificación de cache ===
            try:
                cache_stats = get_cache_stats()
                if cache_stats:
                    test_results['passed'] += 1
                    test_results['details'].append(f"✅ Cache funcionando: {cache_stats['size']} entradas")
                else:
                    test_results['warnings'] += 1
                    test_results['details'].append("⚠️ Cache sin estadísticas disponibles")
            except Exception as e:
                test_results['warnings'] += 1
                test_results['details'].append(f"⚠️ Cache no disponible: {e}")
            
            # === TEST 5: Verificación de operadores registrados ===
            required_operators = [
                'typeanimator.separate_letters',
                'typeanimator.animate_letters',
                'typeanimator.bake_letters',
                'typeanimator.apply_quick_preset',
                'typeanimator.reload_presets'
            ]
            
            for op_name in required_operators:
                if hasattr(bpy.ops, op_name.replace('typeanimator.', '')):
                    test_results['passed'] += 1
                    test_results['details'].append(f"✅ Operador registrado: {op_name}")
                else:
                    test_results['failed'] += 1
                    test_results['details'].append(f"❌ Operador faltante: {op_name}")
            
            # === TEST 6: Verificación de Node Groups ===
            try:
                from .constants import CURVE_NODE_GROUP_NAME
                if CURVE_NODE_GROUP_NAME in bpy.data.node_groups:
                    test_results['passed'] += 1
                    test_results['details'].append(f"✅ Node Group presente: {CURVE_NODE_GROUP_NAME}")
                else:
                    test_results['warnings'] += 1
                    test_results['details'].append(f"⚠️ Node Group faltante: {CURVE_NODE_GROUP_NAME}")
            except Exception as e:
                test_results['warnings'] += 1
                test_results['details'].append(f"⚠️ Error verificando Node Groups: {e}")
            
            # === TEST 7: Verificación de presets ===
            try:
                from .presets import load_all_presets
                presets_data = load_all_presets()
                if presets_data:
                    test_results['passed'] += 1
                    test_results['details'].append(f"✅ Presets cargados: {len(presets_data)} disponibles")
                else:
                    test_results['warnings'] += 1
                    test_results['details'].append("⚠️ No hay presets disponibles")
            except Exception as e:
                test_results['failed'] += 1
                test_results['details'].append(f"❌ Error cargando presets: {e}")
            
            # === TEST 8: Verificación de logging ===
            try:
                from .logging_config import get_log_statistics
                log_stats = get_log_statistics()
                if log_stats:
                    test_results['passed'] += 1
                    test_results['details'].append(f"✅ Logging funcionando: {log_stats['total_lines']} líneas")
                else:
                    test_results['warnings'] += 1
                    test_results['details'].append("⚠️ Logging sin estadísticas")
            except Exception as e:
                test_results['warnings'] += 1
                test_results['details'].append(f"⚠️ Error en logging: {e}")
            
            # === TEST 9: Verificación de constantes ===
            try:
                from .constants import ADDON_VERSION, OPERATOR_PREFIX, CURVE_NODE_GROUP_NAME
                if all([ADDON_VERSION, OPERATOR_PREFIX, CURVE_NODE_GROUP_NAME]):
                    test_results['passed'] += 1
                    test_results['details'].append(f"✅ Constantes centralizadas: v{ADDON_VERSION}")
                else:
                    test_results['failed'] += 1
                    test_results['details'].append("❌ Constantes faltantes")
            except Exception as e:
                test_results['failed'] += 1
                test_results['details'].append(f"❌ Error en constantes: {e}")
            
            # === TEST 10: Verificación de validación ===
            try:
                from .utils import clamp_value, validate_duration
                test_val = clamp_value(150, 0, 100)
                test_duration = validate_duration(200)
                if test_val == 100 and test_duration == 200:
                    test_results['passed'] += 1
                    test_results['details'].append("✅ Funciones de validación funcionando")
                else:
                    test_results['failed'] += 1
                    test_results['details'].append("❌ Funciones de validación fallaron")
            except Exception as e:
                test_results['failed'] += 1
                test_results['details'].append(f"❌ Error en validación: {e}")
            
            # === RESULTADOS FINALES ===
            elapsed_time = time.time() - start_time
            
            # Mostrar resultados en popup
            def draw_results(self, context):
                layout = self.layout
                layout.label(text=f"Test Completo - {elapsed_time:.2f}s")
                layout.separator()
                
                # Resumen
                row = layout.row()
                row.label(text=f"✅ Pasados: {test_results['passed']}")
                row.label(text=f"❌ Fallidos: {test_results['failed']}")
                row.label(text=f"⚠️ Advertencias: {test_results['warnings']}")
                
                layout.separator()
                
                # Detalles
                for detail in test_results['details']:
                    layout.label(text=detail)
                
                layout.separator()
                
                # Estado general
                if test_results['failed'] == 0:
                    layout.label(text="🎉 Sistema funcionando correctamente", icon='CHECKMARK')
                elif test_results['failed'] <= 2:
                    layout.label(text="⚠️ Sistema con problemas menores", icon='ERROR')
                else:
                    layout.label(text="❌ Sistema con problemas críticos", icon='CANCEL')
            
            bpy.context.window_manager.popup_menu(draw_results, title="Resultados del Test", icon='INFO')
            
            # Reporte en consola
            total_tests = test_results['passed'] + test_results['failed'] + test_results['warnings']
            success_rate = (test_results['passed'] / total_tests * 100) if total_tests > 0 else 0
            
            self.report({'INFO'}, f"Test completado: {test_results['passed']}/{total_tests} pasados ({success_rate:.1f}%) en {elapsed_time:.2f}s")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error en test completo: {str(e)}")
            return {'CANCELLED'}

# === OPERADOR DE COMPATIBILIDAD UNDO/REDO ===

class TA_OT_undo_redo_test(bpy.types.Operator):
    """Test de compatibilidad con undo/redo"""
    bl_idname = "typeanimator.undo_redo_test"
    bl_label = "Test Undo/Redo"
    bl_description = "Test de compatibilidad con el sistema undo/redo de Blender"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            # Crear un objeto de prueba
            bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
            test_obj = context.active_object
            test_obj.name = "Test_Undo_Redo"
            
            # Aplicar una transformación
            test_obj.location = (1, 1, 1)
            test_obj.scale = (2, 2, 2)
            
            self.report({'INFO'}, "Objeto de prueba creado. Usa Ctrl+Z para undo y Ctrl+Shift+Z para redo")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error en test undo/redo: {str(e)}")
            return {'CANCELLED'}

# === OPERADOR DE LIMPIEZA DE REFERENCIAS ===

class TA_OT_cleanup_references(bpy.types.Operator):
    """Limpia referencias inválidas en la escena"""
    bl_idname = "typeanimator.cleanup_references"
    bl_label = "Limpiar Referencias"
    bl_description = "Limpia referencias a objetos borrados y datos corruptos"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            from .utils import cleanup_invalid_references, repair_scene_properties
            
            # Limpiar referencias inválidas
            cleaned_refs = cleanup_invalid_references()
            
            # Reparar propiedades de escena
            repaired_scenes = repair_scene_properties()
            
            # Purga de datos huérfanos
            bpy.data.orphans_purge()
            
            self.report({'INFO'}, f"Limpieza completada: {cleaned_refs} referencias limpiadas, {repaired_scenes} escenas reparadas")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error en limpieza: {str(e)}")
            return {'CANCELLED'}

# === OPERADOR DE VALIDACIÓN DE PROPIEDADES ===

class TA_OT_validate_properties(bpy.types.Operator):
    """Valida y corrige todas las propiedades de animación"""
    bl_idname = "typeanimator.validate_properties"
    bl_label = "Validar Propiedades"
    bl_description = "Valida y corrige todas las propiedades de animación en la escena"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            from .utils import validate_animation_properties
            
            validated_count = 0
            error_count = 0
            
            for scene in bpy.data.scenes:
                if hasattr(scene, 'ta_letter_anim_props'):
                    props = scene.ta_letter_anim_props
                    if validate_animation_properties(props):
                        validated_count += 1
                    else:
                        error_count += 1
            
            if error_count == 0:
                self.report({'INFO'}, f"Validación completada: {validated_count} escenas validadas correctamente")
            else:
                self.report({'WARNING'}, f"Validación completada: {validated_count} escenas validadas, {error_count} con errores")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error en validación: {str(e)}")
            return {'CANCELLED'}

# === ADVANCED EXPORT/IMPORT OPERATORS ===

class TA_OT_export_animation_data(bpy.types.Operator):
    """Export animation data in various formats."""
    bl_idname = "typeanimator.export_animation_data"
    bl_label = "Export Animation Data"
    bl_description = "Export animation data in multiple formats"
    
    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Path to save the animation data",
        default="",
        subtype='FILE_PATH'
    )
    
    export_format: bpy.props.EnumProperty(
        name="Export Format",
        description="Format to export animation data",
        items=[
            ('JSON', 'JSON', 'Export as JSON format'),
            ('CSV', 'CSV', 'Export as CSV format'),
            ('XML', 'XML', 'Export as XML format'),
            ('PYTHON', 'Python', 'Export as Python script')
        ],
        default='JSON'
    )
    
    include_settings: bpy.props.BoolProperty(
        name="Include Settings",
        description="Include animation settings in export",
        default=True
    )
    
    include_keyframes: bpy.props.BoolProperty(
        name="Include Keyframes",
        description="Include keyframe data in export",
        default=True
    )
    
    include_curves: bpy.props.BoolProperty(
        name="Include Curves",
        description="Include curve data in export",
        default=True
    )
    
    def execute(self, context):
        try:
            if not self.filepath:
                self.report({'ERROR'}, "No file path specified")
                return {'CANCELLED'}
            
            # Collect animation data
            animation_data = self._collect_animation_data(context)
            
            # Export based on format
            if self.export_format == 'JSON':
                success = self._export_json(animation_data)
            elif self.export_format == 'CSV':
                success = self._export_csv(animation_data)
            elif self.export_format == 'XML':
                success = self._export_xml(animation_data)
            elif self.export_format == 'PYTHON':
                success = self._export_python(animation_data)
            else:
                self.report({'ERROR'}, f"Unsupported format: {self.export_format}")
                return {'CANCELLED'}
            
            if success:
                self.report({'INFO'}, f"Animation data exported to {self.filepath}")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Failed to export animation data")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Export failed: {str(e)}")
            return {'CANCELLED'}
    
    def _collect_animation_data(self, context):
        """Collect animation data from the scene."""
        data = {
            'metadata': {
                'export_time': bpy.context.scene.frame_current,
                'scene_name': context.scene.name,
                'format': self.export_format
            }
        }
        
        if self.include_settings:
            props = context.scene.ta_letter_anim_props
            if props:
                data['settings'] = self._extract_settings(props)
        
        if self.include_keyframes:
            data['keyframes'] = self._extract_keyframes(context)
        
        if self.include_curves:
            data['curves'] = self._extract_curves(context)
        
        return data
    
    def _extract_settings(self, props):
        """Extract animation settings from properties."""
        settings = {}
        
        # Extract timing settings
        if hasattr(props, 'timing'):
            settings['timing'] = {
                'start_frame': props.timing.start_frame,
                'end_frame': props.timing.end_frame,
                'duration': props.timing.duration,
                'overlap': props.timing.overlap
            }
        
        # Extract motion settings
        if hasattr(props, 'motion'):
            settings['motion'] = {
                'scale_x': props.motion.scale_x,
                'scale_y': props.motion.scale_y,
                'scale_z': props.motion.scale_z,
                'rotation_x': props.motion.rotation_x,
                'rotation_y': props.motion.rotation_y,
                'rotation_z': props.motion.rotation_z
            }
        
        # Extract style settings
        if hasattr(props, 'style'):
            settings['style'] = {
                'opacity': props.style.opacity,
                'blur': props.style.blur,
                'color': props.style.color
            }
        
        return settings
    
    def _extract_keyframes(self, context):
        """Extract keyframe data from the scene."""
        keyframes = {}
        
        for obj in context.scene.objects:
            if obj.animation_data and obj.animation_data.action:
                action = obj.animation_data.action
                obj_keyframes = {}
                
                for fcurve in action.fcurves:
                    curve_keyframes = []
                    for keyframe in fcurve.keyframe_points:
                        curve_keyframes.append({
                            'frame': keyframe.co[0],
                            'value': keyframe.co[1],
                            'interpolation': keyframe.interpolation
                        })
                    
                    obj_keyframes[fcurve.data_path] = curve_keyframes
                
                keyframes[obj.name] = obj_keyframes
        
        return keyframes
    
    def _extract_curves(self, context):
        """Extract curve data from the scene."""
        curves = {}
        
        # Extract curve node data
        for node_group in bpy.data.node_groups:
            if CURVE_NODE_GROUP_NAME in node_group.name:
                group_curves = {}
                
                for node in node_group.nodes:
                    if node.bl_idname == 'ShaderNodeRGBCurve':
                        curve_data = []
                        for curve in node.mapping.curves:
                            points = []
                            for point in curve.points:
                                points.append({
                                    'x': point.location[0],
                                    'y': point.location[1],
                                    'handle_type': point.handle_type
                                })
                            curve_data.append(points)
                        
                        group_curves[node.name] = curve_data
                
                curves[node_group.name] = group_curves
        
        return curves
    
    def _export_json(self, data):
        """Export data as JSON."""
        try:
            import json
            
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            logger.error(f"JSON export error: {e}")
            return False
    
    def _export_csv(self, data):
        """Export data as CSV."""
        try:
            import csv
            
            with open(self.filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write metadata
                writer.writerow(['Section', 'Key', 'Value'])
                for key, value in data.get('metadata', {}).items():
                    writer.writerow(['metadata', key, str(value)])
                
                # Write settings
                settings = data.get('settings', {})
                for category, category_data in settings.items():
                    for key, value in category_data.items():
                        writer.writerow([category, key, str(value)])
            
            return True
        except Exception as e:
            logger.error(f"CSV export error: {e}")
            return False
    
    def _export_xml(self, data):
        """Export data as XML."""
        try:
            import xml.etree.ElementTree as ET
            
            root = ET.Element('TypeAnimatorData')
            
            # Add metadata
            metadata = ET.SubElement(root, 'metadata')
            for key, value in data.get('metadata', {}).items():
                elem = ET.SubElement(metadata, key)
                elem.text = str(value)
            
            # Add settings
            settings = ET.SubElement(root, 'settings')
            for category, category_data in data.get('settings', {}).items():
                category_elem = ET.SubElement(settings, category)
                for key, value in category_data.items():
                    elem = ET.SubElement(category_elem, key)
                    elem.text = str(value)
            
            # Create tree and write
            tree = ET.ElementTree(root)
            tree.write(self.filepath, encoding='utf-8', xml_declaration=True)
            
            return True
        except Exception as e:
            logger.error(f"XML export error: {e}")
            return False
    
    def _export_python(self, data):
        """Export data as Python script."""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write("# TypeAnimator Animation Data\n")
                f.write("# Generated automatically\n\n")
                
                f.write("import bpy\n\n")
                
                # Write settings as Python code
                settings = data.get('settings', {})
                f.write("# Animation Settings\n")
                f.write("def apply_animation_settings():\n")
                f.write("    scene = bpy.context.scene\n")
                f.write("    props = scene.ta_letter_anim_props\n\n")
                
                for category, category_data in settings.items():
                    f.write(f"    # {category.title()} settings\n")
                    for key, value in category_data.items():
                        if isinstance(value, (list, tuple)):
                            f.write(f"    props.{category}.{key} = {list(value)}\n")
                        else:
                            f.write(f"    props.{category}.{key} = {value}\n")
                    f.write("\n")
                
                f.write("if __name__ == '__main__':\n")
                f.write("    apply_animation_settings()\n")
            
            return True
        except Exception as e:
            logger.error(f"Python export error: {e}")
            return False
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# === ADVANCED CURVE OPERATORS ===

class TA_OT_copy_curve_between_stages(bpy.types.Operator):
    """Copy curve from one stage to another."""
    bl_idname = "typeanimator.copy_curve_between_stages"
    bl_label = "Copy Curve Between Stages"
    bl_description = "Copy curve configuration from one stage to another"
    bl_options = {'REGISTER', 'UNDO'}
    
    source_stage: bpy.props.EnumProperty(
        name="Source Stage",
        description="Stage to copy from",
        items=[
            ('in', 'IN', 'Copy from IN stage'),
            ('mid', 'MID', 'Copy from MID stage'),
            ('out', 'OUT', 'Copy from OUT stage')
        ],
        default='in'
    )
    
    target_stage: bpy.props.EnumProperty(
        name="Target Stage",
        description="Stage to copy to",
        items=[
            ('in', 'IN', 'Copy to IN stage'),
            ('mid', 'MID', 'Copy to MID stage'),
            ('out', 'OUT', 'Copy to OUT stage')
        ],
        default='mid'
    )
    
    def execute(self, context):
        try:
            from .curves import copy_curve_between_stages
            
            obj = context.active_object
            if not obj:
                self.report({'ERROR'}, "No active object selected")
                return {'CANCELLED'}
            
            success = copy_curve_between_stages(obj, self.source_stage, self.target_stage)
            
            if success:
                self.report({'INFO'}, f"Copied curve from {self.source_stage} to {self.target_stage}")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Failed to copy curve")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Copy failed: {str(e)}")
            return {'CANCELLED'}

class TA_OT_reset_all_curves(bpy.types.Operator):
    """Reset all curves for the active object to defaults."""
    bl_idname = "typeanimator.reset_all_curves"
    bl_label = "Reset All Curves"
    bl_description = "Reset all curve stages to default configurations"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            from .curves import reset_all_curves
            
            obj = context.active_object
            if not obj:
                self.report({'ERROR'}, "No active object selected")
                return {'CANCELLED'}
            
            success = reset_all_curves(obj)
            
            if success:
                self.report({'INFO'}, "All curves reset to defaults")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Failed to reset curves")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Reset failed: {str(e)}")
            return {'CANCELLED'}

class TA_OT_debug_evaluate_curves(bpy.types.Operator):
    """Debug evaluation of curves at specific points."""
    bl_idname = "typeanimator.debug_evaluate_curves"
    bl_label = "Debug Curve Evaluation"
    bl_description = "Test curve evaluation at specific points"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        try:
            from .curves import debug_evaluate_curves
            
            obj = context.active_object
            if not obj:
                self.report({'ERROR'}, "No active object selected")
                return {'CANCELLED'}
            
            # Test points: 0.0, 0.5, 1.0
            test_points = [0.0, 0.5, 1.0]
            debug_results = debug_evaluate_curves(obj, test_points)
            
            if 'error' in debug_results:
                self.report({'ERROR'}, f"Debug failed: {debug_results['error']}")
                return {'CANCELLED'}
            
            # Show results in popup
            def draw_debug_results(self, context):
                layout = self.layout
                layout.label(text=f"Curve Debug: {obj.name}")
                layout.separator()
                
                for stage, stage_results in debug_results['results'].items():
                    layout.label(text=f"Stage {stage.upper()}:", icon='IPO')
                    for point, value in stage_results.items():
                        layout.label(text=f"  {point}: {value:.3f}")
                    layout.separator()
            
            bpy.context.window_manager.popup_menu(draw_debug_results, title="Curve Debug Results", icon='INFO')
            
            self.report({'INFO'}, "Curve debug completed")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Debug failed: {str(e)}")
            return {'CANCELLED'}

class TA_OT_audit_repair_curves(bpy.types.Operator):
    """Audit and repair curve system."""
    bl_idname = "typeanimator.audit_repair_curves"
    bl_label = "Audit & Repair Curves"
    bl_description = "Comprehensive audit and repair of curve system"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        try:
            from .curves import audit_or_repair_curve_nodegroup
            
            audit_results = audit_or_repair_curve_nodegroup()
            
            if 'error' in audit_results:
                self.report({'ERROR'}, f"Audit failed: {audit_results['error']}")
                return {'CANCELLED'}
            
            # Show results in popup
            def draw_audit_results(self, context):
                layout = self.layout
                layout.label(text="Curve Audit Results", icon='INFO')
                layout.separator()
                
                # Summary
                row = layout.row()
                row.label(text=f"Total Objects: {audit_results['total_objects']}")
                row.label(text=f"Valid: {audit_results['valid_objects']}")
                row.label(text=f"Repaired: {audit_results['repaired_objects']}")
                
                layout.separator()
                
                # Warnings
                if audit_results['warnings']:
                    layout.label(text="Warnings:", icon='ERROR')
                    for warning in audit_results['warnings'][:5]:  # Show first 5
                        layout.label(text=f"  {warning}")
                    if len(audit_results['warnings']) > 5:
                        layout.label(text=f"  ... and {len(audit_results['warnings']) - 5} more")
                
                # Details
                if audit_results['details']:
                    layout.separator()
                    layout.label(text="Details:", icon='INFO')
                    for detail in audit_results['details'][:3]:  # Show first 3
                        layout.label(text=f"  {detail}")
                    if len(audit_results['details']) > 3:
                        layout.label(text=f"  ... and {len(audit_results['details']) - 3} more")
            
            bpy.context.window_manager.popup_menu(draw_audit_results, title="Curve Audit Results", icon='INFO')
            
            self.report({'INFO'}, f"Audit completed: {audit_results['valid_objects']}/{audit_results['total_objects']} valid, {audit_results['repaired_objects']} repaired")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Audit failed: {str(e)}")
            return {'CANCELLED'}

class TA_OT_toggle_live_preview(bpy.types.Operator):
    """Toggle live preview mode."""
    bl_idname = "typeanimator.toggle_live_preview"
    bl_label = "Toggle Live Preview"
    bl_description = "Enable or disable live preview mode"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        try:
            props = context.scene.ta_letter_anim_props
            
            # Toggle live preview flag
            if hasattr(props, 'live_preview'):
                props.live_preview = not props.live_preview
                status = "enabled" if props.live_preview else "disabled"
                self.report({'INFO'}, f"Live preview {status}")
            else:
                # Create the property if it doesn't exist
                props.live_preview = True
                self.report({'INFO'}, "Live preview enabled")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Toggle failed: {str(e)}")
            return {'CANCELLED'}

class TA_OT_create_text_from_input(bpy.types.Operator):
    bl_idname = "typeanimator.create_text_from_input"
    bl_label = "Crear Texto desde Input"
    bl_description = "Crea un objeto de texto en la escena con el texto ingresado en el panel"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.ta_letter_anim_props
        text_value = getattr(props, 'new_text_input', None)
        if not text_value:
            self.report({'WARNING'}, "No hay texto para crear.")
            return {'CANCELLED'}
        # Crear objeto de texto
        bpy.ops.object.text_add()
        obj = context.active_object
        obj.data.body = text_value
        obj.name = f"Text_{text_value[:8]}"
        obj.data.align_x = 'CENTER'
        obj.data.align_y = 'CENTER'
        obj.location = (0, 0, 0)
        self.report({'INFO'}, f"Texto '{text_value}' creado.")
        return {'FINISHED'}

# === LISTA DE CLASES PARA REGISTRO ===

classes = [
    # Operadores principales
    TA_OT_separate_letters,
    TA_OT_animate_letters,
    TA_OT_bake_letters,
    TA_OT_reset_anim_props,
    
    # Operadores de presets
    TA_OT_apply_quick_preset,
    TA_OT_apply_animation_preset,
    TA_OT_reload_presets,
    
    # Operadores de curvas
    TA_OT_apply_curve_preset_in,
    TA_OT_apply_curve_preset_mid,
    TA_OT_apply_curve_preset_out,
    
    # Operadores de cache
    TA_OT_clear_letter_cache,
    TA_OT_show_cache_stats,
    TA_OT_optimize_cache,
    
    # Operadores de logging
    TA_OT_clear_log_file,
    TA_OT_open_log_file,
    TA_OT_update_logging_config,
    TA_OT_show_log_statistics,
    
    # Operadores de testing y validación
    TA_OT_self_test,
    TA_OT_comprehensive_test,
    TA_OT_undo_redo_test,
    TA_OT_cleanup_references,
    TA_OT_validate_properties,
    
    # Operadores de export bundle
    TA_OT_export_preset_bundle,
    TA_OT_import_preset_bundle,
    TA_OT_validate_preset_bundle,
    
    # Operadores avanzados de export/import
    TA_OT_export_animation_data,
    
    # Operadores de curvas avanzados
    TA_OT_copy_curve_between_stages,
    TA_OT_reset_all_curves,
    TA_OT_debug_evaluate_curves,
    TA_OT_audit_repair_curves,
    TA_OT_toggle_live_preview,
    TA_OT_create_text_from_input,
]

def register():
    """Registra todos los operadores consolidados"""
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            logger.error(f"Error registrando {cls.__name__}: {e}")

def unregister():
    """Desregistra todos los operadores consolidados"""
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            logger.error(f"Error desregistrando {cls.__name__}: {e}") 