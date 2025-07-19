import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import bpy  # type: ignore
except Exception:  # pragma: no cover - bpy not available in tests
    bpy = None

from . import easing_library
from .presets import safe_json_load
from .constants import PresetPriority

PRESET_DIR = Path(__file__).parent / 'presets'
USER_PRESET_DIR = Path(__file__).parent / 'user_presets'

SCHEMA_VERSION = 1

EXPORT_BUNDLE_VERSION = 1

def upgrade_settings(settings_dict):
    """Actualiza settings_dict al schema actual si es necesario."""
    if 'schema_version' not in settings_dict:
        settings_dict['schema_version'] = SCHEMA_VERSION
    # Aquí puedes agregar migraciones futuras
    return settings_dict

def get_user_preset_dir() -> Path:
    """Return the directory for user presets from prefs or default."""
    if bpy and hasattr(bpy.context, "preferences"):
        addon = bpy.context.preferences.addons.get(__package__)
        if addon:
            path = getattr(addon.preferences, "user_presets_dir", "")
            if path:
                return Path(path)
    return USER_PRESET_DIR

def slugify(name: str) -> str:
    """Return a filesystem-friendly version of a preset name."""
    name = name.strip().lower()
    name = re.sub(r'\s+', '_', name)
    return re.sub(r'[^a-z0-9_-]', '', name)

def user_preset_path(name: str, dir_path: Optional[Path] = None) -> Path:
    if dir_path is None:
        dir_path = get_user_preset_dir()
    slug = slugify(name)
    return dir_path / f'user_{slug}.json'

def save_user_preset(name: str, data: Dict[str, Any], dir_path: Optional[Path] = None) -> Path:
    """Save user preset data under ``presets/``."""
    path = user_preset_path(name, dir_path)
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path

