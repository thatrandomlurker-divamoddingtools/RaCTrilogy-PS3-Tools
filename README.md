# RaCTrilogy-PS3-Tools
Tools to help rip RaCTrilogy .ps3 files with intact rigging

# RaCC_Armor_Ripper.py
Usage: "RaCC_Armor_Ripper.py armor*.ps3"

Reads a .ps3 file and dumps the mesh to a .obj file, as well as weights to a .grp file, and also dumps textures from the corresponding vram file

Supports: Most if not All Armor.ps3 files and Wrench.ps3 files

Known Issues: Doesn't support dumping bone positions. the reason for this is that the armor.ps3 files seemingly don't have any skeleton info inside them. i'll add a base skeleton to this later.

# WeightImport.py
Usage: Open the script in blender, make sure all submeshes have been selected in order of last to first (so 4 - 0), then join them into a single mesh, and re-select it. For simpler use, don't enable submesh splitting when dumping with the Armor Ripper script, as you only have to import the grp on the one mesh imported.

Run the script and choose the corresponding .grp file generated for the armor file, it should correctly assign bone weights.

Known working in blender 2.79, not sure about newer versions

# GroupNames.py
Usage: Open the script in blender, and with a mesh selected, run it. it should change all known group names in the selected object to a more descriptive name (e.g. group 72 becomes the L_Shoulder group)

Known working in blender 2.79, not sure about newer versions
