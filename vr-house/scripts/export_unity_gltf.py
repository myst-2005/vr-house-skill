"""Export the open Blender scene as .gltf + separate JPEG textures, straight into a Unity project.

Usage (headless):
    blender -b House_VR.blend --python export_unity_gltf.py -- <unity_assets_folder> [Name]

Example:
    blender -b vr/House_VR.blend --python scripts/export_unity_gltf.py -- unity/HouseVR/Assets/Models/House House

Why separate textures: glTFast stores textures embedded in a .glb uncompressed (a 1.8 GB Quest build in the
reference project). Separate files go through Unity's own texture importer, which compresses them (ASTC on Quest).
WebP is not readable by glTFast, so textures are written as JPEG here.
"""
import os
import sys

import bpy

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if not args:
    raise SystemExit("usage: blender -b file.blend --python export_unity_gltf.py -- <unity_assets_folder> [Name]")
out_dir = os.path.abspath(args[0])
name = args[1] if len(args) > 1 else "House"
os.makedirs(out_dir, exist_ok=True)

kw = dict(filepath=os.path.join(out_dir, name + ".gltf"), export_format='GLTF_SEPARATE', export_texture_dir="textures",
          use_selection=False, export_apply=True, export_yup=True, export_texcoords=True, export_normals=True,
          export_extras=False, export_cameras=False, export_lights=False, export_animations=False,
          export_image_format='JPEG', export_draco_mesh_compression_enable=False)
try:
    bpy.ops.export_scene.gltf(**kw, export_image_quality=85)
except TypeError:  # older Blender without the quality option
    bpy.ops.export_scene.gltf(**kw)

tex_dir = os.path.join(out_dir, "textures")
n = len(os.listdir(tex_dir)) if os.path.isdir(tex_dir) else 0
size = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(out_dir) for f in fs)
print(f"EXPORT {name}.gltf, {n} textures, {size / 1e6:.1f} MB -> {out_dir}")
