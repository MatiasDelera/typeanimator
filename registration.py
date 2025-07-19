import bpy
from .preferences import TAAddonPreferences
from . import properties, icon_loader, utils, operators, ui, fonts, styles, presets, preset_manager, core, preview
from .settings_io import save_last_settings, load_last_settings
from .logging_config import setup_logging
from .handlers import register_handler, unregister_handler
from .constants import (
    CURVE_NODE_GROUP_NAME, SCENE_PROPERTIES, WM_PROPERTIES, 
    INFO_MESSAGES, ERROR_MESSAGES
)
from .curves import get_or_create_curve_node_group

try:
    logger = setup_logging()
except Exception as e:
    import logging
    logger = logging.getLogger(__name__)

# Importar operadores opcionales individualmente para mejor feedback de errores
try:
    from .operators import batch
except Exception as e:
    batch = None
    logger.warning(f"Error importando 'batch': {e}")
try:
    from .operators import gpencil_blur
except Exception as e:
    gpencil_blur = None
    logger.warning(f"Error importando 'gpencil_blur': {e}")
try:
    from .operators import curve_text
except Exception as e:
    curve_text = None
    logger.warning(f"Error importando 'curve_text': {e}")
try:
    from .operators import copy_paste
except Exception as e:
    copy_paste = None
    logger.warning(f"Error importando 'copy_paste': {e}")
try:
    from .operators import srt_import
except Exception as e:
    srt_import = None
    logger.warning(f"Error importando 'srt_import': {e}")

# Estos módulos no existen en operators/, así que los removemos
op_preset_manager = None
op_preview = None

# Flags para evitar registro duplicado
_registration_flags = {
    'preferences_registered': False,
    'properties_registered': False,
    'operators_registered': False,
    'ui_registered': False,
    'handlers_registered': False
}

