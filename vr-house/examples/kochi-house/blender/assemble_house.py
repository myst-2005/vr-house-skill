"""Headless: blender -b --python tools/assemble_house.py
Builds vr/Kochi_House_VR.blend (one scene: house shell + every furniture pack, in plan coordinates)
and exports vr/export/KochiHouse.glb for Unity. Texture UVs are left untouched (Unity makes lightmap UVs)."""
import os
import bpy

V = r"D:\Kochi-Residence-Interior\vr"
FF = 3.15
bpy.ops.wm.read_homefile(use_empty=True)
sc = bpy.context.scene
sc.name = "KochiHouse"
parts = [("house_shell", os.path.join(V, "export", "house_shell.glb"), (0, 0, 0)),
         ("living", os.path.join(V, "models", "living.glb"), (0, 0, 0)),
         ("master", os.path.join(V, "models", "master.glb"), (-80, 0, FF)),
         ("gaming", os.path.join(V, "models", "gaming.glb"), (-40, 0, FF)),
         ("gf_props", os.path.join(V, "models", "gf_props.glb"), (0, 0, 0)),
         ("ff_props", os.path.join(V, "models", "ff_props.glb"), (0, 0, 0))]
for name, path, off in parts:
    col = bpy.data.collections.new(name)
    sc.collection.children.link(col)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    for o in new:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        col.objects.link(o)
        if o.parent is None:
            o.location = (o.location.x + off[0], o.location.y + off[1], o.location.z + off[2])
        if name == "house_shell" and not o.name.startswith("SHELL_"):
            o.name = "SHELL_" + o.name
    print("KOCHI_PART", name, len(new))

# WebP -> PNG (glTFast can't read WebP), max 1024 px
TEX = os.path.join(V, "export", "tex")
os.makedirs(TEX, exist_ok=True)
for i, im in enumerate(bpy.data.images):
    if im.source != 'FILE' or im.size[0] == 0:
        continue
    if im.file_format == 'WEBP' or im.filepath.lower().endswith('.webp') or im.filepath == '':
        path = os.path.join(TEX, f"img_{i:04d}.png")
        im.filepath_raw = path
        im.file_format = 'PNG'
        im.save()
        if im.packed_file:
            im.unpack(method='REMOVE')
        im.filepath = path
        im.reload()
for im in bpy.data.images:
    if im.size[0] > 1024 or im.size[1] > 1024:
        w, h = im.size
        s = 1024 / max(w, h)
        im.scale(max(1, int(w * s)), max(1, int(h * s)))

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(V, "Kochi_House_VR.blend"))
OUT = os.path.join(V, "export", "KochiHouse.glb")
kw = dict(filepath=OUT, export_format='GLB', use_selection=False, export_apply=True, export_yup=True,
          export_texcoords=True, export_normals=True, export_extras=False, export_cameras=False, export_lights=False,
          export_animations=False, export_image_format='JPEG', export_draco_mesh_compression_enable=False)
try:
    bpy.ops.export_scene.gltf(**kw, export_image_quality=85)
except TypeError:
    bpy.ops.export_scene.gltf(**kw)
data = open(OUT, 'rb').read()
print("KOCHI_EXPORT", round(len(data) / 1e6, 1), "MB", "webp" if b"EXT_texture_webp" in data else "no-webp")
