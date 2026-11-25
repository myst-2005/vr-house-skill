"""Blender helpers for placing VR props in plan coordinates (x east, y north, z up; FF = 3.15).

exec() this file inside Blender; it stores the helpers in bpy.app.driver_namespace["vr"].
Every freshly imported object (no "vr" custom property yet) is treated as the new model.
"""
import math
import bpy
from mathutils import Matrix, Vector

FF = 3.15


def scene():
    sc = bpy.data.scenes.get("VRProps")
    if sc is None:
        sc = bpy.data.scenes.new("VRProps")
    bpy.context.window.scene = sc
    return sc


def roots(objs):
    s = set(objs)
    return [o for o in objs if o.parent not in s]


def bbox(objs):
    pts = []
    for o in objs:
        if o.type == 'MESH' and o.data.vertices:
            pts += [o.matrix_world @ Vector(c) for c in o.bound_box]
    if not pts:
        return None
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx


def new_objects():
    return [o for o in bpy.context.scene.objects if "vr" not in o.keys()]


def info():
    objs = new_objects()
    b = bbox(objs)
    if not b:
        return "no new mesh objects"
    mn, mx = b
    d = mx - mn
    faces = sum(len(o.data.polygons) for o in objs if o.type == 'MESH')
    return f"{len(objs)} objs, dims {d.x:.2f} x {d.y:.2f} x {d.z:.2f}, faces {faces}"


def tag(objs, name):
    for o in objs:
        o["vr"] = name


def transform(objs, M):
    for o in roots(objs):
        o.matrix_world = M @ o.matrix_world
    bpy.context.view_layer.update()


def clean(objs):
    """Freeze rigged parts where they are (drop constraints) and remove helper curves/paths."""
    bpy.context.view_layer.update()
    for o in objs:
        if o.constraints:
            mw = o.matrix_world.copy()
            for c in list(o.constraints):
                o.constraints.remove(c)
            o.matrix_world = mw
    keep = []
    for o in objs:
        if o.type in ('CURVE', 'ARMATURE') and not any(ch.type == 'MESH' for ch in o.children_recursive):
            bpy.data.objects.remove(o, do_unlink=True)
        else:
            keep.append(o)
    bpy.context.view_layer.update()
    return keep


def place(name, cx, cy, z, rot=0.0, width=None, depth=None, height=None, length=None, max_faces=None, objs=None):
    """Rotate (deg, CCW seen from above) about the model centre, scale uniformly to the given size, then
    put the footprint centre at (cx, cy) with the base at z. width = x-extent after rotation,
    depth = y-extent after rotation, length = longest horizontal side, height = z-extent."""
    objs = clean(objs if objs is not None else new_objects())
    mn, mx = bbox(objs)
    c = (mn + mx) / 2
    transform(objs, Matrix.Translation((c.x, c.y, 0)) @ Matrix.Rotation(math.radians(rot), 4, 'Z') @ Matrix.Translation((-c.x, -c.y, 0)))
    mn, mx = bbox(objs)
    d = mx - mn
    s = None
    if width:
        s = width / d.x
    elif depth:
        s = depth / d.y
    elif length:
        s = length / max(d.x, d.y)
    elif height:
        s = height / d.z
    if s:
        c = (mn + mx) / 2
        transform(objs, Matrix.Translation((c.x, c.y, mn.z)) @ Matrix.Scale(s, 4) @ Matrix.Translation((-c.x, -c.y, -mn.z)))
    mn, mx = bbox(objs)
    c = (mn + mx) / 2
    transform(objs, Matrix.Translation((cx - c.x, cy - c.y, z - mn.z)))
    if max_faces:
        decimate(objs, max_faces)
    tag(objs, name)
    mn, mx = bbox(objs)
    return f"{name}: x {mn.x:.2f}-{mx.x:.2f}  y {mn.y:.2f}-{mx.y:.2f}  z {mn.z:.2f}-{mx.z:.2f}"


def decimate(objs, max_faces):
    meshes = [o for o in objs if o.type == 'MESH']
    total = sum(len(o.data.polygons) for o in meshes)
    if total <= max_faces:
        return
    r = max(0.05, max_faces / total)
    for o in meshes:
        if len(o.data.polygons) > 300:
            m = o.modifiers.new("vr_decimate", "DECIMATE")
            m.ratio = r


def copy(name, new_name, cx, cy, z, rot=0.0):
    """Duplicate an already placed model (shared mesh data) and place the copy."""
    src = [o for o in bpy.context.scene.objects if o.get("vr") == name]
    mapping = {}
    for o in src:
        n = o.copy()
        bpy.context.scene.collection.objects.link(n)
        mapping[o] = n
    for o, n in mapping.items():
        if o.parent in mapping:
            n.parent = mapping[o.parent]
            n.matrix_parent_inverse = o.matrix_parent_inverse.copy()
    objs = list(mapping.values())
    for o in objs:
        o["vr"] = "__tmp"
    return place(new_name, cx, cy, z, rot, objs=objs)


def fit(name, x1, x2, y1, y2, z1, z2):
    """Stretch an already placed model so its bounding box exactly fills the given box (built-in joinery)."""
    objs = [o for o in bpy.context.scene.objects if o.get("vr") == name]
    mn, mx = bbox(objs)
    d = mx - mn
    S = Matrix.Diagonal(((x2 - x1) / d.x, (y2 - y1) / d.y, (z2 - z1) / d.z, 1.0))
    transform(objs, Matrix.Translation((x1, y1, z1)) @ S @ Matrix.Translation((-mn.x, -mn.y, -mn.z)))
    mn, mx = bbox(objs)
    return f"{name}: x {mn.x:.2f}-{mx.x:.2f}  y {mn.y:.2f}-{mx.y:.2f}  z {mn.z:.2f}-{mx.z:.2f}"


def remove(name):
    for o in [o for o in bpy.context.scene.objects if o.get("vr") == name]:
        bpy.data.objects.remove(o, do_unlink=True)


bpy.app.driver_namespace["vr"] = dict(scene=scene, info=info, place=place, copy=copy, remove=remove, bbox=bbox, clean=clean, fit=fit,
                                      new_objects=new_objects, decimate=decimate, FF=FF)
