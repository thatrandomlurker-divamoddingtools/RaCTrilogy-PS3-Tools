import struct
from dataclasses import dataclass

class armorVert:
    Pos: list
    Norm: list
    UV: list
    Idxs: list
    Weights: list

def MtlParse(mtl):
    """Returns two lists of Material names and their corresponding Texture names."""
    MatNames = []
    TexNames = []
    for line in mtl.readlines():
        if line[0:6] == "newmtl":
            MatNames.append(line[7:].strip('\n'))
        elif line[0:6] == "map_Kd":
            TexNames.append(line[7:].strip('\n'))
    return MatNames, TexNames
    
def ObjParse(obj, mtl, grp, o, vram):
    InverseUVs = False
    MatNames, TexNames = MtlParse(mtl)
    print(TexNames)
    CurrTexInfoFaceCount = 0
    CurrTexInfoTexId = 0
    TextureInfoStartFace = 0
    VertCoords = []
    UVs = []
    Normals = []
    BoneWeights = []
    BoneIndices = []
    FaceIndices = []
    FaceUVIndices = []
    FaceNormalIndices = []
    TextureInfos = []
    for line in obj.readlines():
        dat = line.split(' ')
        if dat[0] == 'usemtl':
            mtlName = dat[1].strip('\n')
            print(mtlName)
            if CurrTexInfoFaceCount != 0:
                TextureInfos.append([CurrTexInfoTexId, TextureInfoStartFace, CurrTexInfoFaceCount])
            CurrTexInfoTexId = MatNames.index(mtlName)
            print(CurrTexInfoTexId)
            TextureInfoStartFace += CurrTexInfoFaceCount
            CurrTexInfoFaceCount = 0
        elif dat[0] == 'v':
            VertCoords.append([float(dat[1]), float(dat[2]), float(dat[3].strip('\n'))])
        elif dat[0] == 'vn':
            Normals.append([float(dat[1]), float(dat[2]), float(dat[3].strip('\n'))])
        elif dat[0] == 'vt':
            UVs.append([float(dat[1]), float(dat[2].strip('\n'))])
        elif dat[0] == 'f':
            CurrTexInfoFaceCount += 3
            idx1s = dat[1].split('/')
            idx2s = dat[2].split('/')
            idx3s = dat[3].split('/')
            FaceIndices.append([int(idx1s[0]), int(idx2s[0]), int(idx3s[0])])
            FaceUVIndices.append([int(idx1s[1]), int(idx2s[1]), int(idx3s[1])])
            FaceNormalIndices.append([int(idx1s[2]), int(idx2s[2]), int(idx3s[2].strip('\n'))])
    TextureInfos.append([CurrTexInfoTexId, TextureInfoStartFace, CurrTexInfoFaceCount]) # to get the last one in
    for line in grp.readlines():
        dat = line.split(' ')
        if dat[0] == 'bwt':
            Weight1 = float(dat[1])
            Weight2 = float(dat[2])
            Weight3 = float(dat[3])
            Weight4 = float(dat[4].strip('\n'))
            if Weight1 == float(1.0):
                WeightList = [255, 0, 0, 0]
                BoneWeights.append(WeightList)
            else:
                intWeight1 = int(Weight1 * 256)
                intWeight2 = int(Weight2 * 256)
                intWeight3 = int(Weight3 * 256)
                intWeight4 = int(Weight4 * 256)
                WeightList = [intWeight1, intWeight2, intWeight3, intWeight4]
                if sum(WeightList) > 256:
                    WeightList[WeightList.index(min(WeightList))] -= 1
                elif sum(WeightList) < 256:
                    WeightList[WeightList.index(max(WeightList))] += 1
                print(sum(WeightList))
                if sum(WeightList) != 256:
                    print('welp. guess this doesn\'t work.')
                    exit()
                BoneWeights.append(WeightList)
        elif dat[0] == 'bi':
            IndexList = [int(dat[1]), int(dat[2]), int(dat[3]), int(dat[4].strip('\n'))]
            BoneIndices.append(IndexList)
    # Checking validity
    print(f"Lengths: {len(VertCoords)} {len(UVs)} {len(Normals)}")
    #if len(VertCoords) != len(Normals):
        #print("This obj will not work, as it has been optimized by blender. use my export script to get a working obj file.")
        #raise Exception("Invalid OBJ File: Inequal amounts of Verts and Normals. must be a 1:1 match per vert. Exiting...")
        #exit(-1)
    # Won't work
    armorVerts = [None] * len(VertCoords)
    for i in range(len(FaceIndices)):
        Vert1 = armorVert()
        Vert2 = armorVert()
        Vert3 = armorVert()
        Vert1.Pos = list([VertCoords[FaceIndices[i][0]-1][0], VertCoords[FaceIndices[i][0]-1][1], VertCoords[FaceIndices[i][0]-1][2]])
        Vert2.Pos = list([VertCoords[FaceIndices[i][1]-1][0], VertCoords[FaceIndices[i][1]-1][1], VertCoords[FaceIndices[i][1]-1][2]])
        Vert3.Pos = list([VertCoords[FaceIndices[i][2]-1][0], VertCoords[FaceIndices[i][2]-1][1], VertCoords[FaceIndices[i][2]-1][2]])
        Vert1.Norm = list([Normals[FaceNormalIndices[i][0]-1][0], Normals[FaceNormalIndices[i][0]-1][1], Normals[FaceNormalIndices[i][0]-1][2]])
        Vert2.Norm = list([Normals[FaceNormalIndices[i][1]-1][0], Normals[FaceNormalIndices[i][1]-1][1], Normals[FaceNormalIndices[i][1]-1][2]])
        Vert3.Norm = list([Normals[FaceNormalIndices[i][2]-1][0], Normals[FaceNormalIndices[i][2]-1][1], Normals[FaceNormalIndices[i][2]-1][2]])
        Vert1.UV = list([UVs[FaceUVIndices[i][0]-1][0], UVs[FaceUVIndices[i][0]-1][1]])
        Vert2.UV = list([UVs[FaceUVIndices[i][1]-1][0], UVs[FaceUVIndices[i][1]-1][1]])
        Vert3.UV = list([UVs[FaceUVIndices[i][2]-1][0], UVs[FaceUVIndices[i][2]-1][1]])
        # Temp
        Vert1.Idxs = BoneIndices[FaceIndices[i][0]-1]
        Vert2.Idxs = BoneIndices[FaceIndices[i][0]-1]
        Vert3.Idxs = BoneIndices[FaceIndices[i][0]-1]
        Vert1.Weights = BoneWeights[FaceIndices[i][0]-1]
        Vert2.Weights = BoneWeights[FaceIndices[i][0]-1]
        Vert3.Weights = BoneWeights[FaceIndices[i][0]-1]
        armorVerts[FaceIndices[i][0]-1] = Vert1
        armorVerts[FaceIndices[i][1]-1] = Vert2
        armorVerts[FaceIndices[i][2]-1] = Vert3
    for v in armorVerts:
        if v == None:
            print('impossible')
    print(len(armorVerts))
    print(FaceIndices[0])
    o.write(b'\x00\x00\x00\x10')
    TexInfoOffset = o.tell()
    o.write(b'\x00\x00\x00\x00')
    o.write(struct.pack('>I', len(TexNames)))
    o.write(b'\x00\x00\x00\x00')
    o.write(struct.pack('>I', len(TextureInfos)))
    o.write(b'\x00\x00\x00\x00')
    o.write(b'\x00\x00\x00\x30')  # TextureInfosOffset
    o.write(b'\x00\x00\x00\x00')
    VertexPointerOffset = o.tell()
    o.write(b'\x00\x00\x00\x00')
    FacePointerOffset = o.tell()
    o.write(b'\x00\x00\x00\x00')
    o.write(struct.pack('>H', len(VertCoords)))
    o.write(b'\x00\x00\x00\x00\x00\x00')
    # Now at the TextureInfosOffset
    for tex in TextureInfos:
        o.write(struct.pack('>I', tex[0]))  # TexIdx
        o.write(struct.pack('>I', tex[1]))  # StartFace
        o.write(struct.pack('>I', tex[2]))  # FaceCount
        o.write(b'\x05\x00\x00\x00')
    # Padding
    o.write(b'\x00' * 112)
    VertOffset = o.tell()
    o.seek(VertexPointerOffset)
    o.write(struct.pack('>I', VertOffset))
    o.seek(VertOffset)
    for vert in armorVerts:
        o.write(struct.pack('>fff', vert.Pos[0], vert.Pos[1], vert.Pos[2]))
        o.write(struct.pack('>fff', vert.Norm[0], vert.Norm[1], vert.Norm[2]))
        o.write(struct.pack('>ff', vert.UV[0], vert.UV[1] * -1))
        o.write(struct.pack('BBBB', vert.Weights[0], vert.Weights[1], vert.Weights[2], vert.Weights[3]))
        o.write(struct.pack('bbbb', vert.Idxs[0], vert.Idxs[1], vert.Idxs[2], vert.Idxs[3]))
    while o.tell() % 16 != 0:
        o.write(b'\x00') # to align
    FaceOffset = o.tell()
    o.seek(FacePointerOffset)
    o.write(struct.pack('>I', FaceOffset))
    o.seek(FaceOffset)
    for fset in FaceIndices:
        o.write(struct.pack('>HHH', fset[0]-1, fset[1]-1, fset[2]-1))
    while o.tell() % 16 != 0:
        o.write(b'\x00')
    TexInfoPos = o.tell()
    o.seek(TexInfoOffset)
    o.write(struct.pack('>I', TexInfoPos))
    o.seek(TexInfoPos)
    WrittenTexs = []
    for tex in TexNames:
        with open(tex, 'rb') as file:
            file.seek(0xC)
            texWidth = struct.unpack('<I', file.read(4))[0]
            texHeight = struct.unpack('<I', file.read(4))[0]
            o.write(struct.pack('>I', vram.tell()))
            o.write(b'\x00\x0A\x88\x29\x00\x01\x03\x03\x80\x04\x80\x00\x00\x00\xAA\xE4\x02\x06\x3E\x80')
            o.write(struct.pack('>hh', texWidth, texHeight))
            o.write(b'\x00\x10\x00\x00\x00\xFF\x00\x00')
            file.seek(0x80)
            vram.write(file.read())
            while vram.tell() % 16 != 0:
                vram.write(b'\x00')
            vram.write(b'\x00' * 16)
        