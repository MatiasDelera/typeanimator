import bpy
import logging
from . import presets, icon_loader, easing_library
from .presets import get_all_presets, PresetItem

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------
# Utilidades de Items Dinámicos
# ----------------------------------------------------------------

def get_preset_items(self, context):
    """Items genéricos (todos los presets cargados)."""
    from .presets import get_all_presets
    import os
    all_presets = get_all_presets()
    items = [('NONE', "None", "No preset")]
    try:
        preset_dir = os.path.join(os.path.dirname(__file__), 'presets')
        json_files = [f for f in os.listdir(preset_dir) if f.endswith('.json')]
        if not all_presets and json_files:
            raise RuntimeError("[typeanimator] No se cargaron presets aunque existen archivos JSON en presets/")
        for key, data in all_presets.items():
            label = data.get('name', key)
            desc = data.get('description', "")
            items.append((key, label, desc))
    except Exception as e:
        print(f"[typeanimator] get_preset_items error: {e}")
        raise
    return items

def get_quick_preset_items(self, context):
    """Enum dinámica para quick presets (actualmente misma lógica que get_preset_items)."""
    return get_preset_items(self, context)

def get_animation_preset_items(self, context):
    """Enum dinámica filtrada a presets de subtipo animation."""
    from .presets import get_all_presets
    import os
    items = [('NONE', "None", "Sin preset de animación")]
    try:
        all_presets = get_all_presets()
        preset_dir = os.path.join(os.path.dirname(__file__), 'presets')
        json_files = [f for f in os.listdir(preset_dir) if f.endswith('.json')]
        if not all_presets and json_files:
            raise RuntimeError("[typeanimator] No se cargaron presets aunque existen archivos JSON en presets/")
        for key, data in all_presets.items():
            if isinstance(data, dict) and data.get('subtype') == 'animation':
                label = data.get('name', key)
                desc = data.get('description', "")
                items.append((key, label, desc))
    except Exception as e:
        print(f"[typeanimator] get_animation_preset_items error: {e}")
        raise
    return items

# ----------------------------------------------------------------
# Property Groups
# ----------------------------------------------------------------

def on_change_stage_preset(self, context):
    from .presets import get_all_presets
    preset_id = self.preset
    if preset_id == 'NONE':
        return
    preset = get_all_presets().get(preset_id)
    if not preset:
        print(f"[typeanimator] No se encontró el preset de stage '{preset_id}'")
        return
    if 'scale' in preset and hasattr(self, 'scale_manual'):
        self.scale_manual = preset['scale']
    if 'rotation' in preset and hasattr(self, 'rotation_manual'):
        self.rotation_manual = preset['rotation']
    if 'location' in preset and hasattr(self, 'location_manual'):
        self.location_manual = preset['location']
    # Añadir más campos según tu estructura de presets

def on_change_style_preset(self, context):
    from .presets import get_all_presets
    preset_id = self.style_preset
    if preset_id == 'NONE':
        return
    preset = get_all_presets().get(preset_id)
    if not preset:
        print(f"[typeanimator] No se encontró el style preset '{preset_id}'")
        return
    if 'color' in preset and hasattr(self, 'color'):
        self.color = preset['color']
    if 'text_color' in preset and hasattr(self, 'text_color'):
        self.text_color = preset['text_color']
    # Añadir más campos según tu estructura de presets

def on_change_material_preset(self, context):
    from .presets import get_all_presets
    preset_id = self.material_preset
    if preset_id == 'NONE':
        return
    preset = get_all_presets().get(preset_id)
    if not preset:
        print(f"[typeanimator] No se encontró el material preset '{preset_id}'")
        return
    if 'material_duration' in preset and hasattr(self, 'material_duration'):
        self.material_duration = preset['material_duration']
    if 'material_easing' in preset and hasattr(self, 'material_easing'):
        self.material_easing = preset['material_easing']
    # Añadir más campos según tu estructura de presets

