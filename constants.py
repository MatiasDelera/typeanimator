
"""
Constantes centralizadas para TypeAnimator
"""

# === VERSIONES ===
ADDON_VERSION = "1.0.0"
SCHEMA_VERSION = 1
EXPORT_BUNDLE_VERSION = 1

# === NOMBRES DE NODE GROUPS ===
CURVE_NODE_GROUP_NAME = "txFxCurveData"
CURVE_NODE_BASE_NAME = "txFxCurve"

# === PREFIJOS DE OPERADORES ===
OPERATOR_PREFIX = "typeanimator"

# === CATEGORÍAS UI ===
UI_CATEGORIES = {
    'TEXT': "Text",
    'ANIMATE': "Animate", 
    'APPEARANCE': "Appearance",
    'EFFECTS': "Effects",
    'BATCH': "Batch",
    'PREFS': "Preferences",
    'DIAGNOSTIC': "Diagnostic",
    'EXPORT': "Export"
}

# === PROPIEDADES DE OBJETOS ===
LETTER_PROPERTY = "is_letter"
ANIMATION_GROUP_PROPERTY = "is_animation_group"
ROOT_SUFFIX = "_Root"
ANIMATION_GROUP_SUFFIX = "_AnimGroup"
LETTER_PREFIX = "LetterEmpty_"

# === PROPIEDADES DE TRANSFORMACIONES ORIGINALES ===
ORIG_LOCATION = "orig_location"
ORIG_ROTATION = "orig_rotation"
ORIG_SCALE = "orig_scale"
ROOT_NAME = "root_name"

# === TIPOS DE OBJETOS ===
MESH_TYPE = 'MESH'
EMPTY_TYPE = 'EMPTY'
FONT_TYPE = 'FONT'

# === ARCHIVOS DE LOG ===
LOG_FILENAME = "typeanimator.log"

# === LÍMITES DE VALORES ===
MIN_FRAME = 1
MAX_FRAME = 999999
MIN_DURATION = 1
MAX_DURATION = 1000
MIN_OVERLAP = 0
MAX_OVERLAP = 100

# === CONFIGURACIÓN POR DEFECTO ===
DEFAULT_START_FRAME = 1
DEFAULT_END_FRAME = 100
DEFAULT_DURATION = 50
DEFAULT_OVERLAP = 5

# === ETAPAS DE ANIMACIÓN ===
ANIMATION_STAGES = ['in', 'mid', 'out']
STAGE_NAMES = {
    'in': 'IN',
    'mid': 'MID', 
    'out': 'OUT'
}

# === MODOS DE ANIMACIÓN ===
ANIMATION_MODES = {
    'SECUENCIAL': "Secuencial",
    'SIMULTANEO': "Simultáneo",
    'INDIVIDUAL': "Individual"
}

# === MODOS DE FRAGMENTACIÓN ===
FRAGMENT_MODES = {
    'LETTERS': "Letters",
    'WORDS': "Words", 
    'SYLLABLES': "Syllables"
}

# === CATEGORÍAS DE PRESETS ===
PRESET_CATEGORIES = {
    'TIMING': "Timing",
    'MOTION': "Motion",
    'STYLE': "Style",
    'ENTRADA': "Entrada",
    'SALIDA': "Salida",
    'MATERIAL': "Material",
    'COMPOSITE': "Composite"
}

# === PRIORIDADES DE PRESETS ===
PRESET_PRIORITIES = {
    'QUICK': "Quick Preset",
    'STAGE': "Stage Presets",
    'OVERRIDE': "Overrides"
}

# === NOMBRES DE PROPIEDADES DE ESCENA ===
SCENE_PROPERTIES = {
    'FOCUSED_TEXT': 'ta_focused_text',
    'SHOW_CRITICAL_CONTROLS': 'ta_show_critical_controls',
    'COMPACT_LAYOUT': 'ta_compact_layout',
    'SHOW_ACTIVE_STAGE_INDICATOR': 'ta_show_active_stage_indicator',
    'SHOW_FOCUS_INDICATOR': 'ta_show_focus_indicator'
}

