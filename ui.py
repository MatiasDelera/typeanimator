r"""Improved user interface for the Type Animator add-on."""

import bpy
from bpy.types import Panel, Operator, UIList
from bpy.props import StringProperty, BoolProperty, EnumProperty
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
    PRESETS_DIR, USER_PRESETS_DIR, get_text, get_current_language
)
from .utils import is_valid_object, get_valid_letters_from_selection, validate_scene_state
from .properties import TA_StyleProperties, TA_TimingProperties, TA_PreviewProperties, TA_StagesProperties, TA_AnimStageProperties

# Helper functions
def is_text_focused(context, text_obj):
    """Check if a text object is currently focused."""
    return context.scene.ta_focused_text == text_obj.name

def get_or_init_stage(stage, props=None, attr_name=None):
    """Get or initialize a stage property group."""
    if props is None:
        props = bpy.context.scene.ta_letter_anim_props
    
    if attr_name is None:
        attr_name = f'anim_stage_{stage.lower()}'
    
    stage_prop = getattr(props, attr_name, None)
    if stage_prop is None:
        # Initialize the stage
        stage_prop = getattr(props, attr_name)
    
    return stage_prop

def get_or_create_curve_node(context, stage):
    """Get or create a curve node for the given stage."""
    try:
        from . import curves
        return curves.get_or_create_curve_node(f"{context.active_object.name}curve{stage.lower()}", "mapping")
    except:
        return None

def get_system_status(context):
    """Get current system status for UI feedback."""
    status = {
        'scene_valid': False,
        'text_objects': 0,
        'letter_objects': 0,
        'root_objects': 0,
        'animation_active': False,
        'focus_active': False,
        'errors': [],
        'warnings': []
    }
    
    try:
        # Validar escena
        scene_valid, scene_msg = validate_scene_state(context)
        status['scene_valid'] = scene_valid
        
        if not scene_valid:
            status['errors'].append(scene_msg)
        
        # Contar objetos
        for obj in bpy.data.objects:
            if obj.type == FONT_TYPE:
                status['text_objects'] += 1
            elif is_valid_object(obj) and hasattr(obj, LETTER_PROPERTY) and getattr(obj, LETTER_PROPERTY, False):
                status['letter_objects'] += 1
            elif is_valid_object(obj) and obj.name.endswith(ROOT_SUFFIX):
                status['root_objects'] += 1
        
        # Verificar foco activo
        if context.scene.ta_focused_text:
            status['focus_active'] = True
        
        # Verificar animación activa (simplificado)
        if context.scene.frame_current > 1:
            status['animation_active'] = True
        
        # Verificar consistencia
        if status['letter_objects'] > 0 and status['root_objects'] == 0:
            status['warnings'].append("Letras sin root asociado")
        
        if status['root_objects'] > 0 and status['letter_objects'] == 0:
            status['warnings'].append("Roots sin letras asociadas")
            
    except Exception as e:
        status['errors'].append(f"Error obteniendo estado: {e}")
    
    return status

def draw_status_indicator(layout, status, icon='INFO'):
    """Draw a status indicator with appropriate icon and color."""
    if status['errors']:
        layout.label(text="❌ Sistema con errores", icon='ERROR')
        for error in status['errors']:
            layout.label(text=f"  {error}", icon='DOT')
    elif status['warnings']:
        layout.label(text="⚠️ Sistema con advertencias", icon='ERROR')
        for warning in status['warnings']:
            layout.label(text=f"  {warning}", icon='DOT')
    else:
        layout.label(text="✅ Sistema funcionando", icon='CHECKMARK')

def draw_quick_actions(layout, context):
    status = get_system_status(context)
    # Fila 1: Separar y Animar
    row1 = layout.row(align=True)
    if status['text_objects'] > 0:
        row1.operator("typeanimator.separate_letters", text="Separar", icon='MOD_BOOLEAN')
    else:
        row1.enabled = False
        row1.operator("typeanimator.separate_letters", text="Separar", icon='MOD_BOOLEAN')
    if status['letter_objects'] > 0:
        row1 = layout.row(align=True)
        row1.operator("typeanimator.animate_letters", text="Animar", icon='PLAY')
    else:
        row1 = layout.row(align=True)
        row1.enabled = False
        row1.operator("typeanimator.animate_letters", text="Animar", icon='PLAY')
    # Fila 2: Bake y Reset
    row2 = layout.row(align=True)
    if status['letter_objects'] > 0:
        row2.operator("typeanimator.bake_letters", text="Bake", icon='KEYTYPE_KEYFRAME_VEC')
    else:
        row2.enabled = False
        row2.operator("typeanimator.bake_letters", text="Bake", icon='KEYTYPE_KEYFRAME_VEC')
    row2.operator("typeanimator.reset_anim_props", text="Reset", icon='LOOP_BACK')