class TA_AnimStageProperties(bpy.types.PropertyGroup):
    """Properties for animation stages (IN, MID, OUT)."""
    use_manual = bpy.props.BoolProperty(
        name="Use Manual",
        description="Use manual values instead of preset",
        default=False
    )
    preset = bpy.props.EnumProperty(
        name="Preset",
        description="Animation preset for this stage",
        items=get_preset_items,
        default='NONE',
        update=on_change_stage_preset
    )
    scale_manual = bpy.props.FloatVectorProperty(
        name="Scale",
        description="Manual scale values",
        size=3,
        default=(1.0, 1.0, 1.0),
        subtype='XYZ'
    )
    rotation_manual = bpy.props.FloatVectorProperty(
        name="Rotation",
        description="Manual rotation values",
        size=3,
        default=(0.0, 0.0, 0.0),
        subtype='EULER'
    )
    location_manual = bpy.props.FloatVectorProperty(
        name="Location",
        description="Manual location values",
        size=3,
        default=(0.0, 0.0, 0.0),
        subtype='XYZ'
    )
    loaded_name = bpy.props.StringProperty(
        name="Loaded Preset",
        description="Name of the currently loaded preset",
        default=""
    )
    stage_type = bpy.props.StringProperty(
        name="Stage Type",
        description="Type of stage (IN, MID, OUT)",
        default=""
    )

class TA_TimingProperties(bpy.types.PropertyGroup):
    """Properties for timing and animation control."""
    start_frame = bpy.props.IntProperty(
        name="Start Frame",
        description="Starting frame for animation",
        default=1,
        min=1
    )
    end_frame = bpy.props.IntProperty(
        name="End Frame",
        description="Ending frame for animation",
        default=100,
        min=1
    )
    duration = bpy.props.IntProperty(
        name="Duration",
        description="Duration of animation per letter",
        default=50,
        min=1
    )
    overlap = bpy.props.IntProperty(
        name="Overlap",
        description="Overlap between letters",
        default=5,
        min=0
    )
    animation_mode = bpy.props.EnumProperty(
        name="Animation Mode",
        description="How letters are animated",
        items=[
            ('SECUENCIAL', "Secuencial", "Animate letters one by one"),
            ('SIMULTANEO', "Simultáneo", "Animate all letters at once"),
            ('INDIVIDUAL', "Individual", "Custom timing for each letter")
        ],
        default='SECUENCIAL'
    )
    fragment_mode = bpy.props.EnumProperty(
        name="Fragment Mode",
        description="How to fragment the text",
        items=[
            ('LETTERS', "Letters", "Separate by letters"),
            ('WORDS', "Words", "Separate by words"),
            ('SYLLABLES', "Syllables", "Separate by syllables")
        ],
        default='LETTERS'
    )

class TA_StyleProperties(bpy.types.PropertyGroup):
    """Properties for text styling and appearance."""
    color = bpy.props.FloatVectorProperty(
        name="Base Color",
        description="Base color for the text",
        size=4,
        default=(1.0, 1.0, 1.0, 1.0),
        subtype='COLOR'
    )
    text_color = bpy.props.FloatVectorProperty(
        name="Text Color",
        description="Color for the text",
        size=4,
        default=(1.0, 1.0, 1.0, 1.0),
        subtype='COLOR'
    )
    animate_color = bpy.props.BoolProperty(
        name="Animate Color",
        description="Animate the color",
        default=False
    )
    color_start = bpy.props.FloatVectorProperty(
        name="Start Color",
        description="Starting color for animation",
        size=4,
        default=(1.0, 1.0, 1.0, 1.0),
        subtype='COLOR'
    )
    color_end = bpy.props.FloatVectorProperty(
        name="End Color",
        description="Ending color for animation",
        size=4,
        default=(1.0, 1.0, 1.0, 1.0),
        subtype='COLOR'
    )
    text_extrude = bpy.props.FloatProperty(
        name="Extrude",
        description="Extrusion depth",
        default=0.0
    )
    text_bevel_depth = bpy.props.FloatProperty(
        name="Bevel Depth",
        description="Bevel depth",
        default=0.0
    )
    text_align_x = bpy.props.EnumProperty(
        name="Align X",
        description="Horizontal alignment",
        items=[
            ('LEFT', "Left", ""),
            ('CENTER', "Center", ""),
            ('RIGHT', "Right", ""),
            ('JUSTIFY', "Justify", "")
        ],
        default='LEFT'
    )
    text_align_y = bpy.props.EnumProperty(
        name="Align Y",
        description="Vertical alignment",
        items=[
            ('TOP', "Top", ""),
            ('CENTER', "Center", ""),
            ('BOTTOM', "Bottom", ""),
            ('BASELINE', "Baseline", "")
        ],
        default='BASELINE'
    )
    text_rotation = bpy.props.FloatProperty(
        name="Rotation",
        description="Text rotation in degrees",
        default=0.0,
        subtype='ANGLE'
    )
    text_scale = bpy.props.FloatProperty(
        name="Scale",
        description="Text scale",
        default=1.0
    )
    blur = bpy.props.FloatProperty(
        name="Blur",
        description="Blur amount",
        default=0.0,
        min=0.0,
        max=10.0
    )
    style_preset = bpy.props.EnumProperty(
        name="Style Preset",
        description="Preset de estilo",
        items=get_preset_items,
        default='NONE',
        update=on_change_style_preset
    )