# === NOMBRES DE PROPIEDADES DE WINDOW MANAGER ===
WM_PROPERTIES = {
    'STATUS': 'ta_status'
}

# === MENSAJES DE ERROR COMUNES ===
ERROR_MESSAGES = {
    'NO_TEXT_SELECTED': "No hay objeto de texto seleccionado",
    'NO_LETTERS_FOUND': "No se encontraron letras para animar",
    'INVALID_FRAME_RANGE': "Rango de frames inválido",
    'INVALID_DURATION': "Duración inválida",
    'NO_ROOT_EMPTY': "No se encontró empty raíz",
    'NO_ANIMATION_GROUP': "No se encontró grupo de animación",
    'PRESET_NOT_FOUND': "Preset no encontrado",
    'SAVE_PRESET_FAILED': "Error al guardar preset",
    'LOAD_PRESET_FAILED': "Error al cargar preset",
    'DUPLICATE_BL_IDNAME': "bl_idname duplicado detectado",
    'REGISTRATION_FAILED': "Error en registro de clase",
    'UNREGISTRATION_FAILED': "Error en desregistro de clase"
}

# === MENSAJES DE INFO ===
INFO_MESSAGES = {
    'REGISTRATION_SUCCESS': "TypeAnimator registrado exitosamente",
    'UNREGISTRATION_SUCCESS': "TypeAnimator desregistrado exitosamente",
    'CACHE_CLEARED': "Cache limpiado exitosamente",
    'PRESETS_RELOADED': "Presets recargados exitosamente",
    'BUNDLE_EXPORTED': "Bundle exportado exitosamente",
    'BUNDLE_IMPORTED': "Bundle importado exitosamente"
}

# === CONFIGURACIÓN DE CACHE ===
CACHE_CONFIG = {
    'MAX_SIZE': 100,
    'CLEANUP_THRESHOLD': 80,
    'TTL_HOURS': 24
}

# === CONFIGURACIÓN DE LOGGING ===
LOGGING_CONFIG = {
    'DEFAULT_LEVEL': 'INFO',
    'FILE_LEVEL': 'DEBUG',
    'CONSOLE_LEVEL': 'WARNING',
    'MAX_FILE_SIZE': 1024 * 1024,  # 1MB
    'BACKUP_COUNT': 3
}

# === CONFIGURACIÓN DE PERFORMANCE ===
PERFORMANCE_CONFIG = {
    'MAX_LETTERS_PREVIEW': 500,
    'SKIP_FRAMES_PREVIEW': 2,
    'CACHE_ENABLED': True,
    'LIVE_PREVIEW_ENABLED': True
}

# === CONFIGURACIÓN DE EXPORT BUNDLE ===
BUNDLE_CONFIG = {
    'DEFAULT_NAME': "Mi_Preset_Bundle",
    'FILE_EXTENSION': ".json",
    'ENCODING': "utf-8"
}

# === INTERNATIONALIZATION ===
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch',
    'it': 'Italiano',
    'pt': 'Português',
    'ja': '日本語',
    'zh': '中文',
    'ko': '한국어',
    'ru': 'Русский'
}

DEFAULT_LANGUAGE = 'en'

