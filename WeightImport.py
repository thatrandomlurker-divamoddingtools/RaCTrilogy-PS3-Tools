# the submesh should be selected and Active before you click "Run Script"

import bpy
obj = bpy.context.active_object
GrpCount = 0  # fill this in later once the groups have been read and a max value is determined
vertGrpSets = []
vertGrpWeights = []
# manually specify the file path
# easist way is to shift+right click a grp file, copy as path, then paste and add extra "\"s after each "\"
with open("C:\\Users\\john\\Desktop\\New folder\\Avenger\\armor1_13.grp", 'r') as f:
    for line in f.readlines():
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