class TA_PreviewProperties(bpy.types.PropertyGroup):
    """Properties for preview and real-time features."""
    enable_live_preview = bpy.props.BoolProperty(
        name="Live Preview",
        description="Enable live preview of animation",
        default=False
    )
    show_curves = bpy.props.BoolProperty(
        name="Show Curves",
        description="Show curve editor",
        default=False
    )
    material_animation_enabled = bpy.props.BoolProperty(
        name="Material Animation",
        description="Enable material animation",
        default=False
    )
    material_preset = bpy.props.EnumProperty(
        name="Material Preset",
        description="Preset de material",
        items=get_preset_items,
        default='NONE',
        update=on_change_material_preset
    )
    material_duration = bpy.props.FloatProperty(
        name="Material Duration",
        description="Duration of material animation",
        default=1.0
    )
    material_easing = bpy.props.StringProperty(
        name="Material Easing",
        description="Easing function for material animation",
        default="LINEAR"
    )
    material_fx_emission = bpy.props.BoolProperty(
        name="Emission Effect",
        description="Enable emission effect",
        default=False
    )
    material_fx_color = bpy.props.BoolProperty(
        name="Color Effect",
        description="Enable color effect",
        default=False
    )
    material_fx_opacity = bpy.props.BoolProperty(
        name="Opacity Effect",
        description="Enable opacity effect",
        default=False
    )

class TA_StagesProperties(bpy.types.PropertyGroup):
    """Properties for animation stages."""
    anim_stage_in = bpy.props.PointerProperty(type=TA_AnimStageProperties)
    anim_stage_middle = bpy.props.PointerProperty(type=TA_AnimStageProperties)
    anim_stage_out = bpy.props.PointerProperty(type=TA_AnimStageProperties)

