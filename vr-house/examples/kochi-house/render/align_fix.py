"""Headless: blender -b launch_exterior_cycles.blend --python align_fix.py
Fixes found by align_check.py:
 1. GF_Floor wrongly covered the car porch -> cut it to the house rooms only (porch keeps its ground-level floor)
 2. GlowPorch (porch ceiling light) sat inside the children's bedroom above the first floor -> move it under the slab
 3. ground-floor furniture sat 5 cm into the floor -> raise; sit-out pieces 20 cm into the sit-out -> raise
 4. the car sits on the porch floor"""
import bpy
from mathutils import Vector

sc = bpy.context.scene


def fcurves_of(obj):
    ad = obj.animation_data
    if not ad or not ad.action:
        return []
    act = ad.action
    fcs = list(getattr(act, "fcurves", []) or [])
    if not fcs and hasattr(act, "layers"):
        fcs = [fc for layer in act.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]
    return fcs


def shift_z_keys(obj, dz):
    moved = False
    for fc in fcurves_of(obj):
        if fc.data_path == "location" and fc.array_index == 2:
            for kp in fc.keyframe_points:
                kp.co.y += dz
                kp.handle_left.y += dz
                kp.handle_right.y += dz
            moved = True
    if not moved:
        obj.location.z += dz


# 1. GF_Floor: keep x 2.885..10 full depth, add x 0..2.885 only south of the porch (y < 8.75)
fl = sc.objects["GF_Floor"]
ws = [fl.matrix_world @ v.co for v in fl.data.vertices]
x0, x1 = min(v.x for v in ws), max(v.x for v in ws)
y0, y1 = min(v.y for v in ws), max(v.y for v in ws)
inv = fl.matrix_world.inverted()
for v in fl.data.vertices:
    w = fl.matrix_world @ v.co
    if w.x < (x0 + x1) / 2:
        w.x = 2.885
    v.co = inv @ w
fl2 = fl.copy()
fl2.data = fl.data.copy()
fl2.name = "GF_Floor_South"
sc.collection.objects.link(fl2)
for v in fl2.data.vertices:
    w = fl2.matrix_world @ v.co
    w.x = x0 if w.x < 3.0 else 2.885          # copy spans 2.885..x1 after the cut: map it to x0..2.885
    w.y = y0 if w.y < (y0 + y1) / 2 else 8.75
    v.co = fl2.matrix_world.inverted() @ w
print("KX floor split")

# 2. porch ceiling light: under the first-floor slab (slab bottom 3.5)
gp = sc.objects.get("GlowPorch")
if gp:
    zs = [(gp.matrix_world @ Vector(c)).z for c in gp.bound_box]
    sc.frame_set(720)
    zs = [(gp.matrix_world @ Vector(c)).z for c in gp.bound_box]
    shift_z_keys(gp, 3.47 - max(zs))
    print("KX GlowPorch moved by", round(3.47 - max(zs), 3))

# 3 + 4. furniture
gf = sc.objects["FurnitureGF"]
sitout = {"modern_arm_chair_01", "modern_arm_chair_01.001", "side_table_01.004"}
n = 0
for r in gf.children:
    dz = 0.05
    if r.name in sitout:
        dz += 0.20
    r.location.z += dz
    n += 1
# the car (rigged root Sketchfab_model.018 in gf_props): onto the porch floor top (0.1)
sc.frame_set(720)
car = sc.objects.get("Sketchfab_model.018")
if car:
    pts = []
    for o in [car] + list(car.children_recursive):
        if o.type == 'MESH':
            pts += [(o.matrix_world @ Vector(c)).z for c in o.bound_box]
    car.location.z += 0.10 - min(pts)
    print("KX car raised by", round(0.10 - min(pts), 3))
print("KX furniture adjusted", n)
bpy.ops.wm.save_mainfile()
print("KX saved")
