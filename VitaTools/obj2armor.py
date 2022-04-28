import defs
import sys
file = sys.argv[1]

with open(file.split('.')[0] + ".grp", 'r') as grp:
    with open(file.split('.')[0] + ".mtl", 'r') as mtl:
        with open(file, 'r') as obj:
            with open(file.split('.')[0] + ".ps3", 'wb') as ps3:
                with open(file.split('.')[0] + ".vram", 'wb') as vram:
                    defs.ObjParse(obj, mtl, grp, ps3, vram)