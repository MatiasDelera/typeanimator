import bpy

class TAAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = "typeanimator"

    remember_settings: bpy.props.BoolProperty(
        name="Remember last settings on startup",
        description="Recargar los últimos ajustes al iniciar",
        default=False,
    )
    user_presets_dir: bpy.props.StringProperty(
        name="User Presets Folder",
        description="Directorio para exportar e importar presets personalizados",
        subtype='DIR_PATH',
        default="",
    )
    show_debug_panel: bpy.props.BoolProperty(
        name="Mostrar panel de desarrollo (Debug)",
        description="Muestra el panel de debug y herramientas avanzadas en la UI",
        default=False,
    )
    log_level: bpy.props.EnumProperty(
        name="Nivel de Logging",
        description="Nivel de detalle para los logs del addon",
        items=[
            ('DEBUG', 'Debug', 'Máximo detalle para desarrollo'),
            ('INFO', 'Info', 'Información general y errores'),
            ('WARNING', 'Warning', 'Solo advertencias y errores'),
            ('ERROR', 'Error', 'Solo errores críticos'),
        ],
        default='INFO',
    )
    enable_file_logging: bpy.props.BoolProperty(
        name="Logging a Archivo",
        description="Guardar logs en archivo para debugging",
        default=True,
    )
    enable_console_logging: bpy.props.BoolProperty(
        name="Logging a Consola",
        description="Mostrar logs en la consola de Blender",
        default=True,
    )

    def draw(self, context):
        layout = self.layout
        
        # Sección de configuración general
        box = layout.box()
        box.label(text="Configuración General", icon='SETTINGS')
        box.prop(self, "remember_settings")
        box.prop(self, "user_presets_dir")
        box.prop(self, "show_debug_panel")
        
        # Sección de logging
        box = layout.box()
        box.label(text="Sistema de Logging", icon='CONSOLE')
        box.prop(self, "log_level")
        box.prop(self, "enable_file_logging")
        box.prop(self, "enable_console_logging")
        
        # Botones de acción para logging
        row = box.row()
        row.operator("typeanimator.clear_log_file", text="Limpiar Log", icon='TRASH')
        row.operator("typeanimator.open_log_file", text="Abrir Log", icon='FILE_FOLDER') 
