import bpy
from ..properties import TA_LetterAnimProperties

class OBJECT_OT_text_on_curve_toggle(bpy.types.Operator):
    bl_idname = "typeanimator.text_on_curve_toggle"
    bl_label = "Toggle Text on Curve"

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'FONT'

    def execute(self, context):
        text_obj = context.active_object
        props = context.scene.ta_letter_anim_props
        curve_name = f"TA_Curve_{text_obj.name}"
        if props.use_text_on_curve:
            curve = bpy.data.objects.get(curve_name)
            if not curve:
                bpy.ops.curve.primitive_bezier_circle_add()
                curve = context.active_object
                curve.name = curve_name
            curve.scale = (text_obj.data.size,)*3
            if not text_obj.modifiers.get("Curve"):
                mod = text_obj.modifiers.new(name="Curve", type='CURVE')
            else:
                mod = text_obj.modifiers["Curve"]
            mod.object = curve
            if props.use_curve_pivot:
                text_obj.matrix_world.translation = curve.location
        else:
            mod = text_obj.modifiers.get("Curve")
            if mod:
                text_obj.modifiers.remove(mod)
            curve = bpy.data.objects.get(curve_name)
            if curve and not any(m.type=='CURVE' and m.object==curve for ob in bpy.data.objects for m in ob.modifiers):
                bpy.data.objects.remove(curve, do_unlink=True)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(OBJECT_OT_text_on_curve_toggle)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_text_on_curve_toggle)