class TA_LetterAnimProperties(bpy.types.PropertyGroup):
    """Main properties for letter animation."""
    quick_preset = bpy.props.EnumProperty(
        name="Quick Preset",
        description="Quick animation preset",
        items=get_quick_preset_items,
        default='NONE'
    )
    ui_tab = bpy.props.EnumProperty(
        name="UI Tab",
        description="Current UI tab",
        items=[
            ('TEXT', "Text", "Text configuration"),
            ('ANIMATE', "Animate", "Animation settings"),
            ('APPEARANCE', "Appearance", "Style and appearance"),
            ('EFFECTS', "Effects", "Effects and curves"),
            ('BATCH', "Batch", "Batch processing"),
            ('PREFS', "Preferences", "Preferences and settings"),
            ('DIAGNOSTIC', "Diagnostic", "System diagnostics"),
            ('EXPORT', "Export", "Export and import bundles")
        ],
        default='TEXT'
    )
    active_tab = bpy.props.EnumProperty(
        name="Active Tab",
        description="Current active tab",
        items=[
            ('ANIMATE', "Animate", "Animation settings"),
            ('EFFECTS', "Effects", "Effects and curves"),
            ('DIAGNOSTIC', "Diagnostic", "System diagnostics"),
            ('EXPORT', "Export", "Export and import bundles")
        ],
        default='ANIMATE'
    )
    timing = bpy.props.PointerProperty(type=TA_TimingProperties)
    style = bpy.props.PointerProperty(type=TA_StyleProperties)
    preview = bpy.props.PointerProperty(type=TA_PreviewProperties)
    stages = bpy.props.PointerProperty(type=TA_StagesProperties)
    individual_letters = bpy.props.CollectionProperty(type=TA_AnimStageProperties)
    recent_presets = bpy.props.CollectionProperty(type=PresetItem)
    user_presets = bpy.props.CollectionProperty(type=PresetItem)
    recent_presets_index = bpy.props.IntProperty(default=0)
    user_presets_index = bpy.props.IntProperty(default=0)
    batch_mode = bpy.props.EnumProperty(
        name="Batch Mode",
        description="Batch processing mode",
        items=[
            ('ACTIVE', "Active", "Process active object"),
            ('SELECTED', "Selected", "Process selected objects")
        ],
        default='ACTIVE'
    )
    batch_sync = bpy.props.BoolProperty(
        name="Sync",
        description="Synchronize batch processing",
        default=True
    )
    batch_offset = bpy.props.IntProperty(
        name="Offset",
        description="Frame offset for batch processing",
        default=10
    )
    effect_layers_enabled = bpy.props.BoolProperty(
        name="Effect Layers",
        description="Enable effect layers",
        default=False
    )
    effect_layers_preview = bpy.props.BoolProperty(
        name="Preview Effects",
        description="Preview effect layers",
        default=False
    )
    base_name = bpy.props.StringProperty(
        name="Base Name",
        description="Base name for curve nodes",
        default=""
    )
    grouping_tolerance = bpy.props.FloatProperty(
        name="Grouping Tolerance",
        description="Tolerance for grouping letters",
        default=0.1
    )
    lock_extrude = bpy.props.BoolProperty(
        name="Lock Extrude",
        description="Lock extrusion property",
        default=False
    )
    lock_bevel = bpy.props.BoolProperty(
        name="Lock Bevel",
        description="Lock bevel property",
        default=False
    )
    lock_align = bpy.props.BoolProperty(
        name="Lock Align",
        description="Lock alignment property",
        default=False
    )
    text_bevel_resolution = bpy.props.IntProperty(
        name="Bevel Resolution",
        description="Bevel resolution",
        default=0,
        min=0
    )
    text_offset_x = bpy.props.FloatProperty(
        name="Offset X",
        description="Horizontal offset",
        default=0.0
    )
    text_offset_y = bpy.props.FloatProperty(
        name="Offset Y",
        description="Vertical offset",
        default=0.0
    )
    text_fill_mode = bpy.props.EnumProperty(
        name="Fill Mode",
        description="Text fill mode",
        items=[
            ('FRONT', "Front", ""),
            ('BACK', "Back", ""),
            ('BOTH', "Both", "")
        ],
        default='FRONT'
    )
    loop_count = bpy.props.IntProperty(
        name="Loop Count",
        description="Number of loops",
        default=1,
        min=1
    )
    loop_offset = bpy.props.IntProperty(
        name="Loop Offset",
        description="Frame offset between loops",
        default=0
    )
    ping_pong = bpy.props.BoolProperty(
        name="Ping Pong",
        description="Enable ping pong loop",
        default=False
    )
    direction = bpy.props.EnumProperty(
        name="Direction",
        description="Animation direction",
        items=[
            ('FORWARD', "Forward", "Animate forward"),
            ('BACKWARD', "Backward", "Animate backward"),
            ('RANDOM', "Random", "Random order")
        ],
        default='FORWARD'
    )
    # Preset duplicado removido (se usará quick_preset / animation_preset)
    def on_change_animation_preset(self, context):
        from .presets import get_all_presets
        preset_id = self.animation_preset
        if preset_id == 'NONE':
            return
        preset = get_all_presets().get(preset_id)
        if not preset:
            print(f"[typeanimator] No se encontró el preset de animación '{preset_id}'")
            return
        # Asignar campos esperados
        if hasattr(self, 'timing') and hasattr(self.timing, 'duration') and 'duration' in preset:
            self.timing.duration = preset['duration']
        if hasattr(self, 'timing') and hasattr(self.timing, 'overlap') and 'overlap' in preset:
            self.timing.overlap = preset['overlap']
        if hasattr(self, 'style') and hasattr(self.style, 'text_scale') and 'scale_start' in preset:
            self.style.text_scale = preset['scale_start']
        if hasattr(self, 'style') and hasattr(self.style, 'text_rotation') and 'rot_z' in preset:
            self.style.text_rotation = preset['rot_z']
        # Añadir más campos según tu estructura de presets
    animation_preset = bpy.props.EnumProperty(
        name="Animation Preset",
        description="Preset específico de animación",
        items=get_animation_preset_items,
        default='NONE',
        update=on_change_animation_preset
    )
    new_text_input = bpy.props.StringProperty(
        name="Nuevo Texto",
        description="Texto a crear desde el panel",
        default=""
    )

# ----------------------------------------------------------------
# Registro
# ----------------------------------------------------------------

def get_classes():
    return [
        TA_AnimStageProperties,
        TA_TimingProperties,
        TA_StyleProperties,
        TA_PreviewProperties,
        TA_StagesProperties,
        TA_LetterAnimProperties,
    ]

def apply_text_properties_realtime(context, property_name):
    """Hook futuro para aplicar cambios inmediatos al texto."""
    try:
        obj = context.active_object
        if not obj or obj.type != 'FONT':
            return
        # Implementar lógica si es necesario
    except Exception as e:
        print(f"[typeanimator] apply_text_properties_realtime error: {e}")

