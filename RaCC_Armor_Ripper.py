import struct
import sys
file = sys.argv[1]
# Since verts are global, i should define the vert list outside of any reading so it can all be accessed
Vertices = []
Weights = []
BoneIdxs = []
OtherVertices = []
SubmeshInfo = []
mtlWrittenTexIndexes = []
texDataOffs = []
texDataDimensions = []
texDataSizes = []
curmesh = 0

with open(file, 'rb') as ps3:
    SepDec = input("Seperate Meshes? (Y for Yes, N for No.)\n")
    if SepDec.lower() == 'y':
        SeperateMeshes = True
    else:
        SeperateMeshes = False
    # Where info about the armor model is located
    MeshInfoOffset = struct.unpack('>I', ps3.read(4))[0]
    # Where the vram data is located
    VramInfoOffset = struct.unpack('>I', ps3.read(4))[0]
    # How many entries exist in the vram data
    VramCount = struct.unpack('>I', ps3.read(4))[0]
    # Go to the mesh info offset and start grabbing submesh info
    ps3.seek(MeshInfoOffset)
    SubmeshCount = struct.unpack('>I', ps3.read(4))[0]
    UnkCount = struct.unpack('>I', ps3.read(4))[0]
    SubmeshInfoOffset = struct.unpack('>I', ps3.read(4))[0]
    UnkInfoOffset = struct.unpack('>I', ps3.read(4))[0]
    VertOffset = struct.unpack('>I', ps3.read(4))[0]
    FaceOffset = struct.unpack('>I', ps3.read(4))[0]
    VertCount = struct.unpack('>H', ps3.read(2))[0]
    OtherVertCount = struct.unpack('>H', ps3.read(2))[0]
    ps3.seek(SubmeshInfoOffset)
    # While parsing the submesh info (tex index, start face, face count, and something i don't know) we generate the material file
    with open(file.split('.')[0] + ".mtl", 'w') as m:
        for i in range(SubmeshCount):
            Info = {"TextureIndex": 0, "StartFace": 0, "Faces": 0, "Unk": 0}
            Info["TextureIndex"] = struct.unpack('>I', ps3.read(4))[0]
            if Info["TextureIndex"] not in mtlWrittenTexIndexes:
                m.write(f"newmtl tex{Info['TextureIndex']}\nKa 1.0 1.0 1.0\nKd 1.0 1.0 1.0\nmap_Kd " + file.split('.')[0] + f"_{Info['TextureIndex']}.dds\n")
                mtlWrittenTexIndexes.append(Info["TextureIndex"])
            Info["StartFace"] = struct.unpack('>I', ps3.read(4))[0]
            Info["Faces"] = struct.unpack('>I', ps3.read(4))[0]
            Info["Unk"] = struct.unpack('>I', ps3.read(4))[0]
            SubmeshInfo.append(Info)
    # Go to the vertices
    ps3.seek(VertOffset)
    for i in range(VertCount):
        # Each vert contains its Position, normal, uv, weights, and Bone indices
        Pos = list(struct.unpack('>fff', ps3.read(12)))
        Normal = list(struct.unpack('>fff', ps3.read(12)))
        UV = list(struct.unpack('>ff', ps3.read(8)))
        WeightTemp = list(struct.unpack('BBBB', ps3.read(4)))
        # Put the Bone indices into a list for later use
        BoneIdxs.append(list(struct.unpack('BBBB', ps3.read(4))))
        # For the weights, some math has to be done
        # For verts which are fully weighted to a bone, it's a single 255
        # For verts rigged to 2-4 bones, it's a combined total up to 256
        # as such, we do some simple division to get it into a proper value most programs can use
        WeightBlock = []
        for Weight in WeightTemp:
            if Weight == 0xFF:
                WeightBlock.append(float(1.0))
            else:
                WeightBlock.append(float(Weight / 255))
        # Add the fixed weights into the global weights list
        Weights.append(WeightBlock)
        # Add the vert to the global vertices list
        Vertices.append({"P": Pos, "N": Normal, "U": UV})
    # this is just assumed data. it's used by a seperate submesh section to the main submesh section, usually with a -2 tex index
    # i have no clue what it's for, but the models look perfectly normal without it, so i just read it and ignore it for now
    for i in range(OtherVertCount):
        Pos = list(struct.unpack('>fff', ps3.read(12)))
        Normal = list(struct.unpack('>fff', ps3.read(12)))
        WeightTemp = list(struct.unpack('BBBB', ps3.read(4)))
        BoneIdxSet = list(struct.unpack('BBBB', ps3.read(4)))
        WeightBlock = []
        for Weight in WeightTemp:
            if Weight == 0xFF:
                WeightBlock.append(float(1.0))
            else:
                WeightBlock.append(float(Weight / 255))
        OtherVertices.append({"P": Pos, "N": Normal, "W": WeightBlock, "I": BoneIdxs})
    # Now that the model is fully parsed, go to the vram info position
    ps3.seek(VramInfoOffset)
    # open the corrseponding vram file
    with open(file.split('.')[0] + '.vram', 'rb') as vram:
        for i in range(VramCount):
            # Read the offset of the data
            texDataOffs.append(struct.unpack('>I', ps3.read(4))[0])
            ps3.seek(20, 1)
            # Read the texture dimensions
            texDataDimensions.append(list(struct.unpack('>HH', ps3.read(4))))
            ps3.seek(8, 1)
        # a hacky way of getting the texture sizes
        for i in range(VramCount):
            if i == 0:
                continue
            else:
                texDataSizes.append((texDataOffs[i] - 16) - texDataOffs[i-1])
        for i in range(VramCount):
            # not much to explain here
            # if i is last vram entry, read
            # else, read specific size
            with open(file.split('.')[0] + f"_{i}.dds", 'wb') as dds:
                if i == VramCount - 1:
                    vram.seek(texDataOffs[i])
                    dds.write(b'DDS \x7C\x00\x00\x00\x07\x1C\x0A\x00')
                    dds.write(struct.pack('<I', texDataDimensions[i][0]))
                    dds.write(struct.pack('<I', texDataDimensions[i][1]))
                    tempPosHold = dds.tell()
                    dds.write(struct.pack('<I', 0))
                    dds.write(b'\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x04\x00\x00\x00DXT5\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
                    ddsdata = vram.read()
                    endWritePos = dds.tell()
                    dds.seek(tempPosHold)
                    dds.write(struct.pack('<I', len(ddsdata)))
                    dds.seek(endWritePos)
                    dds.write(ddsdata)
                else:
                    vram.seek(texDataOffs[i])
                    dds.write(b'DDS \x7C\x00\x00\x00\x07\x1C\x0A\x00')
                    dds.write(struct.pack('<I', texDataDimensions[i][0]))
                    dds.write(struct.pack('<I', texDataDimensions[i][1]))
                    dds.write(struct.pack('<I', texDataSizes[i]))
                    dds.write(b'\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x04\x00\x00\x00DXT5\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
                    dds.write(vram.read(texDataSizes[i]))
    # Dump the obj file
    with open(file.split('.')[0] + ".obj", 'w') as o:
        o.write('matlib armor0.mtl\n')
        for v in Vertices:
            o.write(f"v {v['P'][0]} {v['P'][1]} {v['P'][2]}\n")
            o.write(f"vn {v['N'][0]} {v['N'][1]} {v['N'][2]}\n")
            o.write(f"vt {v['U'][0]} {v['U'][1] * -1}\n")
        ps3.seek(FaceOffset)
        for s in SubmeshInfo:
            if SeperateMeshes:
                o.write(f"o mesh_{curmesh}\n")
            o.write(f"usemtl tex{s['TextureIndex']}\n")
            for i in range(int(s["Faces"] // 3)):
                FaceSet = struct.unpack('>HHH', ps3.read(6))
                o.write(f"f {FaceSet[0] + 1}/{FaceSet[0] + 1}/{FaceSet[0] + 1} {FaceSet[1] + 1}/{FaceSet[1] + 1}/{FaceSet[1] + 1} {FaceSet[2] + 1}/{FaceSet[2] + 1}/{FaceSet[2] + 1}\n")
            curmesh += 1
    # And dump the indices + weights to a .grp file (not to be confused with the grp format used by win3.1 lol)
    with open(file.split('.')[0] + ".grp", 'w') as o:
        for w in Weights:
            o.write(f"bwt {w[0]} {w[1]} {w[2]} {w[3]}\n")
        for b in BoneIdxs:
            o.write(f"bi {b[0]} {b[1]} {b[2]} {b[3]}\n")
        
        
                