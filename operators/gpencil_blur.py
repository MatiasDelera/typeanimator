import bpy
from ..properties import TA_LetterAnimProperties

class OBJECT_OT_convert_gpencil_blur(bpy.types.Operator):
    bl_idname = "typeanimator.convert_gpencil_blur"
    bl_label = "Convert to GPencil + Blur"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        props = context.scene.ta_letter_anim_props
        bpy.ops.object.convert(target='GPENCIL')
        new_obj = context.active_object
        mod = new_obj.grease_pencil_modifiers.new(name="GPencilBlur", type='GPENCIL_BLUR')
        mod.blur_amount = props.gpencil_blur_radius
        mod.iterations = props.gpencil_blur_iterations
        return {'FINISHED'}

def register():
    bpy.utils.register_class(OBJECT_OT_convert_gpencil_blur)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_convert_gpencil_blur)