# Translation dictionaries
TRANSLATIONS = {
    'en': {
        # UI Labels
        'TYPE_ANIMATOR': 'Type Animator',
        'QUICK_START': 'Quick Start',
        'EASING_TIMING': 'Easing & Timing',
        'STYLE_COLOR': 'Style & Color',
        'ADVANCED': 'Advanced',
        'STAGE_IN': 'Stage IN',
        'STAGE_MID': 'Stage MID',
        'STAGE_OUT': 'Stage OUT',
        
        # Actions
        'SEPARATE': 'Separate',
        'ANIMATE': 'Animate',
        'BAKE': 'Bake',
        'RESET': 'Reset',
        'PREVIEW': 'Preview',
        'STOP': 'Stop',
        'APPLY': 'Apply',
        'CLEAR': 'Clear',
        
        # Status Messages
        'SYSTEM_STATUS': 'System Status',
        'SYSTEM_WORKING': 'System working',
        'SYSTEM_ERRORS': 'System with errors',
        'SYSTEM_WARNINGS': 'System with warnings',
        'TEXTS': 'Texts',
        'LETTERS': 'Letters',
        'ROOTS': 'Roots',
        
        # Error Messages
        'NO_TEXT_SELECTED': 'No text object selected',
        'NO_LETTERS_FOUND': 'No valid letters found',
        'INVALID_PROPERTIES': 'Invalid animation properties',
        'CACHE_ERROR': 'Cache error',
        'ANIMATION_FAILED': 'Animation failed',
        
        # Info Messages
        'ANIMATION_STARTED': 'Animation started',
        'ANIMATION_STOPPED': 'Animation stopped',
        'ANIMATION_BAKED': 'Animation baked to keyframes',
        'CACHE_CLEARED': 'Cache cleared',
        'PROPERTIES_VALIDATED': 'Properties validated',
        
        # Tooltips
        'SEPARATE_TOOLTIP': 'Separate text into individual letters',
        'ANIMATE_TOOLTIP': 'Apply animation to selected letters',
        'BAKE_TOOLTIP': 'Convert animation to keyframes',
        'RESET_TOOLTIP': 'Reset all properties to defaults',
        'PREVIEW_TOOLTIP': 'Start preview animation',
        'STOP_TOOLTIP': 'Stop preview animation',
        
        # Animation Modes
        'SEQUENTIAL': 'Sequential',
        'SIMULTANEOUS': 'Simultaneous',
        'INDIVIDUAL': 'Individual',
        
        # Fragment Modes
        'LETTERS': 'Letters',
        'WORDS': 'Words',
        'SYLLABLES': 'Syllables',
        
        # Timing
        'START_FRAME': 'Start Frame',
        'END_FRAME': 'End Frame',
        'DURATION': 'Duration',
        'OVERLAP': 'Overlap',
        
        # Style
        'OPACITY': 'Opacity',
        'BLUR': 'Blur',
        'COLOR': 'Color',
        'SCALE': 'Scale',
        'ROTATION': 'Rotation',
        
        # Diagnostic
        'DIAGNOSTIC': 'Diagnostic',
        'SYSTEM_TEST': 'System Test',
        'CACHE_STATS': 'Cache Statistics',
        'PERFORMANCE': 'Performance',
        'VALIDATION': 'Validation',
        
        # Export
        'EXPORT': 'Export',
        'IMPORT': 'Import',
        'BUNDLE': 'Bundle',
        'PRESETS': 'Presets',
        
        # Quick Presets
        'BOUNCE': 'Bounce',
        'FADE': 'Fade',
        'SCALE': 'Scale',
        'SHAKE': 'Shake',
        'SLIDE': 'Slide',
        'TYPE': 'Type',
        'WAVE': 'Wave'
    },
    
    'es': {
        # UI Labels
        'TYPE_ANIMATOR': 'Animador de Texto',
        'QUICK_START': 'Inicio Rápido',
        'EASING_TIMING': 'Easing y Tiempo',
        'STYLE_COLOR': 'Estilo y Color',
        'ADVANCED': 'Avanzado',
        'STAGE_IN': 'Etapa IN',
        'STAGE_MID': 'Etapa MID',
        'STAGE_OUT': 'Etapa OUT',
        
        # Actions
        'SEPARATE': 'Separar',
        'ANIMATE': 'Animar',
        'BAKE': 'Bake',
        'RESET': 'Reset',
        'PREVIEW': 'Vista Previa',
        'STOP': 'Detener',
        'APPLY': 'Aplicar',
        'CLEAR': 'Limpiar',
        
        # Status Messages
        'SYSTEM_STATUS': 'Estado del Sistema',
        'SYSTEM_WORKING': 'Sistema funcionando',
        'SYSTEM_ERRORS': 'Sistema con errores',
        'SYSTEM_WARNINGS': 'Sistema con advertencias',
        'TEXTS': 'Textos',
        'LETTERS': 'Letras',
        'ROOTS': 'Roots',
        
        # Error Messages
        'NO_TEXT_SELECTED': 'No hay objeto de texto seleccionado',
        'NO_LETTERS_FOUND': 'No se encontraron letras válidas',
        'INVALID_PROPERTIES': 'Propiedades de animación inválidas',
        'CACHE_ERROR': 'Error de cache',
        'ANIMATION_FAILED': 'La animación falló',
        
        # Info Messages
        'ANIMATION_STARTED': 'Animación iniciada',
        'ANIMATION_STOPPED': 'Animación detenida',
        'ANIMATION_BAKED': 'Animación convertida a keyframes',
        'CACHE_CLEARED': 'Cache limpiado',
        'PROPERTIES_VALIDATED': 'Propiedades validadas',
        
        # Tooltips
        'SEPARATE_TOOLTIP': 'Separar texto en letras individuales',
        'ANIMATE_TOOLTIP': 'Aplicar animación a letras seleccionadas',
        'BAKE_TOOLTIP': 'Convertir animación a keyframes',
        'RESET_TOOLTIP': 'Restablecer todas las propiedades',
        'PREVIEW_TOOLTIP': 'Iniciar vista previa de animación',
        'STOP_TOOLTIP': 'Detener vista previa de animación',
        
        # Animation Modes
        'SEQUENTIAL': 'Secuencial',
        'SIMULTANEOUS': 'Simultáneo',
        'INDIVIDUAL': 'Individual',
        
        # Fragment Modes
        'LETTERS': 'Letras',
        'WORDS': 'Palabras',
        'SYLLABLES': 'Sílabas',
        
        # Timing
        'START_FRAME': 'Frame Inicial',
        'END_FRAME': 'Frame Final',
        'DURATION': 'Duración',
        'OVERLAP': 'Superposición',
        
        # Style
        'OPACITY': 'Opacidad',
        'BLUR': 'Desenfoque',
        'COLOR': 'Color',
        'SCALE': 'Escala',
        'ROTATION': 'Rotación',
        
        # Diagnostic
        'DIAGNOSTIC': 'Diagnóstico',
        'SYSTEM_TEST': 'Prueba del Sistema',
        'CACHE_STATS': 'Estadísticas de Cache',
        'PERFORMANCE': 'Rendimiento',
        'VALIDATION': 'Validación',
        
        # Export
        'EXPORT': 'Exportar',
        'IMPORT': 'Importar',
        'BUNDLE': 'Paquete',
        'PRESETS': 'Presets',
        
        # Quick Presets
        'BOUNCE': 'Rebote',
        'FADE': 'Desvanecer',
        'SCALE': 'Escala',
        'SHAKE': 'Sacudir',
        'SLIDE': 'Deslizar',
        'TYPE': 'Escribir',
        'WAVE': 'Onda'
    },
    
    'fr': {
        # UI Labels
        'TYPE_ANIMATOR': 'Animateur de Texte',
        'QUICK_START': 'Démarrage Rapide',
        'EASING_TIMING': 'Easing et Timing',
        'STYLE_COLOR': 'Style et Couleur',
        'ADVANCED': 'Avancé',
        'STAGE_IN': 'Étape IN',
        'STAGE_MID': 'Étape MID',
        'STAGE_OUT': 'Étape OUT',
        
        # Actions
        'SEPARATE': 'Séparer',
        'ANIMATE': 'Animer',
        'BAKE': 'Cuire',
        'RESET': 'Réinitialiser',
        'PREVIEW': 'Aperçu',
        'STOP': 'Arrêter',
        'APPLY': 'Appliquer',
        'CLEAR': 'Effacer',
        
        # Status Messages
        'SYSTEM_STATUS': 'État du Système',
        'SYSTEM_WORKING': 'Système fonctionnel',
        'SYSTEM_ERRORS': 'Système avec erreurs',
        'SYSTEM_WARNINGS': 'Système avec avertissements',
        'TEXTS': 'Textes',
        'LETTERS': 'Lettres',
        'ROOTS': 'Racines',
        
        # Error Messages
        'NO_TEXT_SELECTED': 'Aucun objet texte sélectionné',
        'NO_LETTERS_FOUND': 'Aucune lettre valide trouvée',
        'INVALID_PROPERTIES': 'Propriétés d\'animation invalides',
        'CACHE_ERROR': 'Erreur de cache',
        'ANIMATION_FAILED': 'L\'animation a échoué',
        
        # Info Messages
        'ANIMATION_STARTED': 'Animation démarrée',
        'ANIMATION_STOPPED': 'Animation arrêtée',
        'ANIMATION_BAKED': 'Animation convertie en keyframes',
        'CACHE_CLEARED': 'Cache effacé',
        'PROPERTIES_VALIDATED': 'Propriétés validées',
        
        # Tooltips
        'SEPARATE_TOOLTIP': 'Séparer le texte en lettres individuelles',
        'ANIMATE_TOOLTIP': 'Appliquer l\'animation aux lettres sélectionnées',
        'BAKE_TOOLTIP': 'Convertir l\'animation en keyframes',
        'RESET_TOOLTIP': 'Réinitialiser toutes les propriétés',
        'PREVIEW_TOOLTIP': 'Démarrer l\'aperçu de l\'animation',
        'STOP_TOOLTIP': 'Arrêter l\'aperçu de l\'animation',
        
        # Animation Modes
        'SEQUENTIAL': 'Séquentiel',
        'SIMULTANEOUS': 'Simultané',
        'INDIVIDUAL': 'Individuel',
        
        # Fragment Modes
        'LETTERS': 'Lettres',
        'WORDS': 'Mots',
        'SYLLABLES': 'Syllabes',
        
        # Timing
        'START_FRAME': 'Frame de Début',
        'END_FRAME': 'Frame de Fin',
        'DURATION': 'Durée',
        'OVERLAP': 'Chevauchement',
        
        # Style
        'OPACITY': 'Opacité',
        'BLUR': 'Flou',
        'COLOR': 'Couleur',
        'SCALE': 'Échelle',
        'ROTATION': 'Rotation',
        
        # Diagnostic
        'DIAGNOSTIC': 'Diagnostic',
        'SYSTEM_TEST': 'Test du Système',
        'CACHE_STATS': 'Statistiques de Cache',
        'PERFORMANCE': 'Performance',
        'VALIDATION': 'Validation',
        
        # Export
        'EXPORT': 'Exporter',
        'IMPORT': 'Importer',
        'BUNDLE': 'Paquet',
        'PRESETS': 'Préréglages',
        
        # Quick Presets
        'BOUNCE': 'Rebond',
        'FADE': 'Fondu',
        'SCALE': 'Échelle',
        'SHAKE': 'Secouer',
        'SLIDE': 'Glisser',
        'TYPE': 'Taper',
        'WAVE': 'Vague'
    }
}

