"""
Sistema de curvas centralizado para TypeAnimator.
"""

import bpy
import logging
from typing import Dict, List, Any, Optional, Tuple
from .constants import (
    CURVE_NODE_GROUP_NAME, CURVE_NODE_BASE_NAME, FONT_TYPE, LETTER_PROPERTY,
    BLEND_WIDTH, BLEND_MODE, OVERSHOOT_ENABLED, OVERSHOOT_LIMIT,
    AUDIT_AUTO_REPAIR, AUDIT_LOG_DETAILS, NODE_NAME_SEPARATOR, 
    CURVE_NODE_PREFIX, STAGE_SEPARATOR, generate_curve_node_name,
    generate_base_name_from_object
)

logger = logging.getLogger(__name__)

# === ENHANCED CURVE EVALUATION ===

def evaluate_staged_curve(obj, stage: str, t: float, props=None) -> float:
    """Centralized function to evaluate curve for a specific stage with blending."""
    try:
        if props is None:
            props = bpy.context.scene.ta_letter_anim_props
        
        # Get curve node for the stage
        curve_node = get_or_create_curve_node(obj, stage)
        if not curve_node:
            return t  # Fallback to linear
        
        # Evaluate the curve
        result = curve_node.mapping.curves[0].evaluate(t)
        
        # Apply overshoot handling
        if OVERSHOOT_ENABLED:
            result = clamp_with_overshoot(result, OVERSHOOT_LIMIT)
        else:
            result = max(0.0, min(1.0, result))
        
        return result
        
    except Exception as e:
        logger.error(f"Error evaluating staged curve: {e}")
        return t

def evaluate_blended_stages(obj, t: float, props=None) -> Dict[str, float]:
    """Evaluate all stages with blending between them."""
    try:
        if props is None:
            props = bpy.context.scene.ta_letter_anim_props
        
        stages = ['in', 'mid', 'out']
        results = {}
        
        # Calculate stage boundaries
        timing = props.timing
        total_duration = timing.duration
        overlap = timing.overlap
        
        # Calculate stage durations
        stage_duration = total_duration / 3.0
        blend_width = stage_duration * BLEND_WIDTH
        
        for i, stage in enumerate(stages):
            stage_start = i * stage_duration
            stage_end = (i + 1) * stage_duration
            
            # Calculate normalized time for this stage
            if t < stage_start:
                stage_t = 0.0
            elif t > stage_end:
                stage_t = 1.0
            else:
                stage_t = (t - stage_start) / stage_duration
            
            # Evaluate curve for this stage
            curve_value = evaluate_staged_curve(obj, stage, stage_t, props)
            
            # Apply blending
            blend_factor = calculate_blend_factor(t, stage_start, stage_end, blend_width)
            results[stage] = curve_value * blend_factor
        
        return results
        
    except Exception as e:
        logger.error(f"Error evaluating blended stages: {e}")
        return {'in': t, 'mid': t, 'out': t}

def calculate_blend_factor(t: float, stage_start: float, stage_end: float, blend_width: float) -> float:
    """Calculate blending factor between stages."""
    try:
        # Calculate distance from stage boundaries
        dist_to_start = abs(t - stage_start)
        dist_to_end = abs(t - stage_end)
        
        # Calculate blend factors
        if dist_to_start < blend_width:
            # Blending at start
            return smooth_step(1.0 - dist_to_start / blend_width)
        elif dist_to_end < blend_width:
            # Blending at end
            return smooth_step(1.0 - dist_to_end / blend_width)
        else:
            # Full stage
            return 1.0
            
    except Exception as e:
        logger.error(f"Error calculating blend factor: {e}")
        return 1.0

def smooth_step(x: float) -> float:
    """Smooth step function for blending."""
    if x <= 0:
        return 0
    elif x >= 1:
        return 1
    else:
        return x * x * (3 - 2 * x)

def clamp_with_overshoot(value: float, limit: float) -> float:
    """Clamp value with optional overshoot."""
    if OVERSHOOT_ENABLED:
        return max(-limit, min(limit, value))
    else:
        return max(0.0, min(1.0, value))

# === ENHANCED NODE MANAGEMENT ===

def get_or_create_curve_node(obj, stage: str) -> Optional[bpy.types.ShaderNodeRGBCurve]:
    """Get or create curve node with normalized naming."""
    try:
        # --- BLINDAJE: Si obj es string, busca el objeto real ---
        if isinstance(obj, str):
            obj_real = bpy.data.objects.get(obj)
            if obj_real is None:
                logger.error(f"get_or_create_curve_node: No se encontró el objeto '{obj}'")
                return None
            obj = obj_real
        # --- BLINDAJE: Si obj es _PropertyDeferred, aborta ---
        if type(obj).__name__ == '_PropertyDeferred' or obj is None:
            logger.error("get_or_create_curve_node: obj es _PropertyDeferred o None, inicialización incompleta")
            return None
        # Generate normalized node name
        base_name = generate_base_name_from_object(obj)
        node_name = generate_curve_node_name(base_name, stage)
        
        # Get or create node group
        node_group = get_or_create_curve_node_group()
        if not node_group:
            return None
        
        # Get or create node
        if node_name in node_group.nodes:
            node = node_group.nodes[node_name]
            if node.bl_idname == 'ShaderNodeRGBCurve':
                return node  # type: ignore
            return None
        
        # Create new node
        curve_node = node_group.nodes.new('ShaderNodeRGBCurve')
        curve_node.name = node_name
        curve_node.label = f"Curve {stage.upper()}"
        
        # Position node
        curve_node.location = get_node_position(stage)
        
        # Apply default preset for stage
        apply_default_preset(curve_node, stage)
        
        logger.debug(f"Created curve node: {node_name}")
        return curve_node  # type: ignore
        
    except Exception as e:
        logger.error(f"Error creating curve node: {e}")
        return None

