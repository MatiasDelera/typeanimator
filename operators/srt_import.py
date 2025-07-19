import bpy
import re
try:
    from bpy_extras.io_utils import ImportHelper
    BASES = (bpy.types.Operator, ImportHelper)
except Exception:
    BASES = (bpy.types.Operator,)
from ..properties import TA_LetterAnimProperties

TIME_RE = re.compile(r"(\d\d):(\d\d):(\d\d),(\d\d\d)")

class OBJECT_OT_import_srt(*BASES):
    bl_idname = "typeanimator.import_srt"
    bl_label = "Import SRT"
    filename_ext = ".srt"

    def execute(self, context):
        text = open(self.filepath, 'r', encoding='utf-8').read()
        pattern = re.compile(r"\d+\s+([0-9:,]+)\s+-->\s+([0-9:,]+)\s+(.*?)(?=\n\n|$)", re.S)
        entries = pattern.findall(text)
        scene = context.scene
        fps = scene.render.fps
        for i, (start, end, body) in enumerate(entries, 1):
            in_frame = self._time_to_frame(start, fps)
            out_frame = self._time_to_frame(end, fps)
            curve = bpy.data.curves.new(body=body.replace('\n', ' '), type='FONT')
            obj = bpy.data.objects.new(f"SRT_{i}", curve)
            scene.collection.objects.link(obj)
            obj.location.y = -1.0
            bpy.context.view_layer.objects.active = obj
            bpy.ops.typeanimator.apply_in(start_frame=in_frame)
            bpy.ops.typeanimator.apply_out(start_frame=out_frame)
            # lower third background
            bpy.ops.mesh.primitive_plane_add(size=3, location=(0, -1.1, 0))
            bg = context.active_object
            bpy.ops.typeanimator.apply_in(start_frame=in_frame)
            bpy.ops.typeanimator.apply_out(start_frame=out_frame)
        return {'FINISHED'}

    def _time_to_frame(self, t, fps):
        h, m, s, ms = TIME_RE.match(t).groups()
        total = int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000.0
        return int(round(total*fps))

def register():
    bpy.utils.register_class(OBJECT_OT_import_srt)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_import_srt)
