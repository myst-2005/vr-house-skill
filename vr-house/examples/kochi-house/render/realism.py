"""Headless: blender -b launch_exterior.blend --python realism.py -- [--test]
Realism pass on the launch-film exterior: Poly Haven PBR textures, photographed skies (day + sunset) fading to night,
textured coconut palms, real shrubs, Kerala window sunshades, reflective glass, ray tracing, haze, motion blur."""
import math
import os
import random
import sys
import time
import bpy
from mathutils import Vector, Euler

random.seed(5)
PH = r"D:\Kochi-Residence-Interior\video\blender\ph"
TEX = os.path.join(PH, "tex")
TEST = "--test" in sys.argv
sc = bpy.context.scene


def img(path, data=False):
    im = bpy.data.images.load(path, check_existing=True)
    if data:
        im.colorspace_settings.name = "Non-Color"
    return im


def pbr(name, tex, size_m, tint=(1, 1, 1), rough_mul=1.0, bump=1.0, var=0.18):
    """World-space box-projected PBR material (no UVs needed) with large-scale colour variation against tiling."""
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(b.outputs[0], out.inputs[0])
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / size_m,) * 3
    nt.links.new(geo.outputs["Position"], mp.inputs["Vector"])

    def tx(kind, data):
        p = os.path.join(TEX, f"{tex}_{kind}.jpg")
        if not os.path.exists(p):
            return None
        n = nt.nodes.new("ShaderNodeTexImage")
        n.image = img(p, data)
        n.projection = 'BOX'
        n.projection_blend = 0.25
        nt.links.new(mp.outputs[0], n.inputs["Vector"])
        return n

    d = tx("diff", False)
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 0.035 / max(0.2, size_m / 4)
    nt.links.new(geo.outputs["Position"], noise.inputs["Vector"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = 'RGBA'
    mix.blend_type = 'MULTIPLY'
    mix.inputs[0].default_value = 1.0
    if d:
        nt.links.new(d.outputs["Color"], mix.inputs[6])
    else:
        mix.inputs[6].default_value = (*tint, 1)
    ramp = nt.nodes.new("ShaderNodeMapRange")
    ramp.inputs["To Min"].default_value = 1 - var
    ramp.inputs["To Max"].default_value = 1 + var * 0.6
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Value"])
    tintn = nt.nodes.new("ShaderNodeMix")
    tintn.data_type = 'RGBA'
    tintn.blend_type = 'MULTIPLY'
    tintn.inputs[0].default_value = 1.0
    tintn.inputs[7].default_value = (*tint, 1)
    nt.links.new(ramp.outputs[0], mix.inputs[7])
    nt.links.new(mix.outputs[2], tintn.inputs[6])
    nt.links.new(tintn.outputs[2], b.inputs["Base Color"])
    r = tx("rough", True)
    if r:
        mr = nt.nodes.new("ShaderNodeMath")
        mr.operation = 'MULTIPLY'
        mr.inputs[1].default_value = rough_mul
        nt.links.new(r.outputs["Color"], mr.inputs[0])
        nt.links.new(mr.outputs[0], b.inputs["Roughness"])
    n = tx("nor", True)
    if n:
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nm.inputs["Strength"].default_value = bump
        nt.links.new(n.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs[0], b.inputs["Normal"])
    return m


def assign(prefixes, m, exact=False):
    k = 0
    for o in sc.objects:
        if o.type != 'MESH':
            continue
        if (o.name in prefixes) if exact else o.name.startswith(tuple(prefixes)):
            o.data.materials.clear()
            o.data.materials.append(m)
            k += 1
    return k


def retex_material(mat_name, m):
    """Swap a named material everywhere it is used."""
    old = bpy.data.materials.get(mat_name)
    if not old:
        return 0
    k = 0
    for o in sc.objects:
        if o.type == 'MESH':
            for s in o.material_slots:
                if s.material == old:
                    s.material = m
                    k += 1
    return k


# ---------------------------------------------------------------------------------------------------------------
# ground, roads, paving, walls, roofs
grass = pbr("R_Grass", "aerial_grass_rock", 7.0, tint=(0.82, 0.95, 0.72), bump=0.6, var=0.25)
lawn = pbr("R_Lawn", "aerial_grass_rock", 4.0, tint=(0.78, 1.0, 0.66), bump=0.5, var=0.2)
road = pbr("R_Asphalt", "aerial_asphalt_01", 9.0, tint=(0.95, 0.95, 0.95), bump=0.5, var=0.15)
paving = pbr("R_Paving", "rectangular_paving", 2.2, tint=(0.95, 0.92, 0.88), bump=0.6, var=0.12)
cw_conc = pbr("R_CompoundWall", "concrete_wall_006", 2.5, tint=(0.95, 0.93, 0.9), bump=0.5, var=0.15)
roof = pbr("R_RoofTiles", "clay_roof_tiles_02", 2.0, tint=(1.0, 0.92, 0.88), bump=1.0, var=0.2)
bark = pbr("R_Bark", "bark_brown_02", 1.2, tint=(0.85, 0.8, 0.72), bump=0.9, var=0.1)
print("KX ground", assign(["Ground", "GroundFar"], grass, exact=True), assign(["Lawn"], lawn, exact=True),
      assign(["Road"], road, exact=True), assign(["Verge", "Driveway", "SitPath"], paving, exact=True))
print("KX bark", retex_material("Bark", bark), "roof", retex_material("N_Terracotta", roof),
      "neighbour cw", retex_material("N_CompoundWall", cw_conc))
# neighbour render: clean or weathered plaster per house, keeping each house's paint colour
for i in range(5):
    old = bpy.data.materials.get(f"N_Render{i}")
    if not old:
        continue
    col = tuple(old.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value[:3])
    new = pbr(f"R_Plaster{i}", "damaged_plaster" if i % 2 else "painted_plaster_wall", 3.0,
              tint=tuple(min(1.0, c * 1.12) for c in col), bump=0.5, var=0.12)
    retex_material(f"N_Render{i}", new)
# the house's own white render keeps its colour, gains a fine plaster surface
wr = bpy.data.materials.get("White_Render")
if wr:
    retex_material("White_Render", pbr("R_HouseRender", "painted_plaster_wall", 2.5, tint=(1.0, 0.99, 0.97), bump=0.25, var=0.05))

# glass: dark, smooth, reflective (ray traced reflections show the sky and the street)
for gname in ("N_WindowDark",):
    g = bpy.data.materials.get(gname)
    if g:
        b = g.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (0.02, 0.025, 0.03, 1)
        b.inputs["Roughness"].default_value = 0.04
        b.inputs["Metallic"].default_value = 0.6

# ---------------------------------------------------------------------------------------------------------------
# Kerala sunshades (chajjas) over every neighbour window, and a dark frame around it
shade_mat = bpy.data.materials.get("R_Plaster0") or cw_conc
frame_mat = bpy.data.materials.new("R_WindowFrame")
frame_mat.use_nodes = True
frame_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.12, 0.1, 0.08, 1)
frame_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.5
n_sh = 0
for o in list(sc.objects):
    if not (o.name.startswith("NH") and "_w" in o.name and o.type == 'MESH'):
        continue
    ps = [o.matrix_world @ Vector(c) for c in o.bound_box]
    x1, x2 = min(p.x for p in ps), max(p.x for p in ps)
    y1, y2 = min(p.y for p in ps), max(p.y for p in ps)
    z2 = max(p.z for p in ps)
    hi = o.name.split("_")[0]
    body = sc.objects.get(f"{hi}_body")
    if not body:
        continue
    bc = body.matrix_world.translation
    thin_x = (x2 - x1) < (y2 - y1)
    if thin_x:
        out_dir = 1 if (x1 + x2) / 2 > bc.x else -1
        cx, cy = (x1 + x2) / 2 + out_dir * 0.28, (y1 + y2) / 2
        dims = (0.56, (y2 - y1) + 0.3, 0.07)
        fdims = (0.06, (y2 - y1) + 0.12, (z2 - min(p.z for p in ps)) + 0.12)
    else:
        out_dir = 1 if (y1 + y2) / 2 > bc.y else -1
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2 + out_dir * 0.28
        dims = ((x2 - x1) + 0.3, 0.56, 0.07)
        fdims = ((x2 - x1) + 0.12, 0.06, (z2 - min(p.z for p in ps)) + 0.12)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, z2 + 0.18))
    s = bpy.context.object
    s.name = f"{hi}_chajja"
    s.scale = dims
    s.data.materials.append(shade_mat)
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x1 + x2) / 2, (y1 + y2) / 2, (z2 + min(p.z for p in ps)) / 2))
    f = bpy.context.object
    f.name = f"{hi}_wframe"
    f.scale = fdims
    f.data.materials.append(frame_mat)
    # the frame sits behind the glass pane: push it 2 cm into the wall
    if thin_x:
        f.location.x -= out_dir * 0.03
    else:
        f.location.y -= out_dir * 0.03
    n_sh += 1