def register():
    from bpy.utils import register_class
    for cls in get_classes():
        try:
            register_class(cls)
        except Exception as e:
            print(f"[typeanimator] ERROR registrando {cls.__name__}: {e}")
    if not hasattr(bpy.types.Scene, 'ta_letter_anim_props'):
        bpy.types.Scene.ta_letter_anim_props = bpy.props.PointerProperty(type=TA_LetterAnimProperties)
    if not hasattr(bpy.types.Scene, 'ta_ui_tab'):
        bpy.types.Scene.ta_ui_tab = bpy.props.EnumProperty(
            name="Tabs",
            items=[
                ('PRESETS', "Presets", ""),
                ('EASING', "Easing & Timing", ""),
                ('STYLE', "Estilo & Colores", ""),
                ('ADVANCED', "Avanzado", ""),
            ],
            default='PRESETS'
        )

def unregister():
    from bpy.utils import unregister_class
    if hasattr(bpy.types.Scene, 'ta_letter_anim_props'):
        del bpy.types.Scene.ta_letter_anim_props
    if hasattr(bpy.types.Scene, 'ta_ui_tab'):
        del bpy.types.Scene.ta_ui_tab
    for cls in reversed(get_classes()):
        try:
            unregister_class(cls)
        except Exception as e:
            print(f"[typeanimator] ERROR al desregistrar {cls.__name__}: {e}")
    if hasattr(TA_LetterAnimProperties, '__annotations__'):
        TA_LetterAnimProperties.__annotations__.clear()
    logger.debug("Properties unregistered successfully")

# ----------------------------------------------------------------
# Inicialización / Helpers
# ----------------------------------------------------------------

def get_or_init_stage(stage, props=None, attr_name=None):
    if type(stage).__name__ == '_PropertyDeferred' and props is not None and attr_name is not None:
        try:
            # Acceso forzado sin reinstanciar manualmente
            _ = getattr(props, attr_name)
            stage = getattr(props, attr_name)
        except Exception:
            pass
    try:
        _ = stage.use_manual
    except Exception:
        pass
    return stage

def ensure_stages():
    """Ensure all stages are properly initialized (nombres tipo IN/MID/OUT)."""
    try:
        if hasattr(bpy.data, 'scenes') and not hasattr(bpy.data, '_RestrictData'):
            for scene in bpy.data.scenes:
                if hasattr(scene, 'ta_letter_anim_props'):
                    props = scene.ta_letter_anim_props
                    if props and hasattr(props, 'stages'):
                        stages = props.stages
                        for attr, label in [('anim_stage_in', 'IN'), ('anim_stage_middle', 'MID'), ('anim_stage_out', 'OUT')]:
                            try:
                                st = getattr(stages, attr)
                                if st:
                                    st.stage_type = label
                            except Exception as e:
                                print(f"[typeanimator] ensure_stages error: {e}")
    except Exception as e:
        print(f"[typeanimator] ensure_stages error: {e}")

def force_init_ta_stages_all_scenes():
    """Deferred initialization of stages after registration."""
    try:
        import bpy.app
        if hasattr(bpy.app, 'timers'):
            bpy.app.timers.register(lambda: (ensure_stages() or None), first_interval=0.1)
        else:
            ensure_stages()
    except Exception as e:
        logger.warning(f"Could not schedule stage initialization: {e}")

def update_preset_enums():
    """Update quick_preset enum state after (re)carga de presets."""
    import bpy as _b
    def _do_update():
        try:
            for scene in _b.data.scenes:
                props = getattr(scene, 'ta_letter_anim_props', None)
                if props:
                    props.quick_preset = 'NONE'
        except Exception as e:
            print(f"[typeanimator] update_preset_enums error: {e}")
        return None
    if hasattr(_b.app, 'timers'):
        _b.app.timers.register(_do_update, first_interval=0.1)
    else:
        _do_update()

def update_anim_preset_enum():
    """Valida que animation_preset apunte a un id existente."""
    import bpy
    from .properties import get_animation_preset_items
    def _reset():
        for scene in bpy.data.scenes:
            props = getattr(scene, 'ta_letter_anim_props', None)
            if props:
                anim_items = get_animation_preset_items(props, bpy.context)
                valid_ids = {i[0] for i in anim_items}
                if props.animation_preset not in valid_ids:
                    props.animation_preset = 'NONE'
        return None
    if hasattr(bpy.app, 'timers'):
        bpy.app.timers.register(_reset, first_interval=0.1)
    else:
        _reset()