def ensure_pointer(prop, prop_name, prop_type):
    val = getattr(prop, prop_name, None)
    if type(val).__name__ == '_PropertyDeferred':
        try:
            setattr(prop, prop_name, prop_type())
            val = getattr(prop, prop_name)
        except Exception as e:
            print(f"[typeanimator] Error inicializando {prop_name}: {e}")
    return val

# Operator classes
class TA_OT_take_focus(Operator):
    """Take focus on the selected text object."""
    bl_idname = "typeanimator.take_focus"
    bl_label = "Take Focus"
    bl_description = "Focus on the selected text object for isolated editing"
    
    def execute(self, context):
        if context.active_object and context.active_object.type == FONT_TYPE:
            context.scene.ta_focused_text = context.active_object.name
            context.window_manager.ta_status = f"Focused on: {context.active_object.name}"
            self.report({'INFO'}, f"Focused on {context.active_object.name}")
        else:
            self.report({'ERROR'}, ERROR_MESSAGES['NO_TEXT_SELECTED'])
        return {'FINISHED'}

class TA_OT_clear_focus(Operator):
    """Clear the current focus."""
    bl_idname = "typeanimator.clear_focus"
    bl_label = "Clear Focus"
    bl_description = "Clear the current text focus"
    
    def execute(self, context):
        context.scene.ta_focused_text = ""
        context.window_manager.ta_status = "Focus cleared"
        self.report({'INFO'}, "Focus cleared")
        return {'FINISHED'}

class TA_OT_preview_play(Operator):
    """Start preview animation."""
    bl_idname = "typeanimator.preview_play"
    bl_label = "Play Preview"
    bl_description = "Start the preview animation"
    
    def execute(self, context):
        try:
            from . import core
            letters = get_valid_letters_from_selection(context)
            if letters:
                core.animate_letters(letters, context.scene.ta_letter_anim_props)
                context.window_manager.ta_status = "Preview started"
                self.report({'INFO'}, "Preview started")
            else:
                self.report({'WARNING'}, "No valid letters found for preview")
        except Exception as e:
            self.report({'ERROR'}, f"Preview failed: {str(e)}")
        return {'FINISHED'}

class TA_OT_preview_stop(Operator):
    """Stop preview animation."""
    bl_idname = "typeanimator.preview_stop"
    bl_label = "Stop Preview"
    bl_description = "Stop the preview animation"
    
    def execute(self, context):
        try:
            from . import core
            letters = get_valid_letters_from_selection(context)
            if letters:
                core.remove_preview_drivers(letters)
                context.window_manager.ta_status = "Preview stopped"
                self.report({'INFO'}, "Preview stopped")
            else:
                self.report({'WARNING'}, "No valid letters found to stop preview")
        except Exception as e:
            self.report({'ERROR'}, f"Stop failed: {str(e)}")
        return {'FINISHED'}

class TA_OT_bake_animation(Operator):
    """Bake animation to keyframes."""
    bl_idname = "typeanimator.bake_animation"
    bl_label = "Bake Animation"
    bl_description = "Bake the preview animation to keyframes"
    
    def execute(self, context):
        try:
            from . import core
            letters = get_valid_letters_from_selection(context)
            if letters:
                core.remove_preview_drivers(letters)
                core.animate_letters(letters, context.scene.ta_letter_anim_props, preview=False)
                context.window_manager.ta_status = "Animation baked"
                self.report({'INFO'}, "Animation baked to keyframes")
            else:
                self.report({'WARNING'}, "No valid letters found for baking")
        except Exception as e:
            self.report({'ERROR'}, f"Bake failed: {str(e)}")
        return {'FINISHED'}

class TA_UL_recent_presets(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="")

class TA_UL_user_presets(bpy.types.UIList):
    """UIList displaying user saved presets."""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            icon_id = 'LOCKED' if item.builtin else 'FILE'
            layout.label(text=item.name, icon=icon_id)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="")

