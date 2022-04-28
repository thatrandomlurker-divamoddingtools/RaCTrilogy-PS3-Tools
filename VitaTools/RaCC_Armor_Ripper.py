import struct
import sys
import io
file = sys.argv[1]
# Since verts are global, i should define the vert list outside of any reading so it can all be accessed
Vertices = []
Weights = []
BoneIdxs = []
ReflectionMeshVerts = []
SubmeshInfo = []
ReflectionMeshInfo = []
mtlWrittenTexIndexes = []
texDataOffs = []
texDataDimensions = []
texDataSizes = []
texDataMipCounts = []
texDataFormats = []
curmesh = 0

with open(file, 'rb') as ps3:
    SepDec = input("Seperate Meshes? (Y for Yes, N for No.)\n")
    RefDec = input("Read Reflection Data? (Y for Yes, N for No.)\n")
    if SepDec.lower() == 'y':
        SeperateMeshes = True
    else:
        SeperateMeshes = False
    if RefDec.lower() == 'y':
        ReadRef = True
    else:
        ReadRef = False
    # Where info about the armor model is located
    MeshInfoOffset = struct.unpack('I', ps3.read(4))[0]
    # Where the vram data is located
    VramInfoOffset = struct.unpack('I', ps3.read(4))[0]
    # How many entries exist in the vram data
    VramCount = struct.unpack('I', ps3.read(4))[0]
    # Go to the mesh info offset and start grabbing submesh info
    ps3.seek(MeshInfoOffset)
    SubmeshCount = struct.unpack('I', ps3.read(4))[0]
    ReflectionMeshCount = struct.unpack('I', ps3.read(4))[0]
    SubmeshInfoOffset = struct.unpack('I', ps3.read(4))[0]
    ReflectionInfoOffset = struct.unpack('I', ps3.read(4))[0]
    VertOffset = struct.unpack('I', ps3.read(4))[0]
    FaceOffset = struct.unpack('I', ps3.read(4))[0]
    VertCount = struct.unpack('H', ps3.read(2))[0]
    ReflectionVertCount = struct.unpack('H', ps3.read(2))[0]
    ps3.seek(SubmeshInfoOffset)
    # While parsing the submesh info (tex index, start face, face count, and something i don't know) we generate the material file
    with open(file.split('.')[0] + ".mtl", 'w') as m:
        for i in range(SubmeshCount):
            Info = {"TextureIndex": 0, "StartFace": 0, "Faces": 0, "Unk": 0}
            Info["TextureIndex"] = struct.unpack('I', ps3.read(4))[0]
            if Info["TextureIndex"] not in mtlWrittenTexIndexes:
                m.write(f"newmtl tex{Info['TextureIndex']}\nKa 1.0 1.0 1.0\nKd 1.0 1.0 1.0\nmap_Kd " + file.split('.')[0] + f"_{Info['TextureIndex']}.dds\n")
                mtlWrittenTexIndexes.append(Info["TextureIndex"])
            Info["StartFace"] = struct.unpack('I', ps3.read(4))[0]
            Info["Faces"] = struct.unpack('I', ps3.read(4))[0]
            Info["Unk"] = struct.unpack('I', ps3.read(4))[0]
            SubmeshInfo.append(Info)
        if ReadRef:
            ps3.seek(ReflectionInfoOffset)
            for i in range(ReflectionMeshCount):
                Info = {"TextureIndex": 0, "StartFace": 0, "Faces": 0, "Unk": 0}
                Info["TextureIndex"] = struct.unpack('I', ps3.read(4))[0]
                m.write(f"newmtl reflect_{i}\nKa 1.0 1.0 1.0\nKd 1.0 1.0 1.0\n")
                Info["StartFace"] = struct.unpack('I', ps3.read(4))[0]
                Info["Faces"] = struct.unpack('I', ps3.read(4))[0]
                Info["Unk"] = struct.unpack('I', ps3.read(4))[0]
                ReflectionMeshInfo.append(Info)
    # Go to the vertices
    ps3.seek(VertOffset)
    for i in range(VertCount):
        # Each vert contains its Position, normal, uv, weights, and Bone indices
        Pos = list(struct.unpack('fff', ps3.read(12)))
        Normal = list(struct.unpack('bbb', ps3.read(3)))
        pad = ps3.read(1)
        UV = list(struct.unpack('ff', ps3.read(8)))
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
        Vertices.append({"P": Pos, "N": [Normal[0] / 127, Normal[1] / 127, Normal[2] / 127], "U": UV})
    # I now know this is the reflection mesh.
    for i in range(ReflectionVertCount):
        Pos = list(struct.unpack('fff', ps3.read(12)))
        Normal = list(struct.unpack('bbb', ps3.read(3)))
        pad = ps3.read(1)
        WeightTemp = list(struct.unpack('BBBB', ps3.read(4)))
        BoneIdxSet = list(struct.unpack('BBBB', ps3.read(4)))
        BoneIdxs.append(BoneIdxSet)
        WeightBlock = []
        for Weight in WeightTemp:
            if Weight == 0xFF:
                WeightBlock.append(float(1.0))
            else:
                WeightBlock.append(float(Weight / 255))
        # Add the fixed weights into the global weights list
        Weights.append(WeightBlock)
        ReflectionMeshVerts.append({"P": Pos, "N": [Normal[0] / 127, Normal[1] / 127, Normal[2] / 127], "W": WeightBlock, "I": BoneIdxs})
    # Now that the model is fully parsed, go to the vram info position
    ps3.seek(VramInfoOffset)
    # open the corrseponding vram file
    with open(file.split('.')[0] + '.vram', 'rb') as vram:
        for i in range(VramCount):
            # Read the offset of the data
            texDataOffs.append(struct.unpack('I', ps3.read(4))[0])
            texDataFormats.append(ps3.read(4))
            ps3.seek(4, 1)
            texDataMipCounts.append(struct.unpack('I', ps3.read(4))[0])
            ps3.seek(8, 1)
            # Read the texture dimensions
            texDataDimensions.append(list(struct.unpack('HH', ps3.read(4))))
            texDataSizes.append(struct.unpack('I', ps3.read(4))[0])
            ps3.seek(84, 1)
        for i in range(VramCount):
            # not much to explain here
            # if i is last vram entry, read
            # else, read specific size
            with open(file.split('.')[0] + f"_{i}.gxt", 'wb') as gxt:
                vram.seek(texDataOffs[i])
                gxt.write(b'GXT\x00\x03\x00\x00\x10\x01\x00\x00\x00\x40\x00\x00\x00')
                gxt.write(struct.pack("<I", texDataSizes[i]))
                gxt.write(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x40\x00\x00\x00")
                gxt.write(struct.pack("<I", texDataSizes[i]))
                gxt.write(b"\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00")
                gxt.write(texDataFormats[i])
                gxt.write(struct.pack('<HH', texDataDimensions[i][0], texDataDimensions[i][1]))
                gxt.write(struct.pack("<HH", texDataMipCounts[i], 0))
                gxt.write(vram.read(texDataSizes[i]))
    # Dump the obj file
    with open(file.split('.')[0] + ".obj", 'w') as o:
        o.write('matlib armor0.mtl\n')
        for v in Vertices:
            o.write(f"v {v['P'][0]} {v['P'][1]} {v['P'][2]}\n")
            o.write(f"vn {v['N'][0]} {v['N'][1]} {v['N'][2]}\n")
            o.write(f"vt {v['U'][0]} {v['U'][1] * -1}\n")
        if ReadRef:
            o.write('# Start of Reflection Verts\n')
            for ov in ReflectionMeshVerts:
                o.write(f"v {ov['P'][0]} {ov['P'][1]} {ov['P'][2]}\n")
                o.write(f"vn {ov['N'][0]} {ov['N'][1]} {ov['N'][2]}\n")
        ps3.seek(FaceOffset)
        if not SeperateMeshes:
            o.write(f"o mesh\n")
        for s in SubmeshInfo:
            if SeperateMeshes:
                o.write(f"o mesh_{curmesh}\n")
            o.write(f"usemtl tex{s['TextureIndex']}\n")
            for i in range(int(s["Faces"] // 3)):
                FaceSet = struct.unpack('HHH', ps3.read(6))
                o.write(f"f {FaceSet[0] + 1}/{FaceSet[0] + 1}/{FaceSet[0] + 1} {FaceSet[1] + 1}/{FaceSet[1] + 1}/{FaceSet[1] + 1} {FaceSet[2] + 1}/{FaceSet[2] + 1}/{FaceSet[2] + 1}\n")
            curmesh += 1
        if ReadRef:
            o.write('# Start of reflection faces\n')
            for i in range(len(ReflectionMeshInfo)):
                o.write(f"o reflect_{i}\n")
                o.write(f"usemtl reflect_{i}\n")
                for i in range(int(ReflectionMeshInfo[i]["Faces"] // 3)):
                    FaceSet = struct.unpack('HHH', ps3.read(6))
                    o.write(f"f {FaceSet[0] + 1}//{FaceSet[0] + 1} {FaceSet[1] + 1}//{FaceSet[1] + 1} {FaceSet[2] + 1}//{FaceSet[2] + 1}\n")
                curmesh += 1
    # And dump the indices + weights to a .grp file (not to be confused with the grp format used by win3.1 lol)
    with open(file.split('.')[0] + ".grp", 'w') as o:
        for w in Weights:
            o.write(f"bwt {w[0]} {w[1]} {w[2]} {w[3]}\n")
        for b in BoneIdxs:
            o.write(f"bi {b[0]} {b[1]} {b[2]} {b[3]}\n")
            
    # Experimental bone dumping
    
    """with open('engine.ps3', 'rb') as eng:
        mobyOff = struct.unpack('>I', eng.read(4))[0]
        eng.seek(mobyOff)
        mobyCount = struct.unpack('>I', eng.read(4))[0]
        for i in range(mobyCount):
            mobyInfo = struct.unpack('>II', eng.read(8))
            if mobyInfo[0] == 0:  # id for ratchet's model:
                eng.seek(mobyInfo[1])
                break
        RatchetMobyStart = eng.tell()
        print(RatchetMobyStart)
        eng.seek(8, 1)
        boneCount = eng.read(1)[0]  # quick way to grab a single byte number
        print(boneCount)
        eng.seek(11, 1)  # since we're only here for the bone positions, we can just ignore extra data.
        BoneMtxOffset = struct.unpack('>I', eng.read(4))[0] + RatchetMobyStart
        BoneDataOffset = struct.unpack('>I', eng.read(4))[0] + RatchetMobyStart
        eng.seek(BoneDataOffset)
        with open('arm.csv', 'w') as arm:
            print(eng.tell())
            for i in range(boneCount):
                BoneX = struct.unpack('>f', eng.read(4))[0]
                BoneY = struct.unpack('>f', eng.read(4))[0]
                BoneZ = struct.unpack('>f', eng.read(4))[0]
                eng.seek(4, 1)  # to skip the extra stuff
                arm.write(f"{BoneX * 0.001}, {BoneY * 0.001}, {BoneZ * 0.001}\n")"""
            
        
        
        
                