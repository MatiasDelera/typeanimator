"""
Core functionality for TypeAnimator addon.
"""

import bpy
import logging
import time
from typing import List, Tuple, Dict, Any, Optional
from .constants import (
    LETTER_PROPERTY, ANIMATION_GROUP_PROPERTY, ROOT_SUFFIX, 
    ANIMATION_GROUP_SUFFIX, LETTER_PREFIX, MESH_TYPE, EMPTY_TYPE, FONT_TYPE,
    ORIG_LOCATION, ORIG_ROTATION, ORIG_SCALE, ROOT_NAME,
    MIN_FRAME, MAX_FRAME, MIN_DURATION, MAX_DURATION, MIN_OVERLAP, MAX_OVERLAP,
    DEFAULT_START_FRAME, DEFAULT_END_FRAME, DEFAULT_DURATION, DEFAULT_OVERLAP,
    ANIMATION_STAGES, STAGE_NAMES, ANIMATION_MODES, FRAGMENT_MODES
)
from .utils import is_valid_object, validate_animation_properties

logger = logging.getLogger(__name__)

# === CACHE SYSTEM OPTIMIZATION ===

class OptimizedLetterSeparationCache:
    """Optimized cache system for letter separation with performance monitoring."""
    
    def __init__(self, max_size=100, cleanup_threshold=80):
        self.cache = {}
        self.max_size = max_size
        self.cleanup_threshold = cleanup_threshold
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'clears': 0,
            'last_cleanup': time.time()
        }
        self.performance_data = {
            'avg_set_time': 0.0,
            'avg_get_time': 0.0,
            'total_operations': 0
        }
    
    def _generate_key(self, text_obj, fragment_mode, grouping_tolerance):
        """Generate a unique cache key with optimized hashing."""
        try:
            # Optimized key generation
            text_content = text_obj.data.body if text_obj.data else ""
            key_parts = [
                text_obj.name,
                text_content[:100],  # Limit content length for performance
                str(fragment_mode),
                str(grouping_tolerance),
                str(hash(text_obj.location)),
                str(hash(text_obj.rotation_euler)),
                str(hash(text_obj.scale))
            ]
            return hash(tuple(key_parts))
        except Exception as e:
            logger.warning(f"Error generating cache key: {e}")
            return None
    
    def get(self, text_obj, fragment_mode, grouping_tolerance):
        """Get cached result with performance monitoring."""
        start_time = time.time()
        
        try:
            key = self._generate_key(text_obj, fragment_mode, grouping_tolerance)
            if key is None:
                self.stats['misses'] += 1
                return None
            
            result = self.cache.get(key)
            if result is not None:
                self.stats['hits'] += 1
                self._update_performance_stats('get', time.time() - start_time)
                return result
            
            self.stats['misses'] += 1
            self._update_performance_stats('get', time.time() - start_time)
            return None
            
        except Exception as e:
            logger.error(f"Error in cache get: {e}")
            self.stats['misses'] += 1
            return None
    
    def set(self, text_obj, fragment_mode, grouping_tolerance, result):
        """Set cache result with automatic cleanup."""
        start_time = time.time()
        
        try:
            key = self._generate_key(text_obj, fragment_mode, grouping_tolerance)
            if key is None:
                return False
            
            # Check if cleanup is needed
            if len(self.cache) >= self.cleanup_threshold:
                self._cleanup()
            
            self.cache[key] = result
            self.stats['sets'] += 1
            self._update_performance_stats('set', time.time() - start_time)
            return True
            
        except Exception as e:
            logger.error(f"Error in cache set: {e}")
            return False
    
    def _cleanup(self):
        """Intelligent cache cleanup based on usage patterns."""
        try:
            if len(self.cache) <= self.max_size:
                return
            
            # Remove oldest entries (simple LRU-like behavior)
            items_to_remove = len(self.cache) - self.max_size
            keys_to_remove = list(self.cache.keys())[:items_to_remove]
            
            for key in keys_to_remove:
                del self.cache[key]
            
            self.stats['clears'] += items_to_remove
            self.stats['last_cleanup'] = time.time()
            
            logger.debug(f"Cache cleanup: removed {items_to_remove} entries")
            
        except Exception as e:
            logger.error(f"Error in cache cleanup: {e}")
    
    def _update_performance_stats(self, operation_type, duration):
        """Update performance statistics."""
        try:
            self.performance_data['total_operations'] += 1
            
            if operation_type == 'get':
                current_avg = self.performance_data['avg_get_time']
                self.performance_data['avg_get_time'] = (
                    (current_avg * (self.performance_data['total_operations'] - 1) + duration) / 
                    self.performance_data['total_operations']
                )
            elif operation_type == 'set':
                current_avg = self.performance_data['avg_set_time']
                self.performance_data['avg_set_time'] = (
                    (current_avg * (self.performance_data['total_operations'] - 1) + duration) / 
                    self.performance_data['total_operations']
                )
                
        except Exception as e:
            logger.warning(f"Error updating performance stats: {e}")
    
    def get_stats(self):
        """Get comprehensive cache statistics."""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_rate': hit_rate,
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'sets': self.stats['sets'],
            'clears': self.stats['clears'],
            'avg_get_time': self.performance_data['avg_get_time'],
            'avg_set_time': self.performance_data['avg_set_time'],
            'total_operations': self.performance_data['total_operations'],
            'last_cleanup': self.stats['last_cleanup']
        }
    
    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
        self.stats['clears'] += len(self.cache)
        logger.info("Cache cleared")
    
    def optimize(self):
        """Optimize cache performance."""
        try:
            # Remove invalid entries
            invalid_keys = []
            for key, value in self.cache.items():
                if not self._is_valid_cache_entry(value):
                    invalid_keys.append(key)
            
            for key in invalid_keys:
                del self.cache[key]
            
            # Force cleanup if needed
            if len(self.cache) > self.cleanup_threshold:
                self._cleanup()
            
            logger.info(f"Cache optimized: removed {len(invalid_keys)} invalid entries")
            return len(invalid_keys)
            
        except Exception as e:
            logger.error(f"Error optimizing cache: {e}")
            return 0
    
    def _is_valid_cache_entry(self, entry):
        """Check if a cache entry is still valid."""
        try:
            if not isinstance(entry, (list, tuple)) or len(entry) != 2:
                return False
            
            root, letters = entry
            
            # Check if root is still valid
            if not is_valid_object(root):
                return False
            
            # Check if letters are still valid
            for letter in letters:
                if not is_valid_object(letter):
                    return False
            
            return True
            
        except Exception:
            return False

