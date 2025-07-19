from pathlib import Path
import bpy
import logging

logger = logging.getLogger(__name__)

# === PROPERTY CLASSES ===

class FavoriteFontItem(bpy.types.PropertyGroup):
    """Property group for favorite font items."""
    path: bpy.props.StringProperty(
        name="Font Path",
        description="Path to the font file",
        subtype='FILE_PATH'
    )

class FontManagerProperties(bpy.types.PropertyGroup):
    """Property group for font manager settings."""
    font_path: bpy.props.StringProperty(
        name="Font Path",
        description="Path to the font file",
        subtype='FILE_PATH'
    )
    
    preview_text: bpy.props.StringProperty(
        name="Preview Text",
        description="Text to use for font preview",
        default="AaBbCc"
    )
    
    font_search: bpy.props.StringProperty(
        name="Search Fonts",
        description="Search for fonts by name",
        default=""
    )
    
    favorites: bpy.props.CollectionProperty(type=FavoriteFontItem)
    active_favorite: bpy.props.IntProperty()

# === UTILITY FUNCTIONS ===

def load_font(font_path):
    """Load a font from the given path."""
    try:
        font = bpy.data.fonts.load(font_path)
        return font
    except Exception as e:
        logger.error(f"Failed to load font {font_path}: {e}")
        raise

# === OPERATORS ===

class FONTMANAGER_OT_add_favorite(bpy.types.Operator):
    bl_idname = "typeanimator.add_favorite_font"
    bl_label = "Add Favorite"
    bl_description = "Add the current font to your favorites list"

    def execute(self, context):
        props = context.scene.font_manager_props
        if not props.font_path:
            self.report({'ERROR'}, "Set a font path first")
            return {'CANCELLED'}

        item = props.favorites.add()
        item.path = props.font_path
        props.active_favorite = len(props.favorites) - 1
        self.report({'INFO'}, f"Added '{Path(props.font_path).name}' to favorites")
        return {'FINISHED'}

class FONTMANAGER_OT_remove_favorite(bpy.types.Operator):
    bl_idname = "typeanimator.remove_favorite_font"
    bl_label = "Remove Favorite"
    bl_description = "Remove the selected font from your favorites list"

    def execute(self, context):
        props = context.scene.font_manager_props
        idx = props.active_favorite
        if 0 <= idx < len(props.favorites):
            removed_name = Path(props.favorites[idx].path).name
            props.favorites.remove(idx)
            props.active_favorite = max(0, idx - 1)
            self.report({'INFO'}, f"Removed '{removed_name}' from favorites")
        return {'FINISHED'}

class FONTMANAGER_OT_use_favorite(bpy.types.Operator):
    bl_idname = "typeanimator.use_favorite_font"
    bl_label = "Use Favorite"
    bl_description = "Use the selected favorite font"

    def execute(self, context):
        props = context.scene.font_manager_props
        idx = props.active_favorite
        if 0 <= idx < len(props.favorites):
            props.font_path = props.favorites[idx].path
            self.report({'INFO'}, f"Set font to '{Path(props.font_path).name}'")
        return {'FINISHED'}

class FONTMANAGER_OT_use_system_font(bpy.types.Operator):
    bl_idname = "typeanimator.use_system_font"
    bl_label = "Use Font"
    bl_description = "Usar la fuente seleccionada"

    font_name: bpy.props.StringProperty()

    def execute(self, context):
        font = bpy.data.fonts.get(self.font_name)
        if font:
            context.scene.font_manager_props.font_path = font.filepath
            self.report({'INFO'}, f"Set font to '{font.name}'")
        return {'FINISHED'}

class FONTMANAGER_OT_preview_font(bpy.types.Operator):
    bl_idname = "typeanimator.preview_font"
    bl_label = "Preview Font"
    bl_description = "Create or update a text object to preview the selected font"

    def execute(self, context):
        props = context.scene.font_manager_props
        if not props.font_path:
            self.report({'ERROR'}, "Select a font to preview")
            return {'CANCELLED'}

        try:
            font = load_font(props.font_path)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load font: {e}")
            return {'CANCELLED'}

        text_obj = context.scene.objects.get("FontPreview")
        if not text_obj:
            curve = bpy.data.curves.new(name="FontPreviewCurve", type='FONT')
            text_obj = bpy.data.objects.new("FontPreview", curve)
            context.collection.objects.link(text_obj)

        text_obj.data.body = props.preview_text
        text_obj.data.font = font
        self.report({'INFO'}, "Font preview updated")
        return {'FINISHED'}

