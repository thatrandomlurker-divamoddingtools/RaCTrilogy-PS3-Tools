# .grp importer v0.1

import bpy
import os

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator


class ImportGrpThroughFileBrowser(Operator, ImportHelper):

    bl_idname = "test.open_filebrowser"
    bl_label = "Import GRP File"
    
    filter_glob = StringProperty(
        default='*.grp',
        options={'HIDDEN'}
    )

    def execute(self, context):
        obj = bpy.context.active_object
        vertGrpWeights = []
        vertGrpSets = []

        with open(self.filepath, 'r') as grp:
            for line in grp.readlines():
                dat = line.split(' ')
                if dat[0] == 'bwt':
                    vertGrpWeights.append([float(dat[1]), float(dat[2]), float(dat[3]), float(dat[4])])
                elif dat[0] == 'bi':
                    temp = [int(dat[1]), int(dat[2]), int(dat[3]), int(dat[4])]
                    vertGrpSets.append([int(dat[1]), int(dat[2]), int(dat[3]), int(dat[4])])
            print(len(vertGrpSets))
            print(len(vertGrpWeights))
            GrpCount = max(max(vertGrpSets)) + 1
            # ok, start with making the groups
            for i in range(GrpCount):
                grp = obj.vertex_groups.new("VertGroup_" + str(i))
            # now work out how to add a vert to each group with a specific weight... maybe
            for i in range(len(vertGrpSets)):  # tbf either would work, since they are intrinsically linked
                currGroups = vertGrpSets[i]
                currWeights = vertGrpWeights[i]
                for g in range(4):
                    obj.vertex_groups["VertGroup_" + str(currGroups[g])].add([i], currWeights[g], 'ADD')
                    
        return {'FINISHED'}
            


def register():
    bpy.utils.register_class(ImportGrpThroughFileBrowser)


def unregister():
    bpy.utils.unregister_class(ImportGrpThroughFileBrowser)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.test.open_filebrowser('INVOKE_DEFAULT')