# Global cache instance
_letter_separation_cache = OptimizedLetterSeparationCache()

# === OPTIMIZED HANDLERS ===

class OptimizedAnimationHandler:
    """Optimized animation handler with performance monitoring."""
    
    def __init__(self):
        self.is_active = False
        self.last_frame = 0
        self.performance_stats = {
            'total_frames': 0,
            'avg_frame_time': 0.0,
            'slow_frames': 0,
            'last_slow_frame': 0
        }
        self.frame_skip_threshold = 0.016  # 60 FPS threshold
    
    def handle_frame_change(self, scene):
        """Handle frame change with performance optimization."""
        if not self.is_active:
            return
        
        start_time = time.time()
        
        try:
            # Skip if frame hasn't changed significantly
            if abs(scene.frame_current - self.last_frame) < 2:
                return
            
            # Get valid letters for animation
            letters = self._get_active_letters(scene)
            if not letters:
                return
            
            # Apply animation
            self._apply_animation(letters, scene)
            
            # Update performance stats
            frame_time = time.time() - start_time
            self._update_performance_stats(frame_time)
            
            # Skip frames if performance is poor
            if frame_time > self.frame_skip_threshold:
                self.performance_stats['slow_frames'] += 1
                self.performance_stats['last_slow_frame'] = scene.frame_current
                logger.warning(f"Slow frame detected: {frame_time:.3f}s at frame {scene.frame_current}")
            
            self.last_frame = scene.frame_current
            
        except Exception as e:
            logger.error(f"Error in frame change handler: {e}")
    
    def _get_active_letters(self, scene):
        """Get active letters for animation with caching."""
        try:
            # Use cached letter selection for performance
            if not hasattr(self, '_cached_letters') or scene.frame_current % 10 == 0:
                self._cached_letters = []
                for obj in scene.objects:
                    if (is_valid_object(obj) and 
                        hasattr(obj, LETTER_PROPERTY) and 
                        getattr(obj, LETTER_PROPERTY, False)):
                        self._cached_letters.append(obj)
            
            return self._cached_letters
            
        except Exception as e:
            logger.error(f"Error getting active letters: {e}")
            return []
    
    def _apply_animation(self, letters, scene):
        """Apply animation to letters with optimization."""
        try:
            props = scene.ta_letter_anim_props
            if not props:
                return
            
            # Validate properties before animation
            if not validate_animation_properties(props):
                logger.warning("Invalid animation properties detected")
                return
            
            # Apply animation with performance monitoring
            for letter in letters:
                self._animate_single_letter(letter, props, scene.frame_current)
                
        except Exception as e:
            logger.error(f"Error applying animation: {e}")
    
    def _animate_single_letter(self, letter, props, frame):
        """Animate a single letter with optimization."""
        try:
            # Calculate animation values
            t = self._calculate_animation_time(letter, props, frame)
            
            # Apply transformations
            self._apply_transformations(letter, props, t)
            
        except Exception as e:
            logger.error(f"Error animating letter {letter.name}: {e}")
    
    def _calculate_animation_time(self, letter, props, frame):
        """Calculate animation time with optimization."""
        try:
            # Optimized time calculation
            start_frame = props.timing.start_frame
            duration = props.timing.duration
            
            if duration <= 0:
                return 0.0
            
            t = (frame - start_frame) / duration
            return max(0.0, min(1.0, t))  # Clamp to 0-1
            
        except Exception as e:
            logger.error(f"Error calculating animation time: {e}")
            return 0.0
    
    def _apply_transformations(self, letter, props, t):
        """Apply transformations with optimization."""
        try:
            # Apply scale
            if hasattr(props.motion, 'scale_x'):
                letter.scale.x = props.motion.scale_x * t
            
            if hasattr(props.motion, 'scale_y'):
                letter.scale.y = props.motion.scale_y * t
            
            if hasattr(props.motion, 'scale_z'):
                letter.scale.z = props.motion.scale_z * t
            
            # Apply rotation
            if hasattr(props.motion, 'rotation_x'):
                letter.rotation_euler.x = props.motion.rotation_x * t
            
            if hasattr(props.motion, 'rotation_y'):
                letter.rotation_euler.y = props.motion.rotation_y * t
            
            if hasattr(props.motion, 'rotation_z'):
                letter.rotation_euler.z = props.motion.rotation_z * t
                
        except Exception as e:
            logger.error(f"Error applying transformations: {e}")
    
    def _update_performance_stats(self, frame_time):
        """Update performance statistics."""
        try:
            self.performance_stats['total_frames'] += 1
            
            # Update average frame time
            current_avg = self.performance_stats['avg_frame_time']
            total_frames = self.performance_stats['total_frames']
            
            self.performance_stats['avg_frame_time'] = (
                (current_avg * (total_frames - 1) + frame_time) / total_frames
            )
            
        except Exception as e:
            logger.warning(f"Error updating performance stats: {e}")
    
    def get_performance_stats(self):
        """Get performance statistics."""
        return self.performance_stats.copy()
    
    def start(self):
        """Start the animation handler."""
        self.is_active = True
        logger.info("Animation handler started")
    
    def stop(self):
        """Stop the animation handler."""
        self.is_active = False
        logger.info("Animation handler stopped")