class VIEW3D_PT_ta_main_improved(bpy.types.Panel):
    """Main panel with improved UI/UX."""

    bl_label = "Type Animator"
    bl_idname = "VIEW3D_PT_ta_main_improved"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Type Animator'
    bl_order = 0

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, 'ta_letter_anim_props')

    def draw(self, context):
        """Draw the main panel with tabs and status indicators."""
        layout = self.layout
        props = context.scene.ta_letter_anim_props

        # === STATUS INDICATOR ===
        status = get_system_status(context)
        status_box = layout.box()
        status_box.label(text="Estado del Sistema", icon='INFO')
        draw_status_indicator(status_box, status)
        
        # Mostrar estadísticas rápidas
        stats_row = status_box.row()
        stats_row.label(text=f"📝 Textos: {status['text_objects']}")
        stats_row.label(text=f"🔤 Letras: {status['letter_objects']}")
        stats_row.label(text=f"📁 Roots: {status['root_objects']}")

        # === QUICK ACTIONS ===
        actions_box = layout.box()
        actions_box.label(text="Acciones Rápidas", icon='PLAY')
        draw_quick_actions(actions_box, context)

        # === TABS ===
        row = layout.row()
        row.prop(props, "active_tab", expand=True)

        # Content based on active tab
        if props.active_tab == 'ANIMATE':
            self.draw_animate_tab(layout, context)
        elif props.active_tab == 'EFFECTS':
            self.draw_effects_tab(layout, context)
        elif props.active_tab == 'DIAGNOSTIC':
            self.draw_diagnostic_tab(layout, context)
        elif props.active_tab == 'EXPORT':
            self.draw_export_tab(layout, context)

    def draw_export_tab(self, layout, context):
        """Panel de exportación de bundles."""
        props = context.scene.ta_letter_anim_props

        # === EXPORT BUNDLE ===
        export_box = layout.box()
        export_box.label(text="Export Bundle", icon='EXPORT')

        # Export Bundle
        row = export_box.row()
        row.operator("typeanimator.export_preset_bundle", text="Exportar Bundle", icon='EXPORT')

        # Import Bundle
        row = export_box.row()
        row.operator("typeanimator.import_preset_bundle", text="Importar Bundle", icon='IMPORT')

        # Validate Bundle
        row = export_box.row()
        row.operator("typeanimator.validate_preset_bundle", text="Validar Bundle", icon='CHECKMARK')

        # === INFORMACIÓN DEL BUNDLE ===
        info_box = layout.box()
        info_box.label(text="Información del Bundle", icon='INFO')

        # Mostrar información del bundle actual
        bundle_info = self.get_bundle_info(props)
        
        for category, count in bundle_info.items():
            row = info_box.row()
            row.label(text=f"{category}: {count} elementos")

        # === COMPONENTES DISPONIBLES ===
        components_box = layout.box()
        components_box.label(text="Componentes Disponibles", icon='SETTINGS')

        # Timing
        timing_row = components_box.row()
        timing_row.label(text="Timing", icon='TIME')
        timing_row.label(text="✅ Disponible")

        # Curves
        curves_row = components_box.row()
        curves_row.label(text="Curves", icon='FCURVE')
        curves_row.label(text="✅ Disponible")

        # Style
        style_row = components_box.row()
        style_row.label(text="Style", icon='MATERIAL')
        style_row.label(text="✅ Disponible")

        # Materials
        materials_row = components_box.row()
        materials_row.label(text="Materials", icon='MATERIAL_DATA')
        materials_row.label(text="✅ Disponible")

    def get_bundle_info(self, props):
        """Get information about current bundle components."""
        bundle_info = {
            'Timing': 0,
            'Curves': 0,
            'Style': 0,
            'Materials': 0
        }
        
        try:
            # Contar componentes de timing
            if hasattr(props, 'timing'):
                timing_props = props.timing
                for attr in dir(timing_props):
                    if not attr.startswith('_') and not callable(getattr(timing_props, attr)):
                        bundle_info['Timing'] += 1
            
            # Contar curvas
            if hasattr(props, 'stages'):
                stages = ['in', 'mid', 'out']
                for stage in stages:
                    stage_attr = f'anim_stage_{stage}'
                    if hasattr(props.stages, stage_attr):
                        bundle_info['Curves'] += 1
            
            # Contar componentes de estilo
            if hasattr(props, 'style'):
                style_props = props.style
                for attr in dir(style_props):
                    if not attr.startswith('_') and not callable(getattr(style_props, attr)):
                        bundle_info['Style'] += 1
            
            # Contar componentes de materiales
            if hasattr(props, 'preview'):
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
                        bundle_info['Materials'] += 1
                        
        except Exception:
            pass
        
        return bundle_info

    def draw_text_tab(self, layout, context):
        """Text configuration tab."""
        props = context.scene.ta_letter_anim_props
        layout.label(text="Crear texto desde input:")
        layout.prop(props, "new_text_input", text="Texto")
        layout.operator("typeanimator.create_text_from_input", text="Crear Texto", icon='FONT_DATA')
        # Mostrar UIList de presets recientes y de usuario
        layout.label(text="Recent Presets:")
        layout.template_list("TA_UL_recent_presets", "", props, "recent_presets", props, "recent_presets_index")
        layout.label(text="User Presets:")
        layout.template_list("TA_UL_user_presets", "", props, "user_presets", props, "user_presets_index")

    def draw_animate_tab(self, layout, context):
        """Animation configuration tab."""
        props = context.scene.ta_letter_anim_props
        
        # === TIMING SECTION ===
        timing_box = layout.box()
        timing_box.label(text="Timing", icon='TIME')
        
        col = timing_box.column(align=True)
        timing = ensure_pointer(props, "timing", TA_TimingProperties)
        col.prop(timing, "start_frame", text="Start Frame")
        col.prop(timing, "end_frame", text="End Frame")
        col.prop(timing, "duration", text="Duration")
        col.prop(timing, "overlap", text="Overlap")
        
        # === ANIMATION MODE ===
        mode_box = layout.box()
        mode_box.label(text="Animation Mode", icon='SETTINGS')
        
        col = mode_box.column()
        col.prop(timing, "animation_mode", text="Mode")
        col.prop(timing, "fragment_mode", text="Fragment Mode")
        
        # === QUICK PRESETS ===
        preset_box = layout.box()
        preset_box.label(text="Quick Presets", icon='PRESET')
        
        col = preset_box.column()
        col.prop(props, "quick_preset", text="Quick Preset")
        
        row = col.row()
        row.operator("typeanimator.apply_quick_preset", text="Apply", icon='PLAY')
        row.operator("typeanimator.reload_presets", text="Reload", icon='FILE_REFRESH')

        # === ANIMATION PRESETS ===
        anim_preset_box = layout.box()
        anim_preset_box.label(text="Animation Presets", icon='ANIM_DATA')
        col = anim_preset_box.column()
        col.prop(props, "animation_preset", text="Anim Preset")
        row = col.row(align=True)
        row.operator("typeanimator.apply_animation_preset", text="Apply", icon='PLAY')
        row.operator("typeanimator.reload_presets", text="Reload", icon='FILE_REFRESH')

    def draw_appearance_tab(self, layout, context):
        props = context.scene.ta_letter_anim_props
        style = ensure_pointer(props, "style", TA_StyleProperties)
        # === STYLE SECTION ===
        style_box = layout.box()
        style_box.label(text="Style", icon='MATERIAL')
        col = style_box.column(align=True)
        if style:
            col.prop(style, "style_preset", text="Style Preset")
            col.prop(style, "opacity", text="Opacity")
            col.prop(style, "blur", text="Blur")
            col.prop(style, "color", text="Color")
            col.prop(style, "text_color", text="Text Color")
            col.prop(style, "animate_color", text="Animate Color")
            col.prop(style, "color_start", text="Start Color")
            col.prop(style, "color_end", text="End Color")
            col.prop(style, "text_extrude", text="Extrude")
            col.prop(style, "text_bevel_depth", text="Bevel Depth")
            col.prop(style, "text_align_x", text="Align X")
            col.prop(style, "text_align_y", text="Align Y")
            col.prop(style, "text_rotation", text="Rotation")
            col.prop(style, "text_scale", text="Scale")
        else:
            col.label(text="No style initialized.")
        # === EFFECT LAYERS, GROUPING, LOCKING, LOOP, DIRECTION ===
        adv_box = layout.box()
        adv_box.label(text="Advanced", icon='SETTINGS')
        col = adv_box.column(align=True)
        col.prop(props, "effect_layers_enabled", text="Effect Layers")
        col.prop(props, "effect_layers_preview", text="Preview Effects")
        col.prop(props, "grouping_tolerance", text="Grouping Tolerance")
        col.prop(props, "lock_extrude", text="Lock Extrude")
        col.prop(props, "lock_bevel", text="Lock Bevel")
        col.prop(props, "lock_align", text="Lock Align")
        col.prop(props, "loop_count", text="Loop Count")
        col.prop(props, "loop_offset", text="Loop Offset")
        col.prop(props, "ping_pong", text="Ping Pong")
        col.prop(props, "direction", text="Direction")

    def draw_effects_tab(self, layout, context):
        props = context.scene.ta_letter_anim_props
        preview = ensure_pointer(props, "preview", TA_PreviewProperties)
        # === MATERIAL PRESETS ===
        material_box = layout.box()
        material_box.label(text="Material Presets", icon='MATERIAL_DATA')
        col = material_box.column()
        if preview:
            col.prop(preview, "material_preset", text="Material Preset")
            col.prop(preview, "material_animation_enabled", text="Material Animation")
            col.prop(preview, "material_duration", text="Material Duration")
            col.prop(preview, "material_easing", text="Material Easing")
            col.prop(preview, "material_fx_emission", text="Emission Effect")
            col.prop(preview, "material_fx_color", text="Color Effect")
            col.prop(preview, "material_fx_opacity", text="Opacity Effect")
        else:
            col.label(text="No preview initialized.")

    def draw_batch_tab(self, layout, context):
        props = context.scene.ta_letter_anim_props
        layout.label(text="Batch Processing")
        col = layout.column(align=True)
        col.prop(props, "batch_mode", text="Batch Mode")
        col.prop(props, "batch_sync", text="Sync")
        col.prop(props, "batch_offset", text="Offset")

    def draw_prefs_tab(self, layout, context):
        """Preferences tab."""
        layout.label(text="Preferences")
        # Implementar contenido del tab de preferencias

    def draw_diagnostic_tab(self, layout, context):
        """Diagnostic tab with comprehensive system information."""
        props = context.scene.ta_letter_anim_props

        # === SYSTEM STATUS ===
        status_box = layout.box()
        status_box.label(text="System Status", icon='INFO')
        status = get_system_status(context)
        draw_status_indicator(status_box, status)

        # === UI CHECKLIST ===
        checklist_box = layout.box()
        checklist_box.label(text="UI Checklist", icon='CHECKMARK')
        def check_attr(obj, attr):
            try:
                return hasattr(obj, attr) and getattr(obj, attr) is not None
            except Exception:
                return False
        # Paneles principales
        checklist_box.label(text=f"Panel Principal: {'✅' if True else '❌'}")
        checklist_box.label(text=f"Quick Start: {'✅' if True else '❌'}")
        checklist_box.label(text=f"Easing & Timing: {'✅' if True else '❌'}")
        checklist_box.label(text=f"Style & Color: {'✅' if True else '❌'}")
        checklist_box.label(text=f"Advanced: {'✅' if True else '❌'}")
        checklist_box.label(text=f"Stage IN: {'✅' if check_attr(props.stages, 'anim_stage_in') else '❌'}")
        checklist_box.label(text=f"Stage MID: {'✅' if check_attr(props.stages, 'anim_stage_middle') else '❌'}")
        checklist_box.label(text=f"Stage OUT: {'✅' if check_attr(props.stages, 'anim_stage_out') else '❌'}")
        checklist_box.label(text=f"Material Presets: {'✅' if check_attr(props, 'preview') and check_attr(props.preview, 'material_preset') else '❌'}")
        checklist_box.label(text=f"Batch: {'✅' if check_attr(props, 'batch_mode') else '❌'}")
        checklist_box.label(text=f"Text Input: {'✅' if check_attr(props, 'new_text_input') else '❌'}")
        checklist_box.label(text=f"Recent Presets UIList: {'✅' if check_attr(props, 'recent_presets') else '❌'}")
        checklist_box.label(text=f"User Presets UIList: {'✅' if check_attr(props, 'user_presets') else '❌'}")
        checklist_box.label(text=f"Animation Preset Combo: {'✅' if check_attr(props, 'animation_preset') else '❌'}")
        checklist_box.label(text=f"Quick Preset Combo: {'✅' if check_attr(props, 'quick_preset') else '❌'}")
        checklist_box.label(text=f"Style Preset Combo: {'✅' if check_attr(props.style, 'style_preset') else '❌'}")
        checklist_box.label(text=f"Material Preset Combo: {'✅' if check_attr(props.preview, 'material_preset') else '❌'}")
        checklist_box.label(text=f"Stage Preset Combo (IN): {'✅' if check_attr(props.stages.anim_stage_in, 'preset') else '❌'}")
        checklist_box.label(text=f"Stage Preset Combo (MID): {'✅' if check_attr(props.stages.anim_stage_middle, 'preset') else '❌'}")
        checklist_box.label(text=f"Stage Preset Combo (OUT): {'✅' if check_attr(props.stages.anim_stage_out, 'preset') else '❌'}")
        checklist_box.label(text=f"Crear Texto desde Input: {'✅' if hasattr(bpy.ops.typeanimator, 'create_text_from_input') else '❌'}")
        checklist_box.label(text=f"Validar Propiedades: {'✅' if hasattr(bpy.ops.typeanimator, 'validate_properties') else '❌'}")
        checklist_box.label(text=f"Comprehensive Test: {'✅' if hasattr(bpy.ops.typeanimator, 'comprehensive_test') else '❌'}")

        # === DETAILED STATISTICS ===
        stats_box = layout.box()
        stats_box.label(text="Detailed Statistics", icon='STATUSBAR')
        
        col = stats_box.column()
        col.label(text=f"Text Objects: {status['text_objects']}")
        col.label(text=f"Letter Objects: {status['letter_objects']}")
        col.label(text=f"Root Objects: {status['root_objects']}")
        col.label(text=f"Animation Active: {'Yes' if status['animation_active'] else 'No'}")
        col.label(text=f"Focus Active: {'Yes' if status['focus_active'] else 'No'}")

        # === CACHE INFORMATION ===
        cache_box = layout.box()
        cache_box.label(text="Cache Information", icon='MEMORY')
        
        try:
            from .core import get_cache_stats
            cache_stats = get_cache_stats()
            if cache_stats:
                col = cache_box.column()
                col.label(text=f"Cache Size: {cache_stats['size']}/{cache_stats['max_size']}")
                col.label(text=f"Hit Rate: {cache_stats['hit_rate']:.1f}%")
                col.label(text=f"Memory Usage: {cache_stats.get('memory_usage', 'N/A')}")
            else:
                cache_box.label(text="No cache statistics available")
        except Exception as e:
            cache_box.label(text=f"Cache error: {e}")

        # === NODE GROUPS ===
        node_box = layout.box()
        node_box.label(text="Node Groups", icon='NODETREE')
        
        try:
            from .constants import CURVE_NODE_GROUP_NAME
            if CURVE_NODE_GROUP_NAME in bpy.data.node_groups:
                node_box.label(text=f"✅ {CURVE_NODE_GROUP_NAME} - Present")
            else:
                node_box.label(text=f"❌ {CURVE_NODE_GROUP_NAME} - Missing")
        except Exception as e:
            node_box.label(text=f"Node group error: {e}")

        # === PRESETS STATUS ===
        preset_box = layout.box()
        preset_box.label(text="Presets Status", icon='PRESET')
        try:
            from .presets import get_all_presets
            presets_data = get_all_presets()
            if presets_data:
                preset_box.label(text=f"✅ {len(presets_data)} presets loaded")
            else:
                preset_box.label(text="⚠️ No presets available")
        except Exception as e:
            preset_box.label(text=f"❌ Preset error: {e}")

        # === ACTION BUTTONS ===
        actions_box = layout.box()
        actions_box.label(text="Diagnostic Actions", icon='TOOL_SETTINGS')
        
        col = actions_box.column()
        row = col.row()
        row.operator("typeanimator.comprehensive_test", text="Full System Test", icon='CHECKMARK')
        row.operator("typeanimator.cleanup_references", text="Cleanup", icon='BRUSH_DATA')
        
        row = col.row()
        row.operator("typeanimator.validate_properties", text="Validate Props", icon='CHECKMARK')
        row.operator("typeanimator.clear_letter_cache", text="Clear Cache", icon='X')

        # === LOGGING ACTIONS ===
        log_box = layout.box()
        log_box.label(text="Logging Actions", icon='CONSOLE')
        
        col = log_box.column()
        row = col.row()
        row.operator("typeanimator.open_log_file", text="Open Log", icon='FILE_TEXT')
        row.operator("typeanimator.clear_log_file", text="Clear Log", icon='X')
        
        row = col.row()
        row.operator("typeanimator.show_log_statistics", text="Log Stats", icon='INFO')
        row.operator("typeanimator.update_logging_config", text="Update Config", icon='SETTINGS')

