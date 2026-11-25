"""Headless: blender -b launch_exterior_real.blend --python realism2.py -- [--test]
Adds the real interior furniture (visible through the glass, rising with each floor) and a distant neighbourhood
(houses and coconut palms) so the horizon is not an empty field."""
import math
import os
import random
import sys
import time
import bpy
from mathutils import Vector

random.seed(23)
V = r"D:\Kochi-Residence-Interior\vr\models"
TEST = "--test" in sys.argv
sc = bpy.context.scene
GF_Z, FF_Z = 0.4, 3.7          # exterior model floor tops (interior model: 0 and 3.15)
INT_FF = 3.15

# placeholder furniture boxes in the exterior model go; the real pieces replace them
for n in ("MasterBed", "MasterHeadboard", "KidsBed", "LoungeSofa", "LivingSofa", "DiningTable"):
    o = sc.objects.get(n)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)


def import_pack(path, offset, parent):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    for o in new:
        if o.parent is None:
            o.location = (o.location.x + offset[0], o.location.y + offset[1], o.location.z + offset[2])
            o.parent = parent
    return new


def floor_empty(name):
    e = bpy.data.objects.new(name, None)
    sc.collection.objects.link(e)
    return e


gf = floor_empty("FurnitureGF")
ff = floor_empty("FurnitureFF")
n = 0
n += len(import_pack(os.path.join(V, "living.glb"), (0, 0, GF_Z), gf))
n += len(import_pack(os.path.join(V, "gf_props.glb"), (0, 0, GF_Z), gf))
n += len(import_pack(os.path.join(V, "master.glb"), (-80, 0, FF_Z), ff))
n += len(import_pack(os.path.join(V, "gaming.glb"), (-40, 0, FF_Z), ff))
n += len(import_pack(os.path.join(V, "ff_props.glb"), (0, 0, FF_Z - INT_FF), ff))
print("KX furniture objects", n)

# the furniture rises with its floor (same drop and ease as the walls)
for e, f0 in ((gf, 330), (ff, 452)):
    e.location.z = -9.5
    e.keyframe_insert("location", index=2, frame=f0)
    e.location.z = 0
    e.keyframe_insert("location", index=2, frame=f0 + 36)
    act = e.animation_data.action
    fcs = getattr(act, "fcurves", None)
    if fcs is None:  # Blender 5 layered actions
        fcs = [fc for layer in act.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]
    for fc in fcs:
        for kp in fc.keyframe_points:
            kp.interpolation = 'BACK'
            kp.easing = 'EASE_OUT'
            kp.back = 0.8

# ---------------------------------------------------------------------------------------------------------------
# distant neighbourhood: a palm proto (collection) instanced across the horizon, plus simple houses
palm_objs = []
tops = {}
for o in sc.objects:
    if o.name.startswith("PalmTrunk") and o.type == 'MESH':
        ps = [o.matrix_world @ Vector(c) for c in o.bound_box]
        p = Vector((sum(q.x for q in ps) / 8, sum(q.y for q in ps) / 8, 0))
        tops.setdefault((round(p.x / 1.5), round(p.y / 1.5)), []).append((o, p))
key = max(tops, key=lambda k: len(tops[k]))
trunks = [o for o, _ in tops[key]]
cx = sum(p.x for _, p in tops[key]) / len(tops[key])
cy = sum(p.y for _, p in tops[key]) / len(tops[key])
fronds = [o for o in sc.objects if o.type == 'MESH' and o.active_material and o.active_material.name.startswith("R_Frond") and not o.hide_render
          and (o.location.xy - Vector((cx, cy))).length < 2.5]
proto = bpy.data.collections.new("PalmProto")
for o in trunks + fronds:
    proto.objects.link(o)
proto.instance_offset = (cx, cy, 0)
placed = 0
tries = 0
while placed < 230 and tries < 5000:
    tries += 1
    r = random.uniform(42, 220)
    a = random.uniform(0, 2 * math.pi)
    x, y = 5 + r * math.cos(a), 8 + r * math.sin(a)
    if 15 < y < 28:            # keep the road clear
        continue
    e = bpy.data.objects.new(f"FarPalm{placed}", None)
    e.instance_type = 'COLLECTION'
    e.instance_collection = proto
    e.location = (x, y, 0)
    e.rotation_euler.z = random.uniform(0, 6.28)
    s = random.uniform(0.85, 1.3)
    e.scale = (s, s, s)
    sc.collection.objects.link(e)
    placed += 1
print("KX far palms", placed, "proto trunks", len(trunks), "fronds", len(fronds))

roof = bpy.data.materials.get("R_RoofTiles")
plasters = [m for m in bpy.data.materials if m.name.startswith("R_Plaster")]
hn = 0
tries = 0
while hn < 70 and tries < 4000:
    tries += 1
    r = random.uniform(40, 170)
    a = random.uniform(0, 2 * math.pi)
    x, y = 5 + r * math.cos(a), 8 + r * math.sin(a)
    if 12 < y < 32:
        continue
    w, d = random.uniform(8, 12), random.uniform(8, 11)
    fl = random.choice((1, 1, 2))
    h = 3.2 * fl
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, h / 2))
    b = bpy.context.object
    b.name = f"FarHouse{hn}"
    b.scale = (w, d, h)
    b.rotation_euler.z = random.choice((0, math.pi / 2)) + random.uniform(-0.1, 0.1)
    b.data.materials.append(random.choice(plasters))
    if random.random() < 0.7:
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1, depth=1, location=(x, y, h + 1.1), rotation=(0, 0, math.pi / 4 + b.rotation_euler.z))
        rf = bpy.context.object
        rf.name = f"FarRoof{hn}"
        rf.scale = ((w + 1.2) * 0.72, (d + 1.2) * 0.72, 2.2)
        rf.data.materials.append(roof)
    hn += 1
print("KX far houses", hn)

sc.render.filepath = r"D:\Kochi-Residence-Interior\video\blender\ext_real\f_"
sc.eevee.taa_render_samples = 24
bpy.ops.wm.save_as_mainfile(filepath=r"D:\Kochi-Residence-Interior\video\blender\launch_exterior_real.blend")
print("KX saved")

if TEST:
    for f in (520, 985):
        sc.frame_set(f)
        sc.render.filepath = rf"D:\Kochi-Residence-Interior\video\blender\real2_{f:04d}.jpg"
        t = time.time()
        bpy.ops.render.render(write_still=True)
        print("KX test frame", f, "%.1f s" % (time.time() - t))
