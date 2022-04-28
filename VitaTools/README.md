## RaCTrilogy-PS3-VitaTools

Note: textures need to be converted to gxt using psp2gxt in order for the model to convert correctly

Aditionally, you'll want to change the texture names in the OBJ's mtl to end with gxt as well

And on top of that, make sure to keep everything as one mesh when converting to obj

When importing an OBJ into blender, make sure to enable keep vertex order or something like that

Do the same when exporting the OBJ to make sure the vertex order is the same in the grp file as in the obj

Also, materials and textures should follow a specific naming scheme in the model

armor(ArmorNumber)\_(TextureIndex) for textured meshes, no support for reflection meshes yet.
