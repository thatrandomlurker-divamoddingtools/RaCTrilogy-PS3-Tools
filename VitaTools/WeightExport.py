# .grp importer v0.1

import bpy
import os

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper
from bpy.types import Operator


class ExportGrpThroughFileBrowser(Operator, ExportHelper):

    bl_idname = "test.open_filebrowser"
    bl_label = "Export GRP File"
    filename_ext = ".grp"
    
    filter_glob = StringProperty(
        default='*.grp',
        options={'HIDDEN'}
    )

    def execute(self, context):
        obj = bpy.context.active_object
        vertGrpWeights = []
        vertGrpSets = []

        with open(self.filepath, 'w') as grp:
            for vert in obj.data.vertices:
                if len(vert.groups) == 1:
                    grp.write("bi {v0g} 0 0 0\n".format(v0g=obj.vertex_groups[vert.groups[0].group].name.split("_")[1]))
                    grp.write("bwt {v0w} 0 0 0\n".format(v0w=vert.groups[0].weight))
                elif len(vert.groups) == 2:
                    grp.write("bi {v0g} {v1g} 0 0\n".format(v0g=obj.vertex_groups[vert.groups[0].group].name.split("_")[1], v1g=obj.vertex_groups[vert.groups[1].group].name.split("_")[1]))
                    grp.write("bwt {v0w} {v1w} 0 0\n".format(v0w=vert.groups[0].weight, v1w=vert.groups[1].weight))
                elif len(vert.groups) == 3:
                    grp.write("bi {v0g} {v1g} {v2g} 0\n".format(v0g=obj.vertex_groups[vert.groups[0].group].name.split("_")[1], v1g=obj.vertex_groups[vert.groups[1].group].name.split("_")[1], v2g=obj.vertex_groups[vert.groups[2].group].name.split("_")[1]))
                    grp.write("bwt {v0w} {v1w} {v2w} 0\n".format(v0w=vert.groups[0].weight, v1w=vert.groups[1].weight, v2w=vert.groups[2].weight))
                elif len(vert.groups) == 4:
                    grp.write("bi {v0g} {v1g} {v2g} {v3g}\n".format(v0g=obj.vertex_groups[vert.groups[0].group].name.split("_")[1], v1g=obj.vertex_groups[vert.groups[1].group].name.split("_")[1], v2g=obj.vertex_groups[vert.groups[2].group].name.split("_")[1], v3g=obj.vertex_groups[vert.groups[3].group].name.split("_")[1]))
                    grp.write("bwt {v0w} {v1w} {v2w} {v3w}\n".format(v0w=vert.groups[0].weight, v1w=vert.groups[1].weight, v2w=vert.groups[2].weight, v3w=vert.groups[3].weight))
                    
        return {'FINISHED'}
            


def register():
    bpy.utils.register_class(ExportGrpThroughFileBrowser)


def unregister():
    bpy.utils.unregister_class(ExportGrpThroughFileBrowser)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.test.open_filebrowser('INVOKE_DEFAULT')