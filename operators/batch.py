import bpy
from ..properties import TA_LetterAnimProperties

class OBJECT_OT_batch_apply(bpy.types.Operator):
    """Apply animation to a batch of objects"""
    bl_idname = "typeanimator.batch_apply"
    bl_label = "Apply to Batch"

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "ta_letter_anim_props")

    def execute(self, context):
        scene = context.scene
        props: TA_LetterAnimProperties = scene.ta_letter_anim_props
        if props.batch_mode == 'ACTIVE':
            targets = [context.active_object] if context.active_object else []
        else:
            targets = list(context.selected_objects)
        original = props.start_frame
        for idx, obj in enumerate(targets):
            if not props.batch_sync:
                props.start_frame = original + idx * props.batch_offset
            context.view_layer.objects.active = obj
            bpy.ops.typeanimator.apply_all()
        props.start_frame = original
        return {'FINISHED'}

def register():
    bpy.utils.register_class(OBJECT_OT_batch_apply)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_batch_apply)