print("KX sunshades", n_sh)

# ---------------------------------------------------------------------------------------------------------------
# coconut palms: keep the trunks (now bark textured), replace the flat fronds with textured, drooping fronds
tops = {}
for o in sc.objects:
    if o.name.startswith("PalmTrunk") and o.type == 'MESH':
        ps = [o.matrix_world @ Vector(c) for c in o.bound_box]
        cx, cy, zt = sum(p.x for p in ps) / 8, sum(p.y for p in ps) / 8, max(p.z for p in ps)
        key = (round(cx / 1.5), round(cy / 1.5))
        best = tops.get(key)
        if best is None or zt > best[2]:
            tops[key] = (cx, cy, zt)
old_fronds = [o for o in sc.objects if o.name.startswith("PalmFrond")]
anim_fronds = [o for o in old_fronds if o.animation_data]
for o in old_fronds:
    bpy.data.objects.remove(o, do_unlink=True)


def frond_material(name, png):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = img(os.path.join(TEX, png))
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(t.outputs["Alpha"], b.inputs["Alpha"])
    b.inputs["Roughness"].default_value = 0.55
    try:
        b.inputs["Subsurface Weight"].default_value = 0.0
        b.inputs["Transmission Weight"].default_value = 0.0
        b.inputs["Coat Weight"].default_value = 0.0
        b.inputs["Specular IOR Level"].default_value = 0.35
    except KeyError:
        pass
    m.surface_render_method = 'DITHERED'
    try:
        m.use_backface_culling = False
    except AttributeError:
        pass
    return m


