"""Headless: blender -b vr/Kochi_House_VR.blend --python tools/export_unity_gltf.py
Exports the assembled house as .gltf + separate JPG/PNG textures straight into the Unity project, so Unity's
own texture importer compresses them (ASTC on Quest) instead of glTFast storing them uncompressed."""
import os
import bpy

OUT_DIR = r"D:\Kochi-Residence-Interior\unity\KochiHouseVR\Assets\Models\KochiHouse"
os.makedirs(OUT_DIR, exist_ok=True)
kw = dict(filepath=os.path.join(OUT_DIR, "KochiHouse.gltf"), export_format='GLTF_SEPARATE', export_texture_dir="textures",
          use_selection=False, export_apply=True, export_yup=True, export_texcoords=True, export_normals=True,
          export_extras=False, export_cameras=False, export_lights=False, export_animations=False,
          export_image_format='JPEG', export_draco_mesh_compression_enable=False)
try:
    bpy.ops.export_scene.gltf(**kw, export_image_quality=85)
except TypeError:
    bpy.ops.export_scene.gltf(**kw)
n = len(os.listdir(os.path.join(OUT_DIR, "textures")))
size = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(OUT_DIR) for f in fs)
print("KOCHI_EXPORT gltf", n, "textures", round(size / 1e6, 1), "MB")
