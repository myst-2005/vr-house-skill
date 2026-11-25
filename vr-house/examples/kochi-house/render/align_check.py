"""Headless: blender -b launch_exterior_cycles.blend --python align_check.py -- [--fix]
Checks every piece of interior furniture inside the exterior scene at the finished pose:
  - floor gap: distance from the piece's lowest point to the surface directly under it (raycast, furniture excluded)
  - wall overlap: how far its box pushes into an exterior wall, glass or frame of the house
With --fix, small floor gaps (sunk or floating up to 0.6 m) are snapped onto the surface and saved."""
import sys
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sc = bpy.context.scene
FIX = "--fix" in sys.argv
sc.frame_set(720)                       # everything has risen by now
dg = bpy.context.evaluated_depsgraph_get()

furn_roots = []
for e in (sc.objects.get("FurnitureGF"), sc.objects.get("FurnitureFF")):
    if e:
        furn_roots += [(c, e.name) for c in e.children]
furn_set = set()
for r, _ in furn_roots:
    furn_set.add(r)
    furn_set.update(r.children_recursive)


def wbox(objs):
    pts = []
    for o in objs:
        if o.type == 'MESH' and len(o.data.vertices):
            pts += [o.matrix_world @ Vector(c) for c in o.bound_box]
    if not pts:
        return None
    return (Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
            Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))))


# BVH of the house + site (not furniture, not grass hair, not far scenery)
verts, polys = [], []
skip = ("Grass_", "FarPalm", "FarHouse", "FarRoof", "SunDisc", "MoonDisc", "FP_", "NH", "SL_", "Palm", "Frond", "R_Frond")
house_parts = []
for o in sc.objects:
    if o.type != 'MESH' or o in furn_set or o.name.startswith(skip) or o.hide_render:
        continue
    b = wbox([o])
    if not b or b[0].x < -2 or b[1].x > 12 or b[0].y < -2 or b[1].y > 17:
        if not o.name.startswith(("Ground", "Lawn", "Driveway", "SitPath", "Porch", "Plinth", "GF_", "Terrace")):
            continue
    me = o.evaluated_get(dg).to_mesh()
    base = len(verts)
    verts += [o.matrix_world @ v.co for v in me.vertices]
    polys += [[base + i for i in p.vertices] for p in me.polygons]
    o.evaluated_get(dg).to_mesh_clear()
    house_parts.append(o)
bvh = BVHTree.FromPolygons(verts, polys)
walls = [o for o in house_parts if o.name[:2] in ("Sw", "Ss", "Sl", "Wg", "Ew", "Es", "El", "Nw", "Nl", "Of", "LR") or o.name.startswith(
    ("Porch", "Front", "Rear", "FF_Shell", "FF_Partition", "LivingFrame", "Ng", "Eg", "Sg", "Cut", "FFGlass", "FFFrame", "Ed", "LRd", "OffN"))]
wall_boxes = [(o.name, wbox([o])) for o in walls]

report, fixed = [], 0
for root, floor_name in furn_roots:
    objs = [root] + list(root.children_recursive)
    b = wbox(objs)
    if not b:
        continue
    mn, mx = b
    size = mx - mn
    if size.x * size.y < 0.01:
        continue
    # sample the floor at 5 points under the piece; take the highest surface below the piece's top
    hits = []
    for fx, fy in ((0.5, 0.5), (0.2, 0.2), (0.8, 0.2), (0.2, 0.8), (0.8, 0.8)):
        x, y = mn.x + size.x * fx, mn.y + size.y * fy
        loc, nrm, idx, dist = bvh.ray_cast(Vector((x, y, mx.z + 0.05)), Vector((0, 0, -1)), 12)
        if loc is not None:
            hits.append(loc.z)
    floor_z = max(hits) if hits else None
    gap = (mn.z - floor_z) if floor_z is not None else None
    # wall overlap
    worst, wname = 0.0, ""
    for nm, wb in wall_boxes:
        if not wb:
            continue
        ox = min(mx.x, wb[1].x) - max(mn.x, wb[0].x)
        oy = min(mx.y, wb[1].y) - max(mn.y, wb[0].y)
        oz = min(mx.z, wb[1].z) - max(mn.z, wb[0].z)
        if ox > 0 and oy > 0 and oz > 0:
            pen = min(ox, oy)
            if pen > worst:
                worst, wname = pen, nm
    name = root.name[:34]
    flag = []
    if gap is not None and abs(gap) > 0.03 and abs(gap) < 0.6:
        flag.append(f"floor gap {gap:+.2f} m")
    if gap is not None and gap >= 0.6:
        flag.append(f"high above floor {gap:.2f} m (wall-mounted or stacked?)")
    if gap is None:
        flag.append("no floor under it")
    if worst > 0.04:
        flag.append(f"into wall {wname} by {worst:.2f} m")
    if flag:
        report.append(f"{floor_name:12s} {name:36s} x {mn.x:5.2f}-{mx.x:5.2f} y {mn.y:5.2f}-{mx.y:5.2f} z {mn.z:5.2f}-{mx.z:5.2f}  " + "; ".join(flag))
    if FIX and gap is not None and 0.03 < abs(gap) < 0.6:
        root.location.z -= gap / (root.parent.matrix_world.to_scale().z if root.parent else 1)
        fixed += 1

print("KX checked", len(furn_roots), "pieces;", len(report), "flagged")
for r in report:
    print("KX", r)
if FIX:
    bpy.ops.wm.save_mainfile()
    print("KX fixed", fixed, "and saved")
