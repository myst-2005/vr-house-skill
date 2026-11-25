"""Headless: blender -b Kochi-Residence_Option-B_Exterior.blend --python build_exterior_anim.py -- [--test]
Builds the launch-film exterior shot: Kochi neighbourhood, site marking lines, the house rising out of the plot,
a full sun + moon cycle, house and street lights at night, one continuous camera move. 30 fps, 990 frames."""
import math
import random
import sys
import bpy
from mathutils import Vector

random.seed(7)
OUT = r"D:\Kochi-Residence-Interior\video\blender\ext2\f_"
SAVE = r"D:\Kochi-Residence-Interior\video\blender\launch_exterior.blend"
TEST = "--test" in sys.argv
sc = bpy.context.scene
FPS, F_END = 30, 990
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 0, F_END

SITE = ("Ground", "Road", "Verge", "GroundFar", "Lawn", "Driveway", "SitPath", "WaterChannel", "Water", "CW_", "Gate",
        "Bollard", "PathLight", "Shrub", "Palm")


def mat(name, color, rough=0.8, emit=None, strength=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    return m


def box(name, x1, x2, y1, y2, z1, z2, m):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2))
    o = bpy.context.object
    o.name = name
    o.scale = (x2 - x1, y2 - y1, z2 - z1)
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(m)
    return o


def roof_hip(name, x1, x2, y1, y2, z, h, m):
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1, depth=1, location=((x1 + x2) / 2, (y1 + y2) / 2, z + h / 2),
                                    rotation=(0, 0, math.pi / 4))
    o = bpy.context.object
    o.name = name
    o.scale = ((x2 - x1) * 0.78, (y2 - y1) * 0.78, h)
    bpy.ops.object.transform_apply(rotation=True, scale=True)
    o.data.materials.append(m)
    return o


