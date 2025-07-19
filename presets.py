"""
Advanced preset system for TypeAnimator with enhanced functionality.
"""

import bpy
import json
import os
import logging
from typing import Dict, List, Any, Optional, Tuple
from .constants import PRESETS_DIR, USER_PRESETS_DIR, CURVE_NODE_GROUP_NAME
from .utils import validate_animation_properties

logger = logging.getLogger(__name__)

# === UTILITY FUNCTIONS ===

def safe_json_load(file_obj, filepath):
    """Safely load JSON data from file object."""
    try:
        return json.load(file_obj)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in {filepath}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error loading JSON from {filepath}: {e}")
        return {}

# === PRESET ITEM CLASS ===

class PresetItem(bpy.types.PropertyGroup):
    """Property group for preset items."""
    
    name: bpy.props.StringProperty(
        name="Name",
        description="Preset name",
        default=""
    )
    
    description: bpy.props.StringProperty(
        name="Description", 
        description="Preset description",
        default=""
    )
    
    category: bpy.props.StringProperty(
        name="Category",
        description="Preset category",
        default=""
    )
    
    author: bpy.props.StringProperty(
        name="Author",
        description="Preset author",
        default=""
    )
    
    version: bpy.props.StringProperty(
        name="Version",
        description="Preset version",
        default="1.0"
    )

# === ADVANCED PRESET SYSTEM ===