f_green = frond_material("R_FrondGreen", "palm_frond_green.png")
f_yellow = frond_material("R_FrondYellow", "palm_frond_yellow.png")
f_dry = frond_material("R_FrondDry", "palm_frond_dry.png")


def frond_mesh(name, length, width, droop):
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=14, y_subdivisions=3, size=1)
    o = bpy.context.object
    o.name = name
    me = o.data
    for v in me.vertices:
        u = v.co.x + 0.5                       # 0 at the base .. 1 at the tip
        w = v.co.y
        v.co.x = u * length
        v.co.y = w * width * (1 - 0.35 * u)
        v.co.z = -droop * u * u + 0.25 * length * u * (1 - u) - abs(w) * 0.25 * width   # arch up, droop at the tip, V-fold
    uv = me.uv_layers.active.data
    for poly in me.polygons:
        for li in poly.loop_indices:
            vco = me.vertices[me.loops[li].vertex_index].co
            uv[li].uv = (vco.x / length, 0.5 + vco.y / (width * 1.0 * max(0.65, 1 - 0.35 * vco.x / length)) * 0.5 / 0.5 * 0.5)
    for p in me.polygons:
        p.use_smooth = True
    return o


protos = [frond_mesh("FrondProto0", 3.6, 1.35, 1.2), frond_mesh("FrondProto1", 3.2, 1.25, 1.8), frond_mesh("FrondProto2", 3.0, 1.1, 2.6)]
for p in protos:
    p.data.materials.append(f_green)
dry_proto = frond_mesh("FrondProtoDry", 2.8, 1.0, 3.0)
dry_proto.data.materials.append(f_dry)
yellow_proto = frond_mesh("FrondProtoY", 3.3, 1.25, 1.5)
yellow_proto.data.materials.append(f_yellow)
nf = 0
for (cx, cy, zt) in tops.values():
    n = 26
    for k in range(n):
        az = 2 * math.pi * k / n + random.uniform(-0.12, 0.12)
        ring = k % 3
        if random.random() < 0.12:
            src = dry_proto
            tilt = math.radians(random.uniform(-65, -45))
        else:
            src = random.choice(protos + [yellow_proto])
            tilt = math.radians([28, 8, -14][ring] + random.uniform(-8, 8))
        o = src.copy()                      # linked duplicate: shares mesh data
        sc.collection.objects.link(o)
        o.location = (cx, cy, zt - 0.15)
        o.rotation_euler = Euler((random.uniform(-0.15, 0.15), -tilt, az), 'XYZ')
        o.scale = (random.uniform(0.85, 1.12),) * 3
        nf += 1
