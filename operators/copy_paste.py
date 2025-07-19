import bpy
from .. import preset_manager

class OBJECT_OT_copy_settings(bpy.types.Operator):
    bl_idname = "typeanimator.copy_settings_clip"
    bl_label = "Copy Settings"

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "ta_letter_anim_props")

    def execute(self, context):
        props = context.scene.ta_letter_anim_props
        data = preset_manager._props_to_dict(props)
        context.window_manager.ta_clipboard = data
        return {'FINISHED'}

class OBJECT_OT_paste_settings(bpy.types.Operator):
    bl_idname = "typeanimator.paste_settings_clip"
    bl_label = "Paste Settings"

    @classmethod
    def poll(cls, context):
        return hasattr(context.window_manager, "ta_clipboard") and bool(getattr(context.window_manager, 'ta_clipboard', None))

    def execute(self, context):
        data = context.window_manager.ta_clipboard
        props = context.scene.ta_letter_anim_props
        if data:
            preset_manager._dict_to_props(data, props)
        return {'FINISHED'}

def register():
    bpy.types.WindowManager.ta_clipboard = None
    bpy.utils.register_class(OBJECT_OT_copy_settings)
    bpy.utils.register_class(OBJECT_OT_paste_settings)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_paste_settings)
    bpy.utils.unregister_class(OBJECT_OT_copy_settings)
    if hasattr(bpy.types.WindowManager, 'ta_clipboard'):
        del bpy.types.WindowManager.ta_clipboard