def get_text(key, language=None):
    """Get translated text for the given key and language."""
    if language is None:
        language = get_current_language()
    
    # Get translation dictionary for the language
    lang_dict = TRANSLATIONS.get(language, TRANSLATIONS[DEFAULT_LANGUAGE])
    
    # Return translated text or fallback to English
    return lang_dict.get(key, TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key))

def get_current_language():
    """Get current language setting."""
    try:
        # Try to get from Blender preferences
        import bpy
        if hasattr(bpy.context.preferences, 'view') and hasattr(bpy.context.preferences.view, 'language'):
            return bpy.context.preferences.view.language
    except:
        pass
    
    return DEFAULT_LANGUAGE

def set_language(language):
    """Set the current language."""
    if language in SUPPORTED_LANGUAGES:
        try:
            import bpy
            if hasattr(bpy.context.preferences, 'view') and hasattr(bpy.context.preferences.view, 'language'):
                bpy.context.preferences.view.language = language
        except:
            pass

def get_supported_languages():
    """Get list of supported languages."""
    return SUPPORTED_LANGUAGES.copy()

# === NODE NAMING CONVENTIONS ===
NODE_NAME_SEPARATOR = "_"
CURVE_NODE_PREFIX = "curve"
STAGE_SEPARATOR = "_"