class AdvancedPresetManager:
    """Advanced preset manager with enhanced functionality."""
    
    def __init__(self):
        self.presets_cache = {}
        self.user_presets = {}
        self.preset_categories = {
            'quick': 'Quick Presets',
            'professional': 'Professional',
            'experimental': 'Experimental',
            'user': 'User Presets',
            'community': 'Community'
        }
        self.load_all_presets()
    
    def load_all_presets(self):
        """Load all presets from various sources."""
        try:
            # Load built-in presets
            self._load_builtin_presets()
            # Load user presets
            self._load_user_presets()
            # Load community presets
            self._load_community_presets()
            logger.info(f"Loaded {len(self.presets_cache)} presets from {len(self.preset_categories)} categories")
            # Mostrar en consola los nombres de presets detectados
            print(f"[TypeAnimator] Presets detectados: {list(self.presets_cache.keys())}")
            print(f"[TypeAnimator] Presets cache: {self.presets_cache}")
            if not self.presets_cache:
                print("[TypeAnimator] ERROR: No presets cargados. Verifica la estructura de los archivos .json en la carpeta presets/")
        except Exception as e:
            logger.error(f"Error loading presets: {e}")
    
    def _load_builtin_presets(self):
        """Load built-in presets from all JSON files in the presets directory."""
        try:
            for filename in os.listdir(PRESETS_DIR):
                if filename.endswith('.json') and not filename.startswith('user_'):
                    filepath = os.path.join(PRESETS_DIR, filename)
                    if os.path.exists(filepath):
                        self._load_preset_file(filepath, 'builtin')
        except Exception as e:
            logger.error(f"Error loading built-in presets: {e}")
    
    def _load_user_presets(self):
        """Load user-created presets."""
        try:
            user_preset_dir = USER_PRESETS_DIR
            if os.path.exists(user_preset_dir):
                for filename in os.listdir(user_preset_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(user_preset_dir, filename)
                        self._load_preset_file(filepath, 'user')
                        
        except Exception as e:
            logger.error(f"Error loading user presets: {e}")
    
    def _load_community_presets(self):
        """Load community-contributed presets."""
        try:
            # This would load from a community repository or shared location
            # For now, we'll create some example community presets
            community_presets = {
                'community_bounce_advanced': {
                    'name': 'Advanced Bounce',
                    'category': 'community',
                    'description': 'Advanced bounce with multiple stages',
                    'author': 'Community',
                    'version': '1.0',
                    'settings': {
                        'timing': {
                            'start_frame': 1,
                            'end_frame': 60,
                            'duration': 30,
                            'overlap': 0.2
                        },
                        'motion': {
                            'scale_x': 1.2,
                            'scale_y': 1.2,
                            'scale_z': 1.2,
                            'rotation_x': 0.1,
                            'rotation_y': 0.1,
                            'rotation_z': 0.1
                        },
                        'style': {
                            'opacity': 1.0,
                            'blur': 0.0,
                            'color': (1.0, 1.0, 1.0, 1.0)
                        }
                    }
                }
            }
            
            self.presets_cache.update(community_presets)
            
        except Exception as e:
            logger.error(f"Error loading community presets: {e}")
    
    def _load_preset_file(self, filepath: str, category: str):
        """Load presets from a JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Process presets and add category information
            is_animation_file = os.path.basename(filepath) == 'animations.json'
            field_map = {'len': 'duration', 'overlap_frames': 'overlap'}
            for preset_id, preset_data in data.items():
                if isinstance(preset_data, dict):
                    preset_data['category'] = category
                    preset_data['filepath'] = filepath
                    if is_animation_file:
                        preset_data['subtype'] = 'animation'
                    # Normalizar claves
                    for old, new in field_map.items():
                        if old in preset_data and new not in preset_data:
                            preset_data[new] = preset_data[old]
                    # Validar y poner defaults
                    if 'duration' not in preset_data:
                        preset_data['duration'] = 50
                        logger.warning(f"Preset {preset_id} missing 'duration', set to default 50")
                    if 'overlap' not in preset_data:
                        preset_data['overlap'] = 5
                        logger.warning(f"Preset {preset_id} missing 'overlap', set to default 5")
                    self.presets_cache[preset_id] = preset_data
                    
        except Exception as e:
            logger.error(f"Error loading preset file {filepath}: {e}")
    
    def get_preset(self, preset_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific preset by ID."""
        return self.presets_cache.get(preset_id)
    
    def get_presets_by_category(self, category: str) -> Dict[str, Any]:
        """Get all presets in a specific category."""
        return {
            preset_id: preset_data 
            for preset_id, preset_data in self.presets_cache.items()
            if preset_data.get('category') == category
        }
    
    def get_all_presets(self) -> Dict[str, Any]:
        """Get all available presets."""
        return self.presets_cache.copy()
    
    def create_user_preset(self, name: str, description: str, settings: Dict[str, Any]) -> str:
        """Create a new user preset."""
        try:
            preset_id = f"user_{name.lower().replace(' ', '_')}"
            
            preset_data = {
                'name': name,
                'description': description,
                'category': 'user',
                'author': 'User',
                'version': '1.0',
                'created': bpy.context.scene.frame_current,
                'settings': settings
            }
            
            # Save to user presets directory
            self._save_user_preset(preset_id, preset_data)
            
            # Add to cache
            self.presets_cache[preset_id] = preset_data
            
            logger.info(f"Created user preset: {preset_id}")
            return preset_id
            
        except Exception as e:
            logger.error(f"Error creating user preset: {e}")
            return None
    
    def _save_user_preset(self, preset_id: str, preset_data: Dict[str, Any]):
        """Save a user preset to file."""
        try:
            if not os.path.exists(USER_PRESETS_DIR):
                os.makedirs(USER_PRESETS_DIR)
            
            filepath = os.path.join(USER_PRESETS_DIR, f"{preset_id}.json")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({preset_id: preset_data}, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error saving user preset: {e}")
    
    def delete_user_preset(self, preset_id: str) -> bool:
        """Delete a user preset."""
        try:
            if preset_id in self.presets_cache:
                preset_data = self.presets_cache[preset_id]
                
                # Remove from cache
                del self.presets_cache[preset_id]
                
                # Remove file
                filepath = os.path.join(USER_PRESETS_DIR, f"{preset_id}.json")
                if os.path.exists(filepath):
                    os.remove(filepath)
                
                logger.info(f"Deleted user preset: {preset_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting user preset: {e}")
        
        return False
    
    def export_preset_bundle(self, preset_ids: List[str], filepath: str) -> bool:
        """Export a bundle of presets."""
        try:
            bundle_data = {
                'metadata': {
                    'name': 'TypeAnimator Preset Bundle',
                    'version': '1.0',
                    'created': bpy.context.scene.frame_current,
                    'preset_count': len(preset_ids)
                },
                'presets': {}
            }
            
            for preset_id in preset_ids:
                if preset_id in self.presets_cache:
                    bundle_data['presets'][preset_id] = self.presets_cache[preset_id]
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(bundle_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported preset bundle: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting preset bundle: {e}")
            return False
    
    def import_preset_bundle(self, filepath: str) -> bool:
        """Import a preset bundle."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                bundle_data = json.load(f)
            
            imported_count = 0
            for preset_id, preset_data in bundle_data.get('presets', {}).items():
                if preset_id not in self.presets_cache:
                    self.presets_cache[preset_id] = preset_data
                    imported_count += 1
            
            logger.info(f"Imported {imported_count} presets from bundle: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing preset bundle: {e}")
            return False
    
    def validate_preset(self, preset_id: str) -> Tuple[bool, List[str]]:
        """Validate a preset's settings."""
        errors = []
        
        try:
            preset_data = self.get_preset(preset_id)
            if not preset_data:
                errors.append(f"Preset {preset_id} not found")
                return False, errors
            
            settings = preset_data.get('settings', {})
            
            # Validate timing settings
            timing = settings.get('timing', {})
            if not self._validate_timing(timing):
                errors.append("Invalid timing settings")
            
            # Validate motion settings
            motion = settings.get('motion', {})
            if not self._validate_motion(motion):
                errors.append("Invalid motion settings")
            
            # Validate style settings
            style = settings.get('style', {})
            if not self._validate_style(style):
                errors.append("Invalid style settings")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Validation error: {e}")
            return False, errors
    
    def _validate_timing(self, timing: Dict[str, Any]) -> bool:
        """Validate timing settings."""
        try:
            required_fields = ['start_frame', 'end_frame', 'duration']
            for field in required_fields:
                if field not in timing:
                    return False
            
            start_frame = timing['start_frame']
            end_frame = timing['end_frame']
            duration = timing['duration']
            
            if not (isinstance(start_frame, (int, float)) and 
                   isinstance(end_frame, (int, float)) and 
                   isinstance(duration, (int, float))):
                return False
            
            if start_frame < 0 or end_frame < start_frame or duration <= 0:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _validate_motion(self, motion: Dict[str, Any]) -> bool:
        """Validate motion settings."""
        try:
            motion_fields = ['scale_x', 'scale_y', 'scale_z', 'rotation_x', 'rotation_y', 'rotation_z']
            
            for field in motion_fields:
                if field in motion:
                    value = motion[field]
                    if not isinstance(value, (int, float)):
                        return False
            
            return True
            
        except Exception:
            return False
    
    def _validate_style(self, style: Dict[str, Any]) -> bool:
        """Validate style settings."""
        try:
            if 'opacity' in style:
                opacity = style['opacity']
                if not isinstance(opacity, (int, float)) or opacity < 0 or opacity > 1:
                    return False
            
            if 'blur' in style:
                blur = style['blur']
                if not isinstance(blur, (int, float)) or blur < 0:
                    return False
            
            if 'color' in style:
                color = style['color']
                if not isinstance(color, (list, tuple)) or len(color) != 4:
                    return False
                
                for component in color:
                    if not isinstance(component, (int, float)) or component < 0 or component > 1:
                        return False
            
            return True
            
        except Exception:
            return False
    
    def get_preset_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded presets."""
        try:
            stats = {
                'total_presets': len(self.presets_cache),
                'categories': {},
                'validation': {
                    'valid': 0,
                    'invalid': 0,
                    'errors': []
                }
            }
            
            # Count by category
            for preset_id, preset_data in self.presets_cache.items():
                category = preset_data.get('category', 'unknown')
                stats['categories'][category] = stats['categories'].get(category, 0) + 1
            
            # Validate all presets
            for preset_id in self.presets_cache.keys():
                is_valid, errors = self.validate_preset(preset_id)
                if is_valid:
                    stats['validation']['valid'] += 1
                else:
                    stats['validation']['invalid'] += 1
                    stats['validation']['errors'].extend(errors)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting preset statistics: {e}")
            return {}

# Global preset manager instance
_preset_manager = AdvancedPresetManager()

# === PUBLIC API ===

def load_all_presets():
    """Load all presets."""
    return _preset_manager.load_all_presets()

def get_preset(preset_id: str):
    """Get a specific preset."""
    return _preset_manager.get_preset(preset_id)

def get_presets_by_category(category: str):
    """Get presets by category."""
    return _preset_manager.get_presets_by_category(category)

def get_all_presets():
    """Get all presets."""
    return _preset_manager.get_all_presets()

def create_user_preset(name: str, description: str, settings: Dict[str, Any]):
    """Create a new user preset."""
    return _preset_manager.create_user_preset(name, description, settings)

def delete_user_preset(preset_id: str):
    """Delete a user preset."""
    return _preset_manager.delete_user_preset(preset_id)

def export_preset_bundle(preset_ids: List[str], filepath: str):
    """Export a preset bundle."""
    return _preset_manager.export_preset_bundle(preset_ids, filepath)

def import_preset_bundle(filepath: str):
    """Import a preset bundle."""
    return _preset_manager.import_preset_bundle(filepath)

def validate_preset(preset_id: str):
    """Validate a preset."""
    return _preset_manager.validate_preset(preset_id)

def get_preset_statistics():
    """Get preset statistics."""
    return _preset_manager.get_preset_statistics()

# === LEGACY SUPPORT ===

def load_presets():
    """Legacy function for loading presets."""
    return load_all_presets()

def get_preset_data():
    """Get all preset data."""
    return _preset_manager.get_all_presets()

def load_stage_presets():
    """Load stage-specific presets."""
    try:
        # Initialize preset manager if needed
        if not hasattr(presets, '_preset_manager'):
            presets._preset_manager = AdvancedPresetManager()
        logger.info("Stage presets loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Error loading stage presets: {e}")
        return False

# === REGISTRATION FUNCTIONS ===

def register():
    """Register preset classes."""
    try:
        bpy.utils.register_class(PresetItem)
        logger.info("PresetItem registered successfully")
    except Exception as e:
        logger.error(f"Error registering PresetItem: {e}")

def unregister():
    """Unregister preset classes."""
    try:
        bpy.utils.unregister_class(PresetItem)
        logger.info("PresetItem unregistered successfully")
    except Exception as e:
        logger.error(f"Error unregistering PresetItem: {e}")