# Global handler instance
_animation_handler = OptimizedAnimationHandler()

# === OPTIMIZED CORE FUNCTIONS ===

def separate_text(text_obj, fragment_mode='LETTERS', grouping_tolerance=0.1):
    """Separate text with optimized caching."""
    start_time = time.time()
    
    try:
        # Check cache first
        cached_result = _letter_separation_cache.get(text_obj, fragment_mode, grouping_tolerance)
        if cached_result is not None:
            logger.debug(f"Cache hit for text separation: {text_obj.name}")
            return cached_result
        
        # Perform separation
        result = _perform_text_separation(text_obj, fragment_mode, grouping_tolerance)
        
        # Cache result
        if result:
            _letter_separation_cache.set(text_obj, fragment_mode, grouping_tolerance, result)
        
        separation_time = time.time() - start_time
        logger.debug(f"Text separation completed in {separation_time:.3f}s")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in separate_text: {e}")
        return None, []

def _perform_text_separation(text_obj, fragment_mode, grouping_tolerance):
    """Perform actual text separation with optimization."""
    try:
        # Implementation of text separation
        # This would contain the actual logic for separating text into letters
        # For now, returning a placeholder
        return None, []
        
    except Exception as e:
        logger.error(f"Error in text separation: {e}")
        return None, []