def generate_curve_node_name(base_name: str, stage: str) -> str:
    """Generate normalized curve node name to avoid collisions."""
    # Clean base_name to avoid special characters
    clean_base = "".join(c for c in base_name if c.isalnum() or c in ('_', '-'))
    # Normalize stage name
    normalized_stage = stage.lower().strip()
    # Generate normalized name
    return f"{clean_base}{NODE_NAME_SEPARATOR}{CURVE_NODE_PREFIX}{NODE_NAME_SEPARATOR}{normalized_stage}"

def generate_base_name_from_object(obj) -> str:
    """Generate stable base name from object."""
    if not obj:
        return "default"
    
    # Use object name as base, but clean it
    base_name = obj.name
    # Remove common suffixes that might change
    for suffix in [ROOT_SUFFIX, "_copy", ".001", ".002"]:
        if base_name.endswith(suffix):
            base_name = base_name[:-len(suffix)]
    
    return base_name

# === PROPERTY STRUCTURE VALIDATION ===
REQUIRED_PROPERTY_GROUPS = {
    'timing': ['start_frame', 'end_frame', 'duration', 'overlap'],
    'stages': ['anim_stage_in', 'anim_stage_mid', 'anim_stage_out'],
    'motion': ['scale_x', 'scale_y', 'scale_z', 'rotation_x', 'rotation_y', 'rotation_z'],
    'style': ['opacity', 'blur', 'color'],
    'flags': ['live_preview', 'material_animation_enabled', 'effect_layers_enabled'],
    'amplitude': ['amplitude_scale', 'amplitude_rotation', 'amplitude_position']
}

