"""Run headless: blender -b vr/Kochi_House_VR.blend --python tools/export_house_glb.py
Exports the whole house (shell + all furniture) for Unity: JPEG/PNG textures only (no WebP), max 1024 px."""
import os
import bpy

OUT = r"D:\Kochi-Residence-Interior\vr\export\KochiHouse.glb"
TEX = r"D:\Kochi-Residence-Interior\vr\export\tex"
os.makedirs(TEX, exist_ok=True)
for i, im in enumerate(bpy.data.images):
    if im.source != 'FILE' or im.size[0] == 0:
        continue
    if im.file_format == 'WEBP' or im.filepath.lower().endswith('.webp') or im.filepath == '':
        # rewrite WebP textures as real PNG files on disk, then point the image at them
        path = os.path.join(TEX, f"img_{i:04d}.png")
        im.filepath_raw = path
        im.file_format = 'PNG'
        im.save()
        if im.packed_file:
            im.unpack(method='REMOVE')
        im.filepath = path
        im.reload()
# Unity makes its own lightmap UVs; keep only each mesh's texture UV map, and make sure it is the active one
for me in bpy.data.meshes:
    for uv in [u for u in me.uv_layers if u.name == "lightmap"]:
        me.uv_layers.remove(uv)
    if len(me.uv_layers):
        me.uv_layers.active_index = 0
        for i, uv in enumerate(me.uv_layers):
            uv.active_render = (i == 0)
for im in bpy.data.images:
    if im.size[0] > 1024 or im.size[1] > 1024:
        w, h = im.size
        s = 1024 / max(w, h)
        im.scale(max(1, int(w * s)), max(1, int(h * s)))
kw = dict(filepath=OUT, export_format='GLB', use_selection=False, export_apply=True, export_yup=True,
          export_texcoords=True, export_normals=True, export_extras=False, export_cameras=False, export_lights=False,
          export_animations=False, export_image_format='JPEG', export_draco_mesh_compression_enable=False)
try:
    bpy.ops.export_scene.gltf(**kw, export_image_quality=85)
except TypeError:
    bpy.ops.export_scene.gltf(**kw)
with open(OUT, 'rb') as f:
    data = f.read()
print("KOCHI_EXPORT", round(len(data) / 1e6, 1), "MB", "webp" if b"EXT_texture_webp" in data else "no-webp")