class FONTMANAGER_OT_replace_fonts(bpy.types.Operator):
    bl_idname = "typeanimator.replace_fonts_scene"
    bl_label = "Replace Scene Fonts"
    bl_description = "Replace the font of all text objects in the scene with the selected font"

    def execute(self, context):
        props = context.scene.font_manager_props
        if not props.font_path:
            self.report({'ERROR'}, "Select a font to replace with")
            return {'CANCELLED'}

        try:
            font = load_font(props.font_path)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load font: {e}")
            return {'CANCELLED'}

        replaced_count = 0
        for obj in context.scene.objects:
            if obj.type == 'FONT':
                obj.data.font = font
                replaced_count += 1

        self.report({'INFO'}, f"Replaced font for {replaced_count} text objects")
        return {'FINISHED'}

# --- UI ---
class FONTMANAGER_UL_favorites(bpy.types.UIList):
    """UIList for displaying favorite fonts."""
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "path", text="", emboss=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.prop(item, "path", text="")

class VIEW3D_PT_font_manager(bpy.types.Panel):
    bl_label = "Fuente"
    bl_idname = "VIEW3D_PT_font_manager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Type Animator'
    bl_order = 0
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        props = context.scene.font_manager_props

        # Sección para seleccionar y previsualizar la fuente
        layout.prop(props, "font_path")
        layout.prop(props, "preview_text")
        layout.operator("typeanimator.preview_font", icon='FONT_DATA')
        layout.prop(props, "font_search")
        search = props.font_search.lower()
        for font in bpy.data.fonts:
            if search and search not in font.name.lower():
                continue
            row = layout.row(align=True)
            row.label(text="AaBbCc", icon='FONT_DATA')
            op = row.operator("typeanimator.use_system_font", text=font.name)
            op.font_name = font.name

        # ---
        layout.separator()
        layout.label(text="Favorite Fonts")

        # Sección de favoritos
        row = layout.row(align=True)
        row.template_list("FONTMANAGER_UL_favorites", "", props, "favorites", props, "active_favorite")

        col = row.column(align=True)
        col.operator("typeanimator.add_favorite_font", icon='ADD', text="")
        col.operator("typeanimator.remove_favorite_font", icon='REMOVE', text="")
        col.operator("typeanimator.use_favorite_font", icon='FILE_TICK', text="")

        # ---
        layout.separator()

        # Botón para reemplazar todas las fuentes de la escena
        layout.operator("typeanimator.replace_fonts_scene", icon='FILE_REFRESH')

# --- Registro y Desregistro ---
def register():
    """Register all classes and properties."""
    # Registrar FavoriteFontItem primero
    bpy.utils.register_class(FavoriteFontItem)
    
    # Luego registrar FontManagerProperties (que usa FavoriteFontItem)
    bpy.utils.register_class(FontManagerProperties)
    
    # Registrar operadores
    bpy.utils.register_class(FONTMANAGER_OT_add_favorite)
    bpy.utils.register_class(FONTMANAGER_OT_remove_favorite)
    bpy.utils.register_class(FONTMANAGER_OT_use_favorite)
    bpy.utils.register_class(FONTMANAGER_OT_use_system_font)
    bpy.utils.register_class(FONTMANAGER_OT_preview_font)
    bpy.utils.register_class(FONTMANAGER_OT_replace_fonts)
    
    # Registrar UI
    bpy.utils.register_class(FONTMANAGER_UL_favorites)
    bpy.utils.register_class(VIEW3D_PT_font_manager)
    
    # Registrar propiedades de escena
    bpy.types.Scene.font_manager_props = bpy.props.PointerProperty(type=FontManagerProperties)
    logger.debug("Font Manager module registered")

def unregister():
    """Unregister all classes and properties."""
    # Desregistrar propiedades de escena primero
    if hasattr(bpy.types.Scene, "font_manager_props"):
        del bpy.types.Scene.font_manager_props
    
    # Desregistrar UI
    bpy.utils.unregister_class(VIEW3D_PT_font_manager)
    bpy.utils.unregister_class(FONTMANAGER_UL_favorites)
    
    # Desregistrar operadores
    bpy.utils.unregister_class(FONTMANAGER_OT_replace_fonts)
    bpy.utils.unregister_class(FONTMANAGER_OT_preview_font)
    bpy.utils.unregister_class(FONTMANAGER_OT_use_system_font)
    bpy.utils.unregister_class(FONTMANAGER_OT_use_favorite)
    bpy.utils.unregister_class(FONTMANAGER_OT_remove_favorite)
    bpy.utils.unregister_class(FONTMANAGER_OT_add_favorite)
    
    # Desregistrar FontManagerProperties primero (que usa FavoriteFontItem)
    bpy.utils.unregister_class(FontManagerProperties)
    
    # Luego desregistrar FavoriteFontItem
    bpy.utils.unregister_class(FavoriteFontItem)
    
    logger.debug("Font Manager module unregistered")