def get_node_position(stage: str) -> Tuple[int, int]:
    """Get position for curve node based on stage."""
    positions = {
        'in': (0, 200),
        'mid': (0, 0),
        'out': (0, -200)
    }
    return positions.get(stage.lower(), (0, 0))

def apply_default_preset(curve_node, stage: str):
    """Apply default preset to curve node."""
    try:
        # Clear existing points
        curve = curve_node.mapping.curves[0]
        curve.points.clear()
        
        # Add default points based on stage
        if stage.lower() == 'in':
            # Ease-in curve
            curve.points.new(0.0, 0.0)
            curve.points.new(0.5, 0.25)
            curve.points.new(1.0, 1.0)
        elif stage.lower() == 'mid':
            # Linear curve
            curve.points.new(0.0, 0.0)
            curve.points.new(1.0, 1.0)
        elif stage.lower() == 'out':
            # Ease-out curve
            curve.points.new(0.0, 0.0)
            curve.points.new(0.5, 0.75)
            curve.points.new(1.0, 1.0)
        
        # Set handle types
        for point in curve.points:
            point.handle_type = 'AUTO'
            
    except Exception as e:
        logger.error(f"Error applying default preset: {e}")

# === CURVE COPYING AND UTILITIES ===

def copy_curve_between_stages(obj, source_stage: str, target_stage: str) -> bool:
    """Copy curve from one stage to another."""
    try:
        source_node = get_or_create_curve_node(obj, source_stage)
        target_node = get_or_create_curve_node(obj, target_stage)
        
        if not source_node or not target_node:
            return False
        
        # Copy curve data
        source_curve = source_node.mapping.curves[0]
        target_curve = target_node.mapping.curves[0]
        
        # Clear target curve
        target_curve.points.clear()
        
        # Copy points
        for source_point in source_curve.points:
            target_point = target_curve.points.new(source_point.location[0], source_point.location[1])
            target_point.handle_type = source_point.handle_type
        
        logger.info(f"Copied curve from {source_stage} to {target_stage}")
        return True
        
    except Exception as e:
        logger.error(f"Error copying curve: {e}")
        return False

def reset_all_curves(obj) -> bool:
    """Reset all curves for an object to defaults."""
    try:
        stages = ['in', 'mid', 'out']
        for stage in stages:
            curve_node = get_or_create_curve_node(obj, stage)
            if curve_node:
                apply_default_preset(curve_node, stage)
        
        logger.info(f"Reset all curves for {obj.name}")
        return True
        
    except Exception as e:
        logger.error(f"Error resetting curves: {e}")
        return False

def export_curves_to_json(obj) -> Dict[str, Any]:
    """Export all curves for an object to JSON format."""
    try:
        curves_data = {}
        stages = ['in', 'mid', 'out']
        
        for stage in stages:
            curve_node = get_or_create_curve_node(obj, stage)
            if curve_node:
                curves_data[stage] = serialize_curve(curve_node)
        
        return {
            'object_name': obj.name,
            'base_name': generate_base_name_from_object(obj),
            'curves': curves_data,
            'export_time': bpy.context.scene.frame_current
        }
        
    except Exception as e:
        logger.error(f"Error exporting curves: {e}")
        return {}

def import_curves_from_json(obj, curves_data: Dict[str, Any]) -> bool:
    """Import curves for an object from JSON format."""
    try:
        if 'curves' not in curves_data:
            return False
        
        curves = curves_data['curves']
        stages = ['in', 'mid', 'out']
        
        for stage in stages:
            if stage in curves:
                curve_node = get_or_create_curve_node(obj, stage)
                if curve_node:
                    deserialize_curve(curve_node, curves[stage])
        
        logger.info(f"Imported curves for {obj.name}")
        return True
        
    except Exception as e:
        logger.error(f"Error importing curves: {e}")
        return False

# === AUDIT AND REPAIR SYSTEM ===