def register():
    """Registro robusto y ordenado del addon con manejo de errores mejorado."""
    global _registration_flags
    
    try:
        logger.info("Iniciando registro de TypeAnimator...")
        
        # === PASO 1: Registrar preferencias ===
        if not _registration_flags['preferences_registered']:
            try:
                bpy.utils.unregister_class(TAAddonPreferences)
            except Exception:
                pass
            bpy.utils.register_class(TAAddonPreferences)
            _registration_flags['preferences_registered'] = True
            logger.debug("Preferencias registradas")
        
        # === PASO 2: Registrar propiedades COMPLETAMENTE antes que UI ===
        if not _registration_flags['properties_registered']:
            try:
                # Primero registrar presets
                presets.register()
                
                # Luego registrar propiedades
                properties.register()
                
                # VERIFICAR que el PointerProperty está asignado
                if not hasattr(bpy.types.Scene, 'ta_letter_anim_props'):
                    raise RuntimeError("ta_letter_anim_props no está asignada a bpy.types.Scene tras registrar properties")
                
                # Forzar inicialización en todas las escenas
                properties.force_init_ta_stages_all_scenes()
                
                # Cargar presets de stage si existen
                if hasattr(presets, 'load_stage_presets'):
                    presets.load_stage_presets()
                
                # Actualizar enums ANTES de registrar UI
                if hasattr(properties, 'update_preset_enums'):
                    properties.update_preset_enums()
                if hasattr(properties, 'update_anim_preset_enum'):
                    properties.update_anim_preset_enum()
                
                _registration_flags['properties_registered'] = True
                logger.debug("Propiedades completamente registradas y verificadas")
                
            except Exception as e:
                logger.error(f"Error registrando propiedades: {e}")
                raise
        
        # === PASO 3: Crear Node Group central de curvas ===
        try:
            node_group = get_or_create_curve_node_group()
            if node_group:
                logger.debug(f"Node Group '{CURVE_NODE_GROUP_NAME}' verificado/creado")
            else:
                def _late_nodegroup():
                    from . import curves
                    ng = curves.get_or_create_curve_node_group('txFxCurveData')
                    if ng:
                        print("[typeanimator] NodeGroup txFxCurveData creado tardío")
                    return None
                if hasattr(bpy.app, 'timers'):
                    bpy.app.timers.register(_late_nodegroup, first_interval=0.2)
                logger.warning("Node Group no disponible, programado para creación tardía")
        except Exception as e:
            logger.error(f"Error creando Node Group: {e}")
        
        # === PASO 4: Registrar módulos principales SOLO si propiedades están listas ===
        if hasattr(bpy.types.Scene, 'ta_letter_anim_props') and _registration_flags['properties_registered']:
            modules_to_register = [
                ('icon_loader', icon_loader),
                ('utils', utils),
                ('operators', operators),
                ('ui', ui),  # UI va DESPUÉS de que propiedades estén completamente listas
                ('styles', styles),
                ('preset_manager', preset_manager),
                ('core', core),
                ('preview', preview),
                ('fonts', fonts),
            ]
            
            for module_name, module in modules_to_register:
                try:
                    if hasattr(module, 'register'):
                        module.register()
                        logger.debug(f"Módulo '{module_name}' registrado")
                    else:
                        logger.warning(f"Módulo '{module_name}' no tiene método register")
                except Exception as e:
                    logger.error(f"Error registrando módulo '{module_name}': {e}")
                    raise
        else:
            logger.error("No se registró la UI porque ta_letter_anim_props no existe en Scene o propiedades no están completamente registradas.")
            raise RuntimeError("Propiedades no disponibles para UI")
        
        # === PASO 5: Registrar operadores opcionales ===
        optional_modules = [
            ('batch', batch),
            ('gpencil_blur', gpencil_blur),
            ('curve_text', curve_text),
            ('copy_paste', copy_paste),
            ('srt_import', srt_import),
            ('op_preset_manager', op_preset_manager),
            ('op_preview', op_preview),
        ]
        
        for module_name, module in optional_modules:
            if module is not None:
                try:
                    if hasattr(module, 'register'):
                        module.register()
                        logger.debug(f"Módulo opcional '{module_name}' registrado")
                except Exception as e:
                    logger.warning(f"Error registrando módulo opcional '{module_name}': {e}")
        
        # === PASO 6: Actualizar enums y cargar configuración ===
        try:
            if hasattr(bpy.app, 'timers'):
                def deferred_updates():
                    try:
                        properties.update_preset_enums()
                        properties.update_anim_preset_enum()
                        from bpy import context
                        for window in context.window_manager.windows:
                            for area in window.screen.areas:
                                if area.type == 'VIEW_3D':
                                    area.tag_redraw()
                        load_last_settings()
                        logger.debug("Enums actualizados, UI refrescada y configuración cargada")
                    except Exception as e:
                        logger.warning(f"Error en actualizaciones diferidas: {e}")
                    return None
                bpy.app.timers.register(deferred_updates, first_interval=0.5)
            else:
                try:
                    properties.update_preset_enums()
                    properties.update_anim_preset_enum()
                    from bpy import context
                    for window in context.window_manager.windows:
                        for area in window.screen.areas:
                            if area.type == 'VIEW_3D':
                                area.tag_redraw()
                    load_last_settings()
                    logger.debug("Enums actualizados, UI refrescada y configuración cargada")
                except Exception as e:
                    logger.warning(f"Error actualizando enums: {e}")
        except Exception as e:
            logger.warning(f"Error configurando actualizaciones diferidas: {e}")
        
        # === PASO 7: Registrar handlers ===
        if not _registration_flags['handlers_registered']:
            try:
                register_handler()
                _registration_flags['handlers_registered'] = True
                logger.debug("Handlers registrados")
            except Exception as e:
                logger.error(f"Error registrando handlers: {e}")
        
        # === PASO 8: Registrar propiedades adicionales ===
        try:
            # Propiedades de escena
            for prop_name, prop_value in SCENE_PROPERTIES.items():
                if not hasattr(bpy.types.Scene, prop_value):
                    setattr(bpy.types.Scene, prop_value, bpy.props.StringProperty(
                        name=f"Texto en Foco" if prop_name == 'FOCUSED_TEXT' else f"Propiedad {prop_name}",
                        description=f"Propiedad {prop_name} de TypeAnimator",
                        default=""
                    ))
            
            # Propiedades de WindowManager
            for prop_name, prop_value in WM_PROPERTIES.items():
                if not hasattr(bpy.types.WindowManager, prop_value):
                    setattr(bpy.types.WindowManager, prop_value, bpy.props.StringProperty(
                        name=f"Estado del Sistema" if prop_name == 'STATUS' else f"Propiedad {prop_name}",
                        description=f"Propiedad {prop_name} de TypeAnimator",
                        default=""
                    ))
            
            logger.debug("Propiedades adicionales registradas")
        except Exception as e:
            logger.error(f"Error registrando propiedades adicionales: {e}")
        
        logger.info("TypeAnimator registrado exitosamente")
        
    except Exception as e:
        logger.error(f"Error durante el registro de TypeAnimator: {e}")
        # Intentar limpiar en caso de error
        try:
            unregister()
        except Exception as cleanup_error:
            logger.error(f"Error durante limpieza: {cleanup_error}")
        raise