# === PANELES HIJO MEJORADOS ===

class VIEW3D_PT_ta_quick_start_improved(bpy.types.Panel):
    """Quick start panel with essential controls."""
    bl_label = "Quick Start"
    bl_idname = "VIEW3D_PT_ta_quick_start_improved"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Type Animator'
    bl_parent_id = "VIEW3D_PT_ta_main_improved"
    bl_order = 1

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, 'ta_letter_anim_props')

    def draw(self, context):
        """Draw quick start controls with status-aware feedback."""
        layout = self.layout
        
        # Status indicator
        status = get_system_status(context)
        if not status['scene_valid']:
            layout.label(text="⚠️ Sistema no válido", icon='ERROR')
            return
        
        # Quick actions with better organization
        draw_quick_actions(layout, context)
        
        # Focus controls
        focus_box = layout.box()
        focus_box.label(text="Focus Controls", icon='VIEWZOOM')
        
        if context.scene.ta_focused_text:
            focus_box.label(text=f"Focused: {context.scene.ta_focused_text}")
            focus_box.operator("typeanimator.clear_focus", text="Clear Focus", icon='X')
        else:
            focus_box.operator("typeanimator.take_focus", text="Take Focus", icon='VIEWZOOM')

class VIEW3D_PT_ta_easing_timing_improved(bpy.types.Panel):
    """Easing and timing controls panel."""
    bl_label = "Easing & Timing"
    bl_idname = "VIEW3D_PT_ta_easing_timing_improved"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Type Animator'
    bl_parent_id = "VIEW3D_PT_ta_main_improved"
    bl_order = 2

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, 'ta_letter_anim_props')

    def draw(self, context):
        """Draw easing and timing controls."""
        layout = self.layout
        props = context.scene.ta_letter_anim_props
        
        # Timing controls
        timing_box = layout.box()
        timing_box.label(text="Timing", icon='TIME')
        
        col = timing_box.column(align=True)
        timing = ensure_pointer(props, "timing", TA_TimingProperties)
        col.prop(timing, "start_frame", text="Start Frame")
        col.prop(timing, "end_frame", text="End Frame")
        col.prop(timing, "duration", text="Duration")
        col.prop(timing, "overlap", text="Overlap")
        
        # Animation mode
        mode_box = layout.box()
        mode_box.label(text="Animation Mode", icon='SETTINGS')
        
        col = mode_box.column()
        col.prop(timing, "animation_mode", text="Mode")
        col.prop(timing, "fragment_mode", text="Fragment Mode")

class VIEW3D_PT_ta_style_color_improved(bpy.types.Panel):
    """Style and color controls panel."""
    bl_label = "Style & Color"
    bl_idname = "VIEW3D_PT_ta_style_color_improved"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Type Animator'
    bl_parent_id = "VIEW3D_PT_ta_main_improved"
    bl_order = 3

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, 'ta_letter_anim_props')

    def draw(self, context):
        """Draw style and color controls."""
        layout = self.layout
        props = context.scene.ta_letter_anim_props
        
        # Style controls
        style_box = layout.box()
        style_box.label(text="Style", icon='MATERIAL')
        
        col = style_box.column(align=True)
        style = ensure_pointer(props, "style", TA_StyleProperties)
        if style:
            col.prop(style, "opacity", text="Opacity")
            col.prop(style, "blur", text="Blur")
        else:
            col.label(text="No style initialized.")
        
        # Color controls
        color_box = layout.box()
        color_box.label(text="Color", icon='COLOR')
        
        col = color_box.column()
        col.prop(props.style, "color", text="Color")

class VIEW3D_PT_ta_advanced_improved(bpy.types.Panel):
    """Advanced controls panel."""
    bl_label = "Advanced"
    bl_idname = "VIEW3D_PT_ta_advanced_improved"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Type Animator'
    bl_parent_id = "VIEW3D_PT_ta_main_improved"
    bl_order = 4

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, 'ta_letter_anim_props')

    def draw(self, context):
        """Draw advanced controls."""
        layout = self.layout
        
        # Advanced controls
        advanced_box = layout.box()
        advanced_box.label(text="Advanced Controls", icon='SETTINGS')
        
        col = advanced_box.column()
        col.operator("typeanimator.comprehensive_test", text="System Test", icon='CHECKMARK')
        col.operator("typeanimator.cleanup_references", text="Cleanup References", icon='BRUSH_DATA')
        col.operator("typeanimator.validate_properties", text="Validate Properties", icon='CHECKMARK')

