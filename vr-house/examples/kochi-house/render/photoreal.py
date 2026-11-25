"""Headless: blender -b launch_exterior_cycles.blend --python photoreal.py -- [--test]
Photoreal details for the Cycles exterior: real grass blades on the near lawns, neighbour houses with plinths, porches,
pillars, doors and parapet copings, a calmer daytime sky exposure."""
import math
import random
import sys
import time
import bpy
from mathutils import Vector

random.seed(31)
sc = bpy.context.scene


def mat(name, color, rough=0.8):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    return m


def box(name, x1, x2, y1, y2, z1, z2, m):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2))
    o = bpy.context.object
    o.name = name
    o.scale = (x2 - x1, y2 - y1, z2 - z1)
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(m)
    return o


# ---------------------------------------------------------------------------------------------------------------
# neighbour houses: plinth band, parapet coping, a front porch with two pillars, a door, a step
plinth = mat("P_Plinth", (0.16, 0.15, 0.14), 0.7)
coping = bpy.data.materials.get("R_CompoundWall") or mat("P_Coping", (0.7, 0.7, 0.68))
door = mat("P_DoorTeak", (0.22, 0.12, 0.06), 0.45)
roofm = bpy.data.materials.get("R_RoofTiles")
nb = 0
for i in range(12):
    body = sc.objects.get(f"NH{i}_body")
    if not body:
        continue
    ps = [body.matrix_world @ Vector(c) for c in body.bound_box]
    x1, x2 = min(p.x for p in ps), max(p.x for p in ps)
    y1, y2 = min(p.y for p in ps), max(p.y for p in ps)
    h = max(p.z for p in ps)
    box(f"NH{i}_plinth", x1 - 0.08, x2 + 0.08, y1 - 0.08, y2 + 0.08, 0, 0.55, plinth)
    if sc.objects.get(f"NH{i}_parapet"):
        box(f"NH{i}_coping", x1 - 0.06, x2 + 0.06, y1 - 0.06, y2 + 0.06, h + 0.6, h + 0.68, coping)
    # porch faces the road (north) for houses south of the road, south for houses north of it
    front_north = (y1 + y2) / 2 < 21
    fy = y2 if front_north else y1
    s = 1 if front_north else -1
    px1, px2 = x1 + (x2 - x1) * 0.15, x1 + (x2 - x1) * 0.55
    depth = 2.2
    py1, py2 = sorted((fy, fy + s * depth))
    box(f"NH{i}_porchfloor", px1, px2, py1, py2, 0, 0.45, plinth)
    box(f"NH{i}_porchroof", px1 - 0.2, px2 + 0.2, min(py1, py2) - (0 if front_north else 0.3), max(py1, py2) + (0.3 if front_north else 0), 2.95, 3.12,
        bpy.data.objects[f"NH{i}_body"].active_material)
    if roofm and random.random() < 0.6:
        box(f"NH{i}_porchtiles", px1 - 0.25, px2 + 0.25, min(py1, py2) - 0.05, max(py1, py2) + 0.3, 3.12, 3.2, roofm)
    for px in (px1 + 0.15, px2 - 0.15):
        bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.13, depth=2.5, location=(px, fy + s * (depth - 0.25), 0.45 + 1.25))
        c = bpy.context.object
        c.name = f"NH{i}_pillar"
        c.data.materials.append(bpy.data.objects[f"NH{i}_body"].active_material)
    dx = (px1 + px2) / 2
    box(f"NH{i}_door", dx - 0.5, dx + 0.5, fy - 0.02 if front_north else fy - 0.04, fy + 0.04 if front_north else fy + 0.02, 0.45, 2.55, door)
    nb += 1
print("KX neighbour details", nb)