def load_user_preset(name: str, dir_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load preset data by name."""
    path = user_preset_path(name, dir_path)
    if path.exists():
        with path.open('r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def delete_user_preset(name: str, dir_path: Optional[Path] = None) -> None:
    """Delete a user preset file if it exists."""
    path = user_preset_path(name, dir_path)
    if path.exists():
        path.unlink()

def list_user_presets(dir_path: Optional[Path] = None) -> List[str]:
    """Return a list of available user preset names without prefix."""
    if dir_path is None:
        dir_path = get_user_preset_dir()
    presets = []
    if dir_path.exists():
        for p in dir_path.glob('user_*.json'):
            name = p.stem[5:]  # strip 'user_'
            presets.append(name)
    return presets

def _props_to_dict(props: Any) -> Dict[str, Any]:
    """Recursively convert a PropertyGroup-like object to a dictionary."""
    data: Dict[str, Any] = {}
    for name in getattr(props, "__annotations__", {}):
        val = getattr(props, name)
        if hasattr(val, "__annotations__"):
            data[name] = _props_to_dict(val)
        else:
            try:
                json.dumps(val)
                data[name] = val
            except TypeError:
                if hasattr(val, "curves"):
                    try:
                        # Use full curve serialization
                        data[name + "_points"] = easing_library.serialize_curve(val)
                    except Exception:
                        pass
    return data

def _dict_to_props(data: Dict[str, Any], props: Any) -> None:
    for name, val in data.items():
        if not hasattr(props, name):
            continue
        attr = getattr(props, name)
        if hasattr(attr, "__annotations__") and isinstance(val, dict):
            _dict_to_props(val, attr)
        else:
            # If this is a curve, look for the _points key
            if hasattr(attr, "curves") and name + "_points" in data:
                try:
                    easing_library.deserialize_curve(attr, data[name + "_points"])
                except Exception:
                    pass
            else:
                try:
                    setattr(props, name, val)
                except Exception:
                    pass

def save_preset(name: str, props: Any, dir_path: Optional[Path] = None) -> Path:
    """Serialize props and save as user preset."""
    data = _props_to_dict(props)
    data = upgrade_settings(data)
    path = save_user_preset(name, data, dir_path)
    return path

def load_preset(name: str, props: Any, dir_path: Optional[Path] = None) -> None:
    """Load user preset and apply values to props."""
    data = load_user_preset(name, dir_path)
    if data:
        curve = data.pop("easing_curve", None)
        _dict_to_props(data, props)
        if curve and hasattr(props, "easing_curve"):
            try:
                mapping = props.easing_curve
                points = mapping.curves[0].points
                points.clear()
                for x, y in curve:
                    points.new(x, y)
            except Exception:
                pass

def delete_preset(name: str, dir_path: Optional[Path] = None) -> None:
    delete_user_preset(name, dir_path)

def export_preset_file(path: Path, props: Any) -> Path:
    """Export current properties to a JSON file at ``path``."""
    data = _props_to_dict(props)
    # Exportar también las curvas de easing in/mid/out
    for curve_name in ["easing_curve_in", "easing_curve_mid", "easing_curve_out"]:
        curve = getattr(props, curve_name, None)
        if curve and hasattr(curve, "curves"):
            try:
                pts = curve.curves[0].points
                data[curve_name] = [(float(p.location[0]), float(p.location[1])) for p in pts]
            except Exception:
                pass
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path

def import_preset_file(path: Path, props: Any) -> None:
    """Load properties from a JSON file."""
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    data = upgrade_settings(data)
    # Importar y restaurar curvas de easing in/mid/out
    for curve_name in ["easing_curve_in", "easing_curve_mid", "easing_curve_out"]:
        curve_data = data.pop(curve_name, None)
        if curve_data and hasattr(props, curve_name):
            mapping = getattr(props, curve_name)
            if hasattr(mapping, "curves"):
                try:
                    points = mapping.curves[0].points
                    points.clear()
                    for x, y in curve_data:
                        points.new(x, y)
                except Exception:
                    pass
    # Importar el resto de propiedades
    curve = data.pop("easing_curve", None)
    _dict_to_props(data, props)
    if curve and hasattr(props, "easing_curve"):
        try:
            mapping = props.easing_curve
            points = mapping.curves[0].points
            points.clear()
            for x, y in curve:
                points.new(x, y)
        except Exception:
            pass

def export_preset_bundle(props, path):
    """Exporta un bundle de preset con timing, curva, estilo y materiales."""
    bundle = {
        'schema_version': EXPORT_BUNDLE_VERSION,
        'timing': {k: getattr(props.timing, k) for k in dir(props.timing) if not k.startswith('_')},
        'style': {k: getattr(props.style, k) for k in dir(props.style) if not k.startswith('_')},
        'preview': {k: getattr(props.preview, k) for k in dir(props.preview) if not k.startswith('_')},
        'curva_in': easing_library.serialize_curve(props.stages.anim_stage_start.mapping) if hasattr(props.stages.anim_stage_start, 'mapping') else [],
        'curva_mid': easing_library.serialize_curve(props.stages.anim_stage_middle.mapping) if hasattr(props.stages.anim_stage_middle, 'mapping') else [],
        'curva_out': easing_library.serialize_curve(props.stages.anim_stage_end.mapping) if hasattr(props.stages.anim_stage_end, 'mapping') else [],
        'material': getattr(props, 'material_preset', None),
    }
    import json
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(bundle, f, indent=2)

def import_preset_bundle(path):
    """Importa y valida un bundle de preset. Devuelve el dict o None si hay error."""
    import json
    with open(path, 'r', encoding='utf-8') as f:
        bundle = json.load(f)
    if 'schema_version' not in bundle or bundle['schema_version'] < EXPORT_BUNDLE_VERSION:
        print(f"[TypeAnimator] Advertencia: versión de preset antigua o faltante en {path}")
    for key in ['timing', 'style', 'curva_in', 'curva_mid', 'curva_out']:
        if key not in bundle:
            print(f"[TypeAnimator] Advertencia: campo '{key}' faltante en bundle {path}")
    return bundle

def register():
    pass

def unregister():
    pass

# --- Operadores de Blender para gestión de presets (unificados desde operators/preset_manager.py) ---
import bpy
from bpy.props import StringProperty

PRESET_DIR = Path(__file__).resolve().parent / "presets"

class OBJECT_OT_save_preset(bpy.types.Operator):
    bl_idname = "typeanimator.save_preset"
    bl_label = "Save Preset"

    name: StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        props = context.scene.ta_letter_anim_props
        data = _props_to_dict(props)
        data = upgrade_settings(data)
        path = PRESET_DIR / f"{self.name.lower().replace(' ','_')}.json"
        with path.open('w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return {'FINISHED'}

class OBJECT_OT_load_preset(bpy.types.Operator):
    bl_idname = "typeanimator.load_preset"
    bl_label = "Load Preset"

    name: StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        path = PRESET_DIR / f"{self.name}.json"
        if not path.exists():
            self.report({'ERROR'}, "Preset not found")
            return {'CANCELLED'}
        data = safe_json_load(path.open('r', encoding='utf-8'), path)
        data = upgrade_settings(data)
        props = context.scene.ta_letter_anim_props
        curve = data.pop('easing_curve', None)
        interp = data.pop('interpolation', None)
        _dict_to_props(data, props)
        if curve and hasattr(props, 'easing_curve'):
            try:
                pts = props.easing_curve.curves[0].points
                pts.clear()
                for x, y in curve:
                    pts.new(x, y)
            except Exception:
                pass
        if interp and hasattr(props, 'interpolation'):
            props.interpolation = interp
        return {'FINISHED'}

class OBJECT_OT_delete_preset(bpy.types.Operator):
    bl_idname = "typeanimator.delete_preset"
    bl_label = "Delete Preset"

    name: StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        path = PRESET_DIR / f"{self.name}.json"
        if path.exists():
            path.unlink()
        if context.area:
            context.area.tag_redraw()
        return {'FINISHED'}

class OBJECT_OT_reset_presets(bpy.types.Operator):
    bl_idname = "typeanimator.reset_presets"
    bl_label = "Reset Presets"

    def execute(self, context):
        default = PRESET_DIR / "default_presets.json"
        if default.exists():
            data = safe_json_load(default.open('r', encoding='utf-8'), default)
            data = upgrade_settings(data)
            for p in PRESET_DIR.glob('*.json'):
                if p.name != 'default_presets.json':
                    p.unlink()
            for name, pdata in data.items():
                with (PRESET_DIR / f"{name}.json").open('w', encoding='utf-8') as f:
                    json.dump(pdata, f, indent=2)
        return {'FINISHED'}

# Registro de operadores

def register_operators():
    bpy.utils.register_class(OBJECT_OT_save_preset)
    bpy.utils.register_class(OBJECT_OT_load_preset)
    bpy.utils.register_class(OBJECT_OT_delete_preset)
    bpy.utils.register_class(OBJECT_OT_reset_presets)

def unregister_operators():
    bpy.utils.unregister_class(OBJECT_OT_reset_presets)
    bpy.utils.unregister_class(OBJECT_OT_delete_preset)
    bpy.utils.unregister_class(OBJECT_OT_load_preset)
    bpy.utils.unregister_class(OBJECT_OT_save_preset)

def apply_preset_with_priority(props, preset_data, priority=PresetPriority.OVERRIDE):
    """
    Aplica un preset con prioridad específica.
    
    Args:
        props: Propiedades del objeto
        preset_data: Datos del preset
        priority: Prioridad de aplicación
    """
    try:
        # Verificar que el preset tiene la estructura correcta
        if not isinstance(preset_data, dict):
            logger.warning(f"Preset data inválido: {type(preset_data)}")
            return False
        
        # Aplicar propiedades según categoría
        categories = preset_data.get('categories', {})
        
        for category, properties in categories.items():
            if category == PresetCategory.TIMING:
                _apply_timing_properties(props, properties)
            elif category == PresetCategory.MOTION:
                _apply_motion_properties(props, properties)
            elif category == PresetCategory.STYLE:
                _apply_style_properties(props, properties)
            elif category == PresetCategory.ENTRADA:
                _apply_entrada_properties(props, properties)
            elif category == PresetCategory.SALIDA:
                _apply_salida_properties(props, properties)
            elif category == PresetCategory.MATERIAL:
                _apply_material_properties(props, properties)
            elif category == PresetCategory.COMPOSITE:
                _apply_composite_properties(props, properties)
        
        # Aplicar curvas si están presentes
        if 'curves' in preset_data:
            _apply_curves(props, preset_data['curves'])
        
        logger.info(f"Preset aplicado con prioridad {priority}")
        return True
        
    except Exception as e:
        logger.error(f"Error aplicando preset con prioridad {priority}: {e}")
        return False

def _apply_timing_properties(props, properties):
    """Aplica propiedades de timing."""
    if hasattr(props, 'timing'):
        timing_props = props.timing
        for key, value in properties.items():
            if hasattr(timing_props, key):
                setattr(timing_props, key, value)

def _apply_motion_properties(props, properties):
    """Aplica propiedades de movimiento."""
    if hasattr(props, 'timing'):
        timing_props = props.timing
        for key, value in properties.items():
            if hasattr(timing_props, key):
                setattr(timing_props, key, value)

def _apply_style_properties(props, properties):
    """Aplica propiedades de estilo."""
    if hasattr(props, 'style'):
        style_props = props.style
        for key, value in properties.items():
            if hasattr(style_props, key):
                setattr(style_props, key, value)

def _apply_entrada_properties(props, properties):
    """Aplica propiedades de entrada."""
    if hasattr(props, 'stages') and hasattr(props.stages, 'anim_stage_in'):
        stage_props = props.stages.anim_stage_in
        for key, value in properties.items():
            if hasattr(stage_props, key):
                setattr(stage_props, key, value)

def _apply_salida_properties(props, properties):
    """Aplica propiedades de salida."""
    if hasattr(props, 'stages') and hasattr(props.stages, 'anim_stage_out'):
        stage_props = props.stages.anim_stage_out
        for key, value in properties.items():
            if hasattr(stage_props, key):
                setattr(stage_props, key, value)

def _apply_material_properties(props, properties):
    """Aplica propiedades de material."""
    if hasattr(props, 'preview'):
        preview_props = props.preview
        for key, value in properties.items():
            if hasattr(preview_props, key):
                setattr(preview_props, key, value)

def _apply_composite_properties(props, properties):
    """Aplica propiedades compuestas (todas las categorías)."""
    # Aplicar a todas las sub-propiedades
    for sub_prop_name in ['timing', 'style', 'preview', 'stages']:
        if hasattr(props, sub_prop_name):
            sub_props = getattr(props, sub_prop_name)
            for key, value in properties.items():
                if hasattr(sub_props, key):
                    setattr(sub_props, key, value)

def _apply_curves(props, curves_data):
    """Aplica curvas de easing."""
    try:
        for curve_name, curve_points in curves_data.items():
            if hasattr(props, curve_name):
                curve_mapping = getattr(props, curve_name)
                if hasattr(curve_mapping, 'curves'):
                    points = curve_mapping.curves[0].points
                    points.clear()
                    for x, y in curve_points:
                        points.new(x, y)
    except Exception as e:
        logger.warning(f"Error aplicando curvas: {e}")

def apply_preset_hierarchy(props):
    """
    Aplica presets en orden de prioridad: Quick Preset → Stage Presets → Overrides.
    
    Args:
        props: Propiedades del objeto
    """
    try:
        # 1. Aplicar Quick Preset (prioridad más alta)
        if hasattr(props, 'quick_preset') and props.quick_preset != 'NONE':
            quick_preset_data = load_preset_by_name(props.quick_preset)
            if quick_preset_data:
                apply_preset_with_priority(props, quick_preset_data, PresetPriority.QUICK_PRESET)
        
        # 2. Aplicar Stage Presets (prioridad media)
        if hasattr(props, 'stages'):
            stages = ['anim_stage_in', 'anim_stage_middle', 'anim_stage_out']
            for stage_name in stages:
                if hasattr(props.stages, stage_name):
                    stage_props = getattr(props.stages, stage_name)
                    if hasattr(stage_props, 'preset') and stage_props.preset != 'NONE':
                        stage_preset_data = load_preset_by_name(stage_props.preset)
                        if stage_preset_data:
                            apply_preset_with_priority(props, stage_preset_data, PresetPriority.STAGE_PRESET)
        
        # 3. Los overrides manuales ya están aplicados (prioridad más baja)
        logger.info("Jerarquía de presets aplicada correctamente")
        return True
        
    except Exception as e:
        logger.error(f"Error aplicando jerarquía de presets: {e}")
        return False

# Funciones dummy para completar el flujo
def load_preset_by_name(name):
    """Busca y carga el preset por nombre desde la carpeta presets/."""
    from .presets import safe_json_load
    path = PRESET_DIR / f"{name}.json"
    if path.exists():
        with path.open('r', encoding='utf-8') as f:
            return safe_json_load(f, path)
    return {}
def apply_preset_to_props(props, preset):
    pass
def apply_stage_preset(props, stage, preset):
    pass
def apply_preset_to_letter(letter_props, preset):
    pass