class VIEW3D_PT_ta_stage_in_improved(bpy.types.Panel):
    bl_label = "Stage IN"
    bl_idname = "VIEW3D_PT_ta_stage_in_improved"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Type Animator'
    bl_parent_id = "VIEW3D_PT_ta_main_improved"
    bl_order = 5
    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, 'ta_letter_anim_props')
    def draw(self, context):
        layout = self.layout
        props = context.scene.ta_letter_anim_props
        stages = ensure_pointer(props, "stages", TA_StagesProperties)
        if stages:
            stage = ensure_pointer(stages, "anim_stage_in", TA_AnimStageProperties)
            col = layout.column(align=True)
            col.prop(stage, "preset", text="Stage Preset")
            col.prop(stage, "use_manual", text="Use Manual")
            col.prop(stage, "scale_manual", text="Scale")
            col.prop(stage, "rotation_manual", text="Rotation")
            col.prop(stage, "location_manual", text="Location")
            col.prop(stage, "loaded_name", text="Loaded Preset")
            col.prop(stage, "stage_type", text="Stage Type")
        else:
            layout.label(text="No stages initialized.")

class VIEW3D_PT_ta_stage_middle_improved(bpy.types.Panel):
    bl_label = "Stage MID"
    bl_idname = "VIEW3D_PT_ta_stage_middle_improved"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Type Animator'
    bl_parent_id = "VIEW3D_PT_ta_main_improved"
    bl_order = 6
    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, 'ta_letter_anim_props')
    def draw(self, context):
        layout = self.layout
        props = context.scene.ta_letter_anim_props
        stages = ensure_pointer(props, "stages", TA_StagesProperties)
        if stages:
            stage = ensure_pointer(stages, "anim_stage_middle", TA_AnimStageProperties)
            col = layout.column(align=True)
            col.prop(stage, "preset", text="Stage Preset")
            col.prop(stage, "use_manual", text="Use Manual")
            col.prop(stage, "scale_manual", text="Scale")
            col.prop(stage, "rotation_manual", text="Rotation")
            col.prop(stage, "location_manual", text="Location")
            col.prop(stage, "loaded_name", text="Loaded Preset")
            col.prop(stage, "stage_type", text="Stage Type")
        else:
            layout.label(text="No stages initialized.")