# ---------------------------------------------------------------------------------------------------------------
# real grass: hair particles on the lawns near the camera path (house lawn + a 70 m patch around the street)
grass_mat = bpy.data.materials.new("P_GrassBlades")
grass_mat.use_nodes = True
nt = grass_mat.node_tree
nt.nodes.clear()
out = nt.nodes.new("ShaderNodeOutputMaterial")
pb = nt.nodes.new("ShaderNodeBsdfPrincipled")
info = nt.nodes.new("ShaderNodeHairInfo")
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].color = (0.05, 0.09, 0.02, 1)
ramp.color_ramp.elements[1].color = (0.28, 0.36, 0.1, 1)
nt.links.new(info.outputs["Intercept"], ramp.inputs["Fac"])
nt.links.new(ramp.outputs["Color"], pb.inputs["Base Color"])
pb.inputs["Roughness"].default_value = 0.6
nt.links.new(pb.outputs[0], out.inputs[0])


def grass_patch(name, x1, x2, y1, y2, count, length):
    bpy.ops.mesh.primitive_plane_add(size=1, location=((x1 + x2) / 2, (y1 + y2) / 2, 0.012))
    p = bpy.context.object
    p.name = name
    p.scale = (x2 - x1, y2 - y1, 1)
    bpy.ops.object.transform_apply(scale=True)
    p.data.materials.append(bpy.data.materials.get("R_Grass"))
    p.data.materials.append(grass_mat)
    p.modifiers.new("grass", 'PARTICLE_SYSTEM')
    ps = p.particle_systems[0].settings
    ps.type = 'HAIR'
    ps.count = count
    ps.hair_length = length
    ps.use_advanced_hair = True
    ps.material_slot = "P_GrassBlades"
    ps.render_type = 'PATH'
    ps.display_step = 2
    ps.render_step = 3
    ps.child_type = 'INTERPOLATED'
    ps.rendered_child_count = 12
    ps.child_length = 0.9
    ps.child_length_threshold = 0.3
    ps.roughness_1 = 0.08
    ps.roughness_endpoint = 0.06
    ps.normal_factor = 0.05
    ps.tangent_factor = 0.01
    ps.factor_random = 0.04
    ps.brownian_factor = 0.004
    ps.root_radius = 0.0012 * 1
    ps.tip_radius = 0.0
    ps.radius_scale = 1.0
    try:
        ps.hair_step = 4
    except Exception:
        pass
    p.visible_shadow = True
    return p


# skip hard surfaces: the patches are only where it is lawn (the house lawn is laid out by the plinth/paths on top)
grass_patch("Grass_HouseLawn", -1.0, 10.8, -1.3, 16.6, 22000, 0.07)
grass_patch("Grass_West", -30, -1.3, -26, 16.4, 30000, 0.09)
grass_patch("Grass_East", 11.1, 40, -26, 16.4, 30000, 0.09)
grass_patch("Grass_North", -30, 40, 25.2, 46, 26000, 0.09)
print("KX grass patches 4")

# ---------------------------------------------------------------------------------------------------------------
# calmer day sky so the clouds keep their shape; sun a touch softer
world = sc.world
for n in world.node_tree.nodes:
    if n.type == 'BACKGROUND' and n.inputs["Color"].is_linked:
        src = n.inputs["Color"].links[0].from_node
        if src.type == 'TEX_ENVIRONMENT' and "kloofendal" in src.image.name:
            act = world.node_tree.animation_data.action if world.node_tree.animation_data else None
            fcs = []
            if act is not None:
                fcs = list(getattr(act, "fcurves", []) or [])
                if not fcs and hasattr(act, "layers"):
                    fcs = [fc for layer in act.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]
            for fc in fcs:
                if f'nodes["{n.name}"]' in fc.data_path:
                    for kp in fc.keyframe_points:
                        kp.co.y *= 0.62
                        kp.handle_left.y *= 0.62
                        kp.handle_right.y *= 0.62
            print("KX day sky scaled")
sc.render.filepath = r"D:\Kochi-Residence-Interior\video\blender\ext_cyc\f_"
bpy.ops.wm.save_as_mainfile(filepath=r"D:\Kochi-Residence-Interior\video\blender\launch_exterior_cycles.blend")
print("KX saved")

if "--test" in sys.argv:
    for f in (175, 520, 790):
        sc.frame_set(f)
        sc.render.filepath = rf"D:\Kochi-Residence-Interior\video\blender\pr_{f:04d}.jpg"
        t = time.time()
        bpy.ops.render.render(write_still=True)
        print("KX frame", f, "%.1f s" % (time.time() - t))