def audit_or_repair_curve_nodegroup() -> Dict[str, Any]:
    """Comprehensive audit and repair of curve node groups."""
    try:
        audit_results = {
            'total_objects': 0,
            'valid_objects': 0,
            'repaired_objects': 0,
            'errors': [],
            'warnings': [],
            'details': []
        }
        
        # Audit all objects
        for obj in bpy.data.objects:
            if obj.type == FONT_TYPE or (obj.type == 'MESH' and hasattr(obj, LETTER_PROPERTY)):
                audit_results['total_objects'] += 1
                
                # Check if object has valid curve setup
                is_valid, issues = audit_object_curves(obj)
                
                if is_valid:
                    audit_results['valid_objects'] += 1
                else:
                    audit_results['warnings'].extend(issues)
                    
                    # Repair if auto-repair is enabled
                    if AUDIT_AUTO_REPAIR:
                        if repair_object_curves(obj):
                            audit_results['repaired_objects'] += 1
                            audit_results['details'].append(f"Repaired curves for {obj.name}")
        
        # Log audit results
        if AUDIT_LOG_DETAILS:
            logger.info(f"Curve audit completed: {audit_results['valid_objects']}/{audit_results['total_objects']} valid, {audit_results['repaired_objects']} repaired")
        
        return audit_results
        
    except Exception as e:
        logger.error(f"Error in curve audit: {e}")
        return {'error': str(e)}

def audit_object_curves(obj) -> Tuple[bool, List[str]]:
    """Audit curves for a specific object."""
    try:
        issues = []
        stages = ['in', 'mid', 'out']
        
        for stage in stages:
            curve_node = get_or_create_curve_node(obj, stage)
            if not curve_node:
                issues.append(f"Missing curve node for stage {stage}")
                continue
            
            # Check curve validity
            curve = curve_node.mapping.curves[0]
            if len(curve.points) < 2:
                issues.append(f"Insufficient points in {stage} curve")
            
            # Check for invalid point values
            for point in curve.points:
                if point.location[0] < 0 or point.location[0] > 1:
                    issues.append(f"Invalid X coordinate in {stage} curve")
                if point.location[1] < -OVERSHOOT_LIMIT or point.location[1] > OVERSHOOT_LIMIT:
                    issues.append(f"Invalid Y coordinate in {stage} curve")
        
        return len(issues) == 0, issues
        
    except Exception as e:
        return False, [f"Error auditing curves: {e}"]

def repair_object_curves(obj) -> bool:
    """Repair curves for a specific object."""
    try:
        stages = ['in', 'mid', 'out']
        
        for stage in stages:
            curve_node = get_or_create_curve_node(obj, stage)
            if curve_node:
                # Apply default preset to repair
                apply_default_preset(curve_node, stage)
        
        return True
        
    except Exception as e:
        logger.error(f"Error repairing curves: {e}")
        return False

# === DEBUG AND TESTING ===

def debug_evaluate_curves(obj, test_points: List[float] = None) -> Dict[str, Any]:
    """Debug evaluation of curves at specific points."""
    try:
        if test_points is None:
            test_points = [0.0, 0.5, 1.0]
        
        debug_results = {
            'object_name': obj.name,
            'base_name': generate_base_name_from_object(obj),
            'test_points': test_points,
            'results': {}
        }
        
        stages = ['in', 'mid', 'out']
        
        for stage in stages:
            stage_results = {}
            for t in test_points:
                value = evaluate_staged_curve(obj, stage, t)
                stage_results[f"t={t}"] = value
            debug_results['results'][stage] = stage_results
        
        return debug_results
        
    except Exception as e:
        logger.error(f"Error in curve debug: {e}")
        return {'error': str(e)}

# === LEGACY SUPPORT ===

def serialize_curve(curve_node) -> Dict[str, Any]:
    """Serialize curve data for export."""
    try:
        curve = curve_node.mapping.curves[0]
        points = []
        
        for point in curve.points:
            points.append({
                'x': point.location[0],
                'y': point.location[1],
                'handle_type': point.handle_type
            })
        
        return {
            'points': points,
            'node_name': curve_node.name
        }
        
    except Exception as e:
        logger.error(f"Error serializing curve: {e}")
        return {}

def deserialize_curve(curve_node, curve_data: Dict[str, Any]):
    """Deserialize curve data for import."""
    try:
        curve = curve_node.mapping.curves[0]
        curve.points.clear()
        
        if 'points' in curve_data:
            for point_data in curve_data['points']:
                point = curve.points.new(point_data['x'], point_data['y'])
                point.handle_type = point_data.get('handle_type', 'AUTO')
        
    except Exception as e:
        logger.error(f"Error deserializing curve: {e}")

def get_or_create_curve_node_group():
    """Get or create the main curve node group."""
    try:
        if CURVE_NODE_GROUP_NAME in bpy.data.node_groups:
            return bpy.data.node_groups[CURVE_NODE_GROUP_NAME]
        
        # Create new node group
        node_group = bpy.data.node_groups.new(CURVE_NODE_GROUP_NAME, 'ShaderNodeTree')
        node_group.use_fake_user = True
        
        # Add input and output nodes
        input_node = node_group.nodes.new('NodeGroupInput')
        output_node = node_group.nodes.new('NodeGroupOutput')
        
        # Position nodes
        input_node.location = (-300, 0)
        output_node.location = (300, 0)
        
        logger.info(f"Created curve node group: {CURVE_NODE_GROUP_NAME}")
        return node_group
        
    except Exception as e:
        print(f"[typeanimator] curves.py error: {e}")
        return None
