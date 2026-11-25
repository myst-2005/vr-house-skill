"""Find image textures that fail to load (Cycles renders them bright pink/magenta) and unplug them,
so each material falls back to its base values. Saves the .blend.

    blender -b scene.blend --python fix_textures.py

In the reference project, imported car models had empty texture slots that turned the wheel rims pink.
"""
import bpy

missing = []
for im in bpy.data.images:
    if im.source not in ('FILE', 'TILED') or im.users == 0:
        continue
    ok = im.has_data
    if not ok:
        try:
            im.reload()
            ok = im.has_data or len(im.pixels) > 0
        except Exception:
            ok = False
    if not ok:
        missing.append(im)
print("missing images:", [(im.name, im.filepath) for im in missing])

unplugged = 0
for m in bpy.data.materials:
    if not m.use_nodes:
        continue
    for n in m.node_tree.nodes:
        if n.type == 'TEX_IMAGE' and (n.image is None or n.image in missing):
            for out in n.outputs:
                for link in list(out.links):
                    m.node_tree.links.remove(link)
                    unplugged += 1
print("unplugged links:", unplugged)
bpy.ops.wm.save_mainfile()