# === BLENDING CONFIGURATION ===
BLEND_WIDTH = 0.1  # Width of blending zone between stages
BLEND_MODE = 'SMOOTH'  # SMOOTH, LINEAR, EASE_IN_OUT
OVERSHOOT_ENABLED = True  # Allow values > 1 for overshoot effects
OVERSHOOT_LIMIT = 2.0  # Maximum overshoot value

# === AUDIT AND REPAIR FLAGS ===
AUDIT_AUTO_REPAIR = True  # Automatically repair issues found during audit
AUDIT_LOG_DETAILS = True  # Log detailed audit information
AUDIT_VALIDATE_ON_STARTUP = True  # Run audit on addon startup

# === LIVE PREVIEW CONFIGURATION ===
LIVE_PREVIEW_ENABLED = True  # Global live preview toggle
LIVE_PREVIEW_UPDATE_RATE = 0.016  # 60 FPS update rate
LIVE_PREVIEW_FRAME_SKIP = 2  # Skip frames for performance

# === PRESET DIRECTORIES ===
import os
PRESETS_DIR = os.path.join(os.path.dirname(__file__), 'presets')
USER_PRESETS_DIR = os.path.join(os.path.dirname(__file__), 'user_presets')

# === PRESET PRIORITY ENUM ===
from enum import Enum

class PresetPriority(Enum):
    """Priority levels for preset application."""
    QUICK_PRESET = 1
    STAGE_PRESET = 2
    OVERRIDE = 3
