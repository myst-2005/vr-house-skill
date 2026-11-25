"""Headless: blender -b launch_exterior_real.blend --python cycles_setup.py -- [--test]
Switch the realistic exterior to Cycles path tracing on the GPU (OptiX) with denoising, and time test frames."""
import sys
import time
import bpy

sc = bpy.context.scene
prefs = bpy.context.preferences.addons["cycles"].preferences
for kind in ("OPTIX", "CUDA"):
    try:
        prefs.compute_device_type = kind
        prefs.get_devices()
        gpus = [d for d in prefs.devices if d.type == kind]
        if gpus:
            for d in prefs.devices:
                d.use = d.type == kind
            print("KX device", kind, [d.name for d in gpus])
            break
    except Exception as e:
        print("KX device err", kind, e)
sc.render.engine = 'CYCLES'
c = sc.cycles
c.device = 'GPU'
c.samples = 96
c.use_adaptive_sampling = True
c.adaptive_threshold = 0.03
c.use_denoising = True
try:
    c.denoiser = 'OPTIX'
except Exception:
    c.denoiser = 'OPENIMAGEDENOISE'
c.max_bounces = 6
c.diffuse_bounces = 3
c.glossy_bounces = 3
c.transmission_bounces = 6
c.transparent_max_bounces = 24          # palm fronds are alpha cut-outs
c.use_light_tree = True
c.sample_clamp_indirect = 8
c.caustics_reflective = False
c.caustics_refractive = False
sc.render.use_persistent_data = True
sc.render.use_motion_blur = True
sc.render.motion_blur_shutter = 0.4
# a slight depth of field on the drone camera: everything near sharp, far horizon just soft
cam = sc.camera
cam.data.dof.use_dof = True
cam.data.dof.aperture_fstop = 8.0
cam.data.dof.focus_object = bpy.data.objects.get("FilmTarget")
sc.render.filepath = r"D:\Kochi-Residence-Interior\video\blender\ext_cyc\f_"
bpy.ops.wm.save_as_mainfile(filepath=r"D:\Kochi-Residence-Interior\video\blender\launch_exterior_cycles.blend")
print("KX saved cycles blend")

if "--test" in sys.argv:
    for f in (520, 790):
        sc.frame_set(f)
        sc.render.filepath = rf"D:\Kochi-Residence-Interior\video\blender\cyc_{f:04d}.jpg"
        t = time.time()
        bpy.ops.render.render(write_still=True)
        print("KX cycles frame", f, "%.1f s" % (time.time() - t))
