import bpy

def register():
    bpy.utils.register_class(TYPEANIMATOR_OT_force_init_properties)

def unregister():
    bpy.utils.unregister_class(TYPEANIMATOR_OT_force_init_properties)

class TYPEANIMATOR_OT_force_init_properties(bpy.types.Operator):
    """Force initialization of TypeAnimator properties"""
    bl_idname = "typeanimator.force_init_properties"
    bl_label = "Force Init Properties"
    bl_description = "Force initialization of TypeAnimator properties"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            # Forzar inicialización de propiedades
            if hasattr(context.scene, 'ta_letter_anim_props'):
                props = context.scene.ta_letter_anim_props
                # Intentar acceder a todas las propiedades principales para forzar inicialización
                _ = props.timing
                _ = props.style
                _ = props.preview
                _ = props.stages
                # Forzar actualización de enums
                from .. import properties
                properties.update_preset_enums()
                properties.update_anim_preset_enum()
                self.report({'INFO'}, "Propiedades inicializadas correctamente")
                # Refrescar UI
                for area in context.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "ta_letter_anim_props no encontrado en Scene")
                return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error inicializando propiedades: {e}")
            return {'CANCELLED'}