def smooth(e0, e1, x):
    t = min(1, max(0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------------------------------------------------------
# neighbourhood (plain Kerala houses: white or pastel render, terracotta hip roofs or flat roofs, lit windows at night)
render_cols = [(0.86, 0.84, 0.78), (0.92, 0.88, 0.76), (0.80, 0.84, 0.82), (0.90, 0.80, 0.70), (0.84, 0.82, 0.86)]
tile = mat("N_Terracotta", (0.55, 0.22, 0.12), 0.7)
win_glass = mat("N_WindowDark", (0.05, 0.06, 0.07), 0.15)
win_glow = mat("N_WindowGlow", (0.05, 0.05, 0.05), 0.4, emit=(1.0, 0.72, 0.42), strength=0.0)
cw = mat("N_CompoundWall", (0.75, 0.73, 0.68), 0.9)
night_emitters = [win_glow]
houses = [  # x1, x2, y1, y2, floors, hip roof
    (-17, -8, -2, 9, 2, True), (-23, -15, 11, 20, 1, True), (14, 23, -3, 8, 2, False), (15, 23, 10, 16, 1, True),
    (-14, -4, 31, 40, 2, True), (0, 9, 32, 41, 1, True), (13, 22, 31, 39, 2, False), (26, 34, 31, 40, 1, True),
    (-3, 7, -20, -9, 2, False), (11, 21, -19, -9, 1, True), (-18, -8, -20, -8, 1, True), (28, 36, -2, 9, 1, True),
]
for i, (x1, x2, y1, y2, fl, hip) in enumerate(houses):
    h = 3.2 * fl
    col = mat(f"N_Render{i % len(render_cols)}", render_cols[i % len(render_cols)], 0.9)
    box(f"NH{i}_body", x1, x2, y1, y2, 0, h, col)
    if hip:
        box(f"NH{i}_eave", x1 - 0.6, x2 + 0.6, y1 - 0.6, y2 + 0.6, h, h + 0.15, tile)
        roof_hip(f"NH{i}_roof", x1 - 0.6, x2 + 0.6, y1 - 0.6, y2 + 0.6, h + 0.15, 2.4, tile)
    else:
        box(f"NH{i}_parapet", x1, x2, y1, y2, h, h + 0.6, col)
    # windows on all four sides, some lit at night
    for f in range(fl):
        zc = f * 3.2 + 1.6
        for side in ("N", "S", "E", "W"):
            span = (x1, x2) if side in "NS" else (y1, y2)
            n = max(1, int((span[1] - span[0]) / 3))
            for k in range(n):
                c = span[0] + (k + 0.5) * (span[1] - span[0]) / n
                lit = random.random() < 0.55
                m = win_glow if lit else win_glass
                if side == "N": box(f"NH{i}_w", c - 0.6, c + 0.6, y2, y2 + 0.04, zc - 0.6, zc + 0.6, m)
                if side == "S": box(f"NH{i}_w", c - 0.6, c + 0.6, y1 - 0.04, y1, zc - 0.6, zc + 0.6, m)
                if side == "E": box(f"NH{i}_w", x2, x2 + 0.04, c - 0.6, c + 0.6, zc - 0.6, zc + 0.6, m)
                if side == "W": box(f"NH{i}_w", x1 - 0.04, x1, c - 0.6, c + 0.6, zc - 0.6, zc + 0.6, m)
    # compound wall around each plot
    px1, px2, py1, py2 = x1 - 2, x2 + 2, y1 - 2, y2 + 2
    for a in ((px1, px2, py1, py1 + 0.2), (px1, px2, py2 - 0.2, py2), (px1, px1 + 0.2, py1, py2), (px2 - 0.2, px2, py1, py2)):
        box(f"NH{i}_cw", *a, 0, 1.3, cw)

# more coconut palms: copy the existing palm (trunk + fronds near x -6, y 9) to new spots
palm_src = [o for o in sc.objects if o.name.startswith(("PalmTrunk.02", "PalmTrunk.03", "PalmFrond.06", "PalmFrond.07", "PalmFrond.08"))
            and abs(o.matrix_world.translation.x + 6.1) < 4 and abs(o.matrix_world.translation.y - 9) < 4]
for j, (px, py, rot) in enumerate([(-30, 22, 0.6), (35, 20, 2.1), (30, -14, 1.2), (-31, 12, 2.9), (19, -6, 0.3),
                                   (-21, 3, 1.7), (31, 14, 2.6), (6, -24, 0.9), (-10, -24, 2.2), (38, 26, 1.4)]):
    for o in palm_src:
        n = o.copy()
        sc.collection.objects.link(n)
        v = o.matrix_world.translation - Vector((-6.1, 9.0, 0))
        v.rotate(__import__("mathutils").Euler((0, 0, rot)))
        n.location = Vector((px, py, 0)) + v
        n.rotation_euler.z += rot
        n.scale = o.scale * (0.85 + 0.3 * ((j * 37) % 10) / 10)

# street lights along the road (north side of the plot), lit at night
pole = mat("N_Pole", (0.25, 0.26, 0.27), 0.5, )
lamp = mat("N_StreetLamp", (0.9, 0.9, 0.85), 0.3, emit=(1.0, 0.78, 0.5), strength=0.0)
night_emitters.append(lamp)
street_lights = []
for x in range(-36, 50, 16):
    box(f"SL_pole{x}", x - 0.08, x + 0.08, 17.4, 17.56, 0, 6.5, pole)
    box(f"SL_arm{x}", x - 0.06, x + 0.06, 17.4, 18.9, 6.4, 6.5, pole)
    box(f"SL_lamp{x}", x - 0.2, x + 0.2, 18.6, 19.1, 6.3, 6.4, lamp)
    bpy.ops.object.light_add(type='POINT', location=(x, 18.85, 6.1))
    l = bpy.context.object
    l.data.energy = 0
    l.data.color = (1.0, 0.75, 0.48)
    l.data.shadow_soft_size = 0.3
    l.data.use_shadow = False
    street_lights.append(l)

# ---------------------------------------------------------------------------------------------------------------
# the house: everything that is not site. Footprints drawn as white lime lines, then the house rises out of the plot.
house = [o for o in sc.objects if o.type == 'MESH' and not o.name.startswith(SITE) and not o.name.startswith(("NH", "SL_", "Palm"))
         and o.name not in [p.name for p in palm_src]]
house = [o for o in house if not o.name.startswith(("PalmTrunk", "PalmFrond"))]
lime = mat("SiteLime", (0.95, 0.95, 0.92), 0.95)


def zrange(o):
    zs = [(o.matrix_world @ Vector(c)).z for c in o.bound_box]
    return min(zs), max(zs)


def xyrange(o):
    ps = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return min(p.x for p in ps), max(p.x for p in ps), min(p.y for p in ps), max(p.y for p in ps)


F_DRAW0, F_DRAW1 = 165, 280          # site lines get marked
F_RISE0, F_RISE1 = 280, 560          # the house rises
walls = [o for o in house if zrange(o)[0] < 0.5 and zrange(o)[1] > 2.5 and (xyrange(o)[1] - xyrange(o)[0] < 0.4 or xyrange(o)[3] - xyrange(o)[2] < 0.4)]
cx, cy = 5.0, 7.0
walls.sort(key=lambda o: math.atan2((xyrange(o)[2] + xyrange(o)[3]) / 2 - cy, (xyrange(o)[0] + xyrange(o)[1]) / 2 - cx))
for i, o in enumerate(walls):
    x1, x2, y1, y2 = xyrange(o)
    fp = box(f"FP_{o.name}", x1 - 0.03, x2 + 0.03, y1 - 0.03, y2 + 0.03, 0.005, 0.04, lime)
    f = F_DRAW0 + (F_DRAW1 - F_DRAW0 - 12) * i / max(1, len(walls) - 1)
    fp.scale = (1, 1, 1)
    fp.keyframe_insert("scale", frame=f + 10)
    fp.scale = (0.001, 0.001, 1)
    fp.keyframe_insert("scale", frame=f)
    fp.location.z = 0
    fp.keyframe_insert("location", frame=F_RISE1)
    fp.location.z = -0.5                      # tuck the lines away once the plinth covers them
    fp.keyframe_insert("location", frame=F_RISE1 + 1)

DROP = 9.5
levels = sorted(house, key=lambda o: (zrange(o)[0], xyrange(o)[0]))
for i, o in enumerate(levels):
    z0 = zrange(o)[0]
    tier = 0 if z0 < 0.3 else 1 if z0 < 3.3 else 2
    span = {0: (F_RISE0, F_RISE0 + 60), 1: (F_RISE0 + 40, F_RISE0 + 170), 2: (F_RISE0 + 160, F_RISE1)}[tier]
    xs = xyrange(o)
    k = ((xs[0] + xs[1]) / 2 + 1) / 12          # stagger west to east within a tier
    start = span[0] + (span[1] - span[0] - 36) * min(1, max(0, k))
    end = start + 36
    zfin = o.location.z
    o.location.z = zfin - DROP
    o.keyframe_insert("location", index=2, frame=start)
    o.location.z = zfin
    o.keyframe_insert("location", index=2, frame=end)
    for fc in (o.animation_data.action.fcurves if hasattr(o.animation_data.action, "fcurves") else []):
        for kp in fc.keyframe_points:
            kp.interpolation = 'BACK'
            kp.easing = 'EASE_OUT'
            kp.back = 0.8

# ---------------------------------------------------------------------------------------------------------------
# sun, moon, sky: a virtual clock across the shot
KEYS = [(0, 5.6), (150, 6.0), (280, 8.0), (560, 15.5), (700, 18.0), (850, 20.5), (990, 30.6)]


def hour(f):
    for (f0, h0), (f1, h1) in zip(KEYS, KEYS[1:]):
        if f <= f1:
            return h0 + (h1 - h0) * (f - f0) / (f1 - f0)
    return KEYS[-1][1]


def body_dir(a, emax):
    e = math.radians(emax) * math.sin(a)
    h = Vector((math.cos(a), -math.sin(a) * 0.9, 0)).normalized()     # east -> south -> west arc
    return (h * math.cos(e) + Vector((0, 0, math.sin(e)))).normalized(), e


CENTER = Vector((5, 7, 0))
R = 900
sun_vis = bpy.data.objects.new("SunDisc", None)
bpy.ops.mesh.primitive_uv_sphere_add(radius=30, location=(0, 0, 0))
sun_disc = bpy.context.object
sun_disc.name = "SunDisc"
sun_disc.data.materials.append(mat("SunMat", (1, 0.9, 0.7), 1, emit=(1.0, 0.86, 0.6), strength=60))
bpy.ops.mesh.primitive_uv_sphere_add(radius=24, location=(0, 0, 0))
moon_disc = bpy.context.object
moon_disc.name = "MoonDisc"
moon_mat = mat("MoonMat", (0.9, 0.92, 0.95), 1, emit=(0.85, 0.9, 1.0), strength=6)
moon_disc.data.materials.append(moon_mat)
for o in (sun_disc, moon_disc):
    o.visible_shadow = False

sun = bpy.data.objects.get("SunLow")
for l in [o for o in sc.objects if o.type == 'LIGHT' and o.data.type == 'SUN' and o is not sun]:
    l.data.energy = 0                           # keep one sun; the sky does the fill
sun.data.angle = math.radians(1.5)
bpy.ops.object.light_add(type='SUN', location=(0, 0, 50))
moonlight = bpy.context.object
moonlight.name = "MoonLight"
moonlight.data.color = (0.62, 0.72, 1.0)
moonlight.data.angle = math.radians(2)

world = sc.world
nt = world.node_tree
sky = next(n for n in nt.nodes if n.type == 'TEX_SKY')
bg = next(n for n in nt.nodes if n.type == 'BACKGROUND')
out = next(n for n in nt.nodes if n.type == 'OUTPUT_WORLD')
print("KX sky type", sky.sky_type)
if hasattr(sky, "sun_disc"):
    sky.sun_disc = False
for p in ('sun_size','sun_intensity','altitude','air_density','dust_density','ozone_density','aerosol_density'):
    print('KX sky', p, getattr(sky, p, None))
print('KX bg strength', bg.inputs['Strength'].default_value)
night_bg = nt.nodes.new("ShaderNodeBackground")
night_bg.inputs["Color"].default_value = (0.010, 0.016, 0.040, 1)
add = nt.nodes.new("ShaderNodeAddShader")
nt.links.new(bg.outputs[0], add.inputs[0])
nt.links.new(night_bg.outputs[0], add.inputs[1])
nt.links.new(add.outputs[0], out.inputs["Surface"])

glows = [m for m in bpy.data.materials if m.name.startswith(("Interior_Glow", "Bollard_Glow"))]
house_lights = [o for o in sc.objects if o.type == 'LIGHT' and o.data.type != 'SUN' and not o.name.startswith(("SL", "Point"))]
for l in house_lights:
    l["day_energy"] = l.data.energy
glow_base = {}
for m in glows:
    b = next(n for n in m.node_tree.nodes if n.type in ("BSDF_PRINCIPLED", "EMISSION"))
    key = "Emission Strength" if b.type == "BSDF_PRINCIPLED" else "Strength"
    glow_base[m.name] = (b, key, b.inputs[key].default_value)
sun_noon = 4.5
STEP = 3
for f in range(0, F_END + 1, STEP):
    h = hour(f)
    a_sun = math.pi * (h - 6) / 12
    d_sun, e_sun = body_dir(a_sun, 68)
    a_moon = math.pi * (((h - 19) % 24)) / 12
    d_moon, e_moon = body_dir(a_moon, 34)
    day = smooth(-4, 8, math.degrees(e_sun))           # 0 night .. 1 day
    night = 1 - smooth(-8, 2, math.degrees(e_sun))
    built = smooth(F_RISE1 - 40, F_RISE1, f)            # house lights only once the house stands
    sun_disc.location = CENTER + d_sun * R
    moon_disc.location = CENTER + d_moon * R * 0.97
    sun_disc.keyframe_insert("location", frame=f)
    moon_disc.keyframe_insert("location", frame=f)
    sun.rotation_euler = (-d_sun).to_track_quat('-Z', 'Y').to_euler()
    sun.data.energy = sun_noon * smooth(-1, 10, math.degrees(e_sun))
    sun.data.color = (1.0, 0.72 + 0.26 * smooth(0, 25, math.degrees(e_sun)), 0.45 + 0.5 * smooth(0, 30, math.degrees(e_sun)))
    sun.keyframe_insert("rotation_euler", frame=f)
    sun.data.keyframe_insert("energy", frame=f)
    sun.data.keyframe_insert("color", frame=f)
    moonlight.rotation_euler = (-d_moon).to_track_quat('-Z', 'Y').to_euler()
    moonlight.data.energy = 0.35 * night * smooth(-2, 8, math.degrees(e_moon))
    moonlight.keyframe_insert("rotation_euler", frame=f)
    moonlight.data.keyframe_insert("energy", frame=f)
    if hasattr(sky, "sun_elevation"):
        sky.sun_elevation = max(e_sun, math.radians(-12))
        sky.keyframe_insert("sun_elevation", frame=f)
    if hasattr(sky, "sun_rotation"):
        sky.sun_rotation = math.atan2(-d_sun.x, d_sun.y)
        sky.keyframe_insert("sun_rotation", frame=f)
    night_bg.inputs["Strength"].default_value = 0.25 + 0.75 * night
    night_bg.inputs["Strength"].keyframe_insert("default_value", frame=f)
    moon_mat.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 2 + 6 * night
    moon_mat.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].keyframe_insert("default_value", frame=f)
    lights_on = night * built
    for m in night_emitters:
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Emission Strength"].default_value = (6 if m.name == "N_StreetLamp" else 3) * night
        b.inputs["Emission Strength"].keyframe_insert("default_value", frame=f)
    for name, (b, key, base) in glow_base.items():
        b.inputs[key].default_value = base * lights_on
        b.inputs[key].keyframe_insert("default_value", frame=f)
    for l in house_lights:
        l.data.energy = l["day_energy"] * (0.15 + 0.85 * lights_on) * built
        l.data.keyframe_insert("energy", frame=f)
    for l in street_lights:
        l.data.energy = 400 * night
        l.data.keyframe_insert("energy", frame=f)
    sc.view_settings.exposure = 1.3 * night
    sc.view_settings.keyframe_insert("exposure", frame=f)

# ---------------------------------------------------------------------------------------------------------------
# camera: one continuous drone move, from a high dawn view over the plot, down and around with the sun, to night
cam_data = bpy.data.cameras.new("FilmCam")
cam_data.lens = 24
cam_data.clip_end = 3000
cam = bpy.data.objects.new("FilmCam", cam_data)
sc.collection.objects.link(cam)
sc.camera = cam
target = bpy.data.objects.new("FilmTarget", None)
sc.collection.objects.link(target)
con = cam.constraints.new('TRACK_TO')
con.target = target
con.track_axis = 'TRACK_NEGATIVE_Z'
con.up_axis = 'UP_Y'
CAM = [(0, (26, 25, 10), (-4, 3, 7)),          # night, looking west: the moon setting behind the plot
       (90, (12, 28, 9), (2, 4, 4)),
       (175, (-14, 26, 8), (16, 4, 5)),        # swung round to look east: sunrise behind the empty plot
       (250, (-6, 25, 17), (5, 7, 0)),         # crane up: the site lines get marked
       (330, (2, 27, 16), (5, 7, 0.5)),
       (560, (12, 27, 9), (5, 7, 3.2)),        # the house rises as the sun climbs
       (640, (24, 23, 7), (-6, 5, 4.5)),       # east side, looking west: sunset behind the finished house
       (720, (25, 23, 9.5), (-8, 5, 4.5)),
       (785, (6, 29, 11.5), (5, 6, 4)),        # pass north of the house, over the road, high above the roofs
       (850, (-12, 27, 11), (12, 5, 8)),       # night, west side looking east: the moon rising over the house
       (990, (-12, 30, 16), (16, 4, 6))]       # crane up above the palms as the night runs to the next dawn
for f, p, t in CAM:
    cam.location = p
    cam.keyframe_insert("location", frame=f)
    target.location = t
    target.keyframe_insert("location", frame=f)

# ---------------------------------------------------------------------------------------------------------------
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, 100
sc.render.image_settings.file_format = 'JPEG'
sc.render.image_settings.quality = 92
sc.render.filepath = OUT
try:
    sc.eevee.taa_render_samples = 24
except Exception:
    pass
try:
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception as e:
    print("KX view", e)
bpy.ops.wm.save_as_mainfile(filepath=SAVE)
print("KX built: neighbours", len(houses), "walls", len(walls), "house objs", len(levels))

if TEST:
    import time
    for f in (20, 175, 260, 420, 600, 680, 760, 870, 985):
        sc.frame_set(f)
        sc.render.filepath = rf"D:\Kochi-Residence-Interior\video\blender\test_{f:04d}.jpg"
        t = time.time()
        bpy.ops.render.render(write_still=True)
        print("KX test frame", f, "hour %.1f" % hour(f), "%.1f s" % (time.time() - t))