def unregister():
    """Desregistro ordenado del addon."""
    global _registration_flags
    
    try:
        logger.info("Iniciando desregistro de TypeAnimator...")
        
        # === PASO 1: Desregistrar handlers ===
        if _registration_flags['handlers_registered']:
            try:
                unregister_handler()
                _registration_flags['handlers_registered'] = False
                logger.debug("Handlers desregistrados")
            except Exception as e:
                logger.error(f"Error desregistrando handlers: {e}")
        
        # === PASO 2: Desregistrar módulos principales en orden inverso ===
        modules_to_unregister = [
            ('preview', preview),
            ('core', core),
            ('preset_manager', preset_manager),
            ('styles', styles),
            ('fonts', fonts),
            ('ui', ui),
            ('operators', operators),
            ('utils', utils),
            ('icon_loader', icon_loader),
        ]
        
        for module_name, module in modules_to_unregister:
            try:
                if hasattr(module, 'unregister'):
                    module.unregister()
                    logger.debug(f"Módulo '{module_name}' desregistrado")
                else:
                    logger.warning(f"Módulo '{module_name}' no tiene método unregister")
            except Exception as e:
                logger.warning(f"Error desregistrando módulo '{module_name}': {e}")
        
        # === PASO 3: Desregistrar operadores opcionales ===
        optional_modules = [
            ('op_preview', op_preview),
            ('op_preset_manager', op_preset_manager),
            ('srt_import', srt_import),
            ('copy_paste', copy_paste),
            ('curve_text', curve_text),
            ('gpencil_blur', gpencil_blur),
            ('batch', batch),
        ]
        
        for module_name, module in optional_modules:
            if module is not None:
                try:
                    if hasattr(module, 'unregister'):
                        module.unregister()
                        logger.debug(f"Módulo opcional '{module_name}' desregistrado")
                except Exception as e:
                    logger.warning(f"Error desregistrando módulo opcional '{module_name}': {e}")
        
        # === PASO 4: Desregistrar propiedades ===
        if _registration_flags['properties_registered']:
            try:
                properties.unregister()
                presets.unregister()
                _registration_flags['properties_registered'] = False
                logger.debug("Propiedades desregistradas")
            except Exception as e:
                logger.error(f"Error desregistrando propiedades: {e}")
        
        # === PASO 5: Desregistrar preferencias ===
        if _registration_flags['preferences_registered']:
            try:
                bpy.utils.unregister_class(TAAddonPreferences)
                _registration_flags['preferences_registered'] = False
                logger.debug("Preferencias desregistradas")
            except Exception as e:
                logger.error(f"Error desregistrando preferencias: {e}")
        
        # === PASO 6: Limpiar propiedades adicionales ===
        try:
            # Propiedades de escena
            for prop_name, prop_value in SCENE_PROPERTIES.items():
                if hasattr(bpy.types.Scene, prop_value):
                    delattr(bpy.types.Scene, prop_value)
            
            # Propiedades de WindowManager
            for prop_name, prop_value in WM_PROPERTIES.items():
                if hasattr(bpy.types.WindowManager, prop_value):
                    delattr(bpy.types.WindowManager, prop_value)
            
            logger.debug("Propiedades adicionales limpiadas")
        except Exception as e:
            logger.error(f"Error limpiando propiedades adicionales: {e}")
        
        # === PASO 7: Limpiar Node Group ===
        try:
            if hasattr(bpy.data, "node_groups") and CURVE_NODE_GROUP_NAME in bpy.data.node_groups:
                bpy.data.node_groups.remove(bpy.data.node_groups[CURVE_NODE_GROUP_NAME])
                logger.debug(f"Node Group '{CURVE_NODE_GROUP_NAME}' eliminado")
        except Exception as e:
            logger.error(f"Error eliminando Node Group: {e}")
        
        # Reset flags
        _registration_flags = {
            'preferences_registered': False,
            'properties_registered': False,
            'operators_registered': False,
            'ui_registered': False,
            'handlers_registered': False
        }
        
        logger.info("TypeAnimator desregistrado exitosamente")
        
    except Exception as e:
        logger.error(f"Error durante el desregistro de TypeAnimator: {e}")
        raise