for p in protos + [dry_proto, yellow_proto]:
    p.hide_render = True
    p.hide_viewport = True
    p.location = (0, 0, -100)
print("KX palms", len(tops), "fronds", nf)

# shrubs: Poly Haven shrub_02 fitted to each old shrub blob
before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=os.path.join(PH, "models", "shrub_02", "shrub_02_1k.gltf"))
shrub_objs = [o for o in bpy.data.objects if o not in before]
shrub_mesh = next(o for o in shrub_objs if o.type == 'MESH')
shrub_mesh.data.transform(shrub_mesh.matrix_world)
for o in shrub_objs:
    if o is not shrub_mesh:
        bpy.data.objects.remove(o, do_unlink=True)
shrub_mesh.parent = None
from mathutils import Matrix
shrub_mesh.matrix_world = Matrix.Identity(4)
ps = [Vector(c) for c in shrub_mesh.bound_box]
smin = Vector((min(p.x for p in ps), min(p.y for p in ps), min(p.z for p in ps)))
smax = Vector((max(p.x for p in ps), max(p.y for p in ps), max(p.z for p in ps)))
ns = 0
for o in [o for o in sc.objects if o.name.startswith("Shrub") and o.type == 'MESH']:
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    a = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    b = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    s = shrub_mesh.copy()
    sc.collection.objects.link(s)
    fx = (b.x - a.x) * 1.2 / (smax.x - smin.x)
    fz = (b.z - a.z) * 1.5 / (smax.z - smin.z)
    f = max(fx, fz)
    s.scale = (f, f, f)
    s.rotation_euler.z = random.uniform(0, 6.28)
    s.location = Vector(((a.x + b.x) / 2, (a.y + b.y) / 2, 0)) - Vector(((smin.x + smax.x) / 2 * f, (smin.y + smax.y) / 2 * f, smin.z * f))
    bpy.data.objects.remove(o, do_unlink=True)
    ns += 1
# a few more shrubs along the neighbours' compound walls
for i in range(12):
    hb = sc.objects.get(f"NH{i}_body")
    if not hb:
        continue
    ps = [hb.matrix_world @ Vector(c) for c in hb.bound_box]
    x1, x2 = min(p.x for p in ps), max(p.x for p in ps)
    y1, y2 = min(p.y for p in ps), max(p.y for p in ps)
    for k in range(3):
        s = shrub_mesh.copy()
        sc.collection.objects.link(s)
        f = random.uniform(0.25, 0.4)
        s.scale = (f, f, f)
        s.rotation_euler.z = random.uniform(0, 6.28)
        s.location = (random.uniform(x1, x2), random.choice((y1 - 1.3, y2 + 1.3)), -smin.z * f)
        ns += 1
shrub_mesh.hide_render = True
shrub_mesh.location = (0, 0, -100)
print("KX shrubs", ns)

# ---------------------------------------------------------------------------------------------------------------
# sky: photographed day sky and sunset sky, cross-faded by the sun's height, over the night navy; light haze
world = sc.world
nt = world.node_tree
out = next(n for n in nt.nodes if n.type == 'OUTPUT_WORLD')
night = next(n for n in nt.nodes if n.type == 'BACKGROUND' and n.inputs["Color"].default_value[2] > 0.03 and n.inputs["Color"].default_value[0] < 0.05)
sky_bg = next(n for n in nt.nodes if n.type == 'BACKGROUND' and n is not night)


def hdri_bg(path, rot_deg):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = (0, 0, math.radians(rot_deg))
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = img(path)
    nt.links.new(mp.outputs[0], env.inputs["Vector"])
    bg = nt.nodes.new("ShaderNodeBackground")
    nt.links.new(env.outputs[0], bg.inputs["Color"])
    return bg