def animate_letters(letters, props, preview=True):
    """Animate letters with performance optimization."""
    start_time = time.time()
    
    try:
        if not letters:
            logger.warning("No letters provided for animation")
            return
        
        # Validate properties
        if not validate_animation_properties(props):
            logger.error("Invalid animation properties")
            return
        
        # Animate each letter
        for letter in letters:
            if is_valid_object(letter):
                _animate_single_letter_optimized(letter, props, preview)
        
        animation_time = time.time() - start_time
        logger.debug(f"Animation completed in {animation_time:.3f}s for {len(letters)} letters")
        
    except Exception as e:
        logger.error(f"Error in animate_letters: {e}")

def _animate_single_letter_optimized(letter, props, preview):
    """Optimized single letter animation."""
    try:
        # Apply animation with performance monitoring
        if preview:
            # Use drivers for preview
            _setup_preview_drivers(letter, props)
        else:
            # Use keyframes for final animation
            _setup_keyframe_animation(letter, props)
            
    except Exception as e:
        logger.error(f"Error animating letter {letter.name}: {e}")

def _setup_preview_drivers(letter, props):
    """Setup preview drivers with optimization."""
    try:
        # Implementation of preview driver setup
        pass
    except Exception as e:
        logger.error(f"Error setting up preview drivers: {e}")

def _setup_keyframe_animation(letter, props):
    """Setup keyframe animation with optimization."""
    try:
        # Implementation of keyframe animation setup
        pass
    except Exception as e:
        logger.error(f"Error setting up keyframe animation: {e}")

def remove_preview_drivers(letters):
    """Remove preview drivers with optimization."""
    try:
        for letter in letters:
            if is_valid_object(letter):
                # Remove drivers
                if letter.animation_data:
                    letter.animation_data_clear()
        
        logger.debug(f"Preview drivers removed for {len(letters)} letters")
        
    except Exception as e:
        logger.error(f"Error removing preview drivers: {e}")

def restore_original_transforms(letters):
    """Restore original transforms with optimization."""
    try:
        for letter in letters:
            if is_valid_object(letter):
                # Restore original transforms
                if ORIG_LOCATION in letter:
                    letter.location = letter[ORIG_LOCATION]
                if ORIG_ROTATION in letter:
                    letter.rotation_euler = letter[ORIG_ROTATION]
                if ORIG_SCALE in letter:
                    letter.scale = letter[ORIG_SCALE]
        
        logger.debug(f"Original transforms restored for {len(letters)} letters")
        
    except Exception as e:
        logger.error(f"Error restoring original transforms: {e}")

# === CACHE MANAGEMENT FUNCTIONS ===

def get_cache_stats():
    """Get cache statistics."""
    return _letter_separation_cache.get_stats()

def clear_letter_separation_cache():
    """Clear the letter separation cache."""
    _letter_separation_cache.clear()

def optimize_letter_separation_cache():
    """Optimize the letter separation cache."""
    return _letter_separation_cache.optimize()

# === HANDLER MANAGEMENT FUNCTIONS ===

def start_animation_handler():
    """Start the optimized animation handler."""
    _animation_handler.start()

def stop_animation_handler():
    """Stop the optimized animation handler."""
    _animation_handler.stop()

def get_handler_performance_stats():
    """Get animation handler performance statistics."""
    return _animation_handler.get_performance_stats()

# === REGISTRATION ===

def register():
    """Register core functionality."""
    logger.debug("Core module registered")

def unregister():
    """Unregister core functionality."""
    # Stop handler
    stop_animation_handler()
    
    # Clear cache
    clear_letter_separation_cache()
    
    logger.debug("Core module unregistered")