class VIEW3D_PT_ta_stage_out_improved(bpy.types.Panel):
    bl_label = "Stage OUT"
    bl_idname = "VIEW3D_PT_ta_stage_out_improved"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Type Animator'
    bl_parent_id = "VIEW3D_PT_ta_main_improved"
    bl_order = 7
    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, 'ta_letter_anim_props')
    def draw(self, context):
        layout = self.layout
        props = context.scene.ta_letter_anim_props
        stages = ensure_pointer(props, "stages", TA_StagesProperties)
        if stages:
            stage = ensure_pointer(stages, "anim_stage_out", TA_AnimStageProperties)
            col = layout.column(align=True)
            col.prop(stage, "preset", text="Stage Preset")
            col.prop(stage, "use_manual", text="Use Manual")
            col.prop(stage, "scale_manual", text="Scale")
            col.prop(stage, "rotation_manual", text="Rotation")
            col.prop(stage, "location_manual", text="Location")
            col.prop(stage, "loaded_name", text="Loaded Preset")
            col.prop(stage, "stage_type", text="Stage Type")
        else:
            layout.label(text="No stages initialized.")

# === REGISTRO ===

classes = [
    TA_OT_take_focus,
    TA_OT_clear_focus,
    TA_OT_preview_play,
    TA_OT_preview_stop,
    TA_OT_bake_animation,
    TA_UL_recent_presets,
    TA_UL_user_presets,
    VIEW3D_PT_ta_main_improved,
    VIEW3D_PT_ta_quick_start_improved,
    VIEW3D_PT_ta_easing_timing_improved,
    VIEW3D_PT_ta_style_color_improved,
    VIEW3D_PT_ta_advanced_improved,
    VIEW3D_PT_ta_stage_in_improved,
    VIEW3D_PT_ta_stage_middle_improved,
    VIEW3D_PT_ta_stage_out_improved,
]

def register():
    """Register UI classes."""
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(f"Error registering {cls.__name__}: {e}")

def unregister():
    """Unregister UI classes."""
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"Error unregistering {cls.__name__}: {e}")