day_bg = hdri_bg(os.path.join(PH, "hdri", "kloofendal_48d_partly_cloudy_puresky_2k.exr"), 0)
set_bg = hdri_bg(os.path.join(PH, "hdri", "belfast_sunset_puresky_2k.exr"), 90)
a1 = nt.nodes.new("ShaderNodeAddShader")
a2 = nt.nodes.new("ShaderNodeAddShader")
a3 = nt.nodes.new("ShaderNodeAddShader")
nt.links.new(day_bg.outputs[0], a1.inputs[0])
nt.links.new(set_bg.outputs[0], a1.inputs[1])
nt.links.new(a1.outputs[0], a2.inputs[0])
nt.links.new(night.outputs[0], a2.inputs[1])
nt.links.new(a2.outputs[0], a3.inputs[0])
nt.links.new(sky_bg.outputs[0], a3.inputs[1])
nt.links.new(a3.outputs[0], out.inputs["Surface"])
vol = nt.nodes.new("ShaderNodeVolumePrincipled")
vol.inputs["Density"].default_value = 0.0035
vol.inputs["Color"].default_value = (0.78, 0.84, 0.92, 1)
vol.inputs["Anisotropy"].default_value = 0.35
# (no world volume: in EEVEE an infinite world volume blocks the sun entirely)
# drop the old sky's keyed strength to a faint fill; the photographs carry the sky now
if world.node_tree.animation_data and world.node_tree.animation_data.action:
    act = world.node_tree.animation_data.action
    fcs = getattr(act, "fcurves", None)
    if fcs:
        for fc in list(fcs):
            if f'nodes["{sky_bg.name}"]' in fc.data_path:
                fcs.remove(fc)
sky_bg.inputs["Strength"].default_value = 0.08

KEYS = [(0, 5.6), (150, 6.0), (280, 8.0), (560, 15.5), (700, 18.0), (850, 20.5), (990, 30.6)]


def hour(f):
    for (f0, h0), (f1, h1) in zip(KEYS, KEYS[1:]):
        if f <= f1:
            return h0 + (h1 - h0) * (f - f0) / (f1 - f0)
    return KEYS[-1][1]


def smooth(e0, e1, x):
    t = min(1, max(0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


for f in range(0, 991, 3):
    h = hour(f)
    a = math.pi * (h - 6) / 12
    elev = 68 * math.sin(a)
    day = smooth(4, 22, elev)
    dusk = smooth(-7, 3, elev) * (1 - smooth(8, 22, elev))
    day_bg.inputs["Strength"].default_value = 0.9 * day
    set_bg.inputs["Strength"].default_value = 0.8 * dusk
    day_bg.inputs["Strength"].keyframe_insert("default_value", frame=f)
    set_bg.inputs["Strength"].keyframe_insert("default_value", frame=f)
    vol.inputs["Density"].default_value = 0.0012 + 0.0028 * max(day, dusk)


# ---------------------------------------------------------------------------------------------------------------
# renderer: ray tracing, soft shadows, volumes for haze, motion blur
ee = sc.eevee
for attr, val in (("use_raytracing", True), ("ray_tracing_method", 'SCREEN'), ("use_fast_gi", True),
                  ("shadow_ray_count", 2), ("shadow_step_count", 8), ("volumetric_end", 260.0),
                  ("volumetric_tile_size", '8'), ("volumetric_samples", 48), ("taa_render_samples", 48),
                  ("use_shadows", True), ("use_volumetric_shadows", False)):
    try:
        setattr(ee, attr, val)
    except Exception as e:
        print("KX skip", attr, e)
try:
    ee.ray_tracing_options.resolution_scale = '2'
    ee.ray_tracing_options.use_denoise = True
except Exception as e:
    print("KX rt options", e)
sc.render.use_motion_blur = True
sc.render.motion_blur_shutter = 0.5
cam = sc.camera
cam.data.dof.use_dof = False
sc.render.filepath = r"D:\Kochi-Residence-Interior\video\blender\ext_real\f_"
bpy.ops.wm.save_as_mainfile(filepath=r"D:\Kochi-Residence-Interior\video\blender\launch_exterior_real.blend")
print("KX saved realism blend")

if TEST:
    for f in (20, 175, 300, 470, 640, 700, 790, 870, 985):
        sc.frame_set(f)
        sc.render.filepath = rf"D:\Kochi-Residence-Interior\video\blender\real_{f:04d}.jpg"
        t = time.time()
        bpy.ops.render.render(write_still=True)
        print("KX test frame", f, "%.1f s" % (time.time() - t))
