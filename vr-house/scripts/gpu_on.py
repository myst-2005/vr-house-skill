"""Switch Cycles to the GPU. Run it first in every headless Blender session that renders:

    blender -b scene.blend --python gpu_on.py --python render.py

The compute device is a user preference, not stored in the .blend, so a headless run otherwise falls back to the
CPU without any warning (about 7x slower on an RTX 2050 laptop in the reference project).
Tries OptiX (NVIDIA RTX), then CUDA, then HIP (AMD), then METAL (Apple).
"""
import bpy

prefs = bpy.context.preferences.addons["cycles"].preferences
chosen = None
for kind in ("OPTIX", "CUDA", "HIP", "METAL"):
    try:
        prefs.compute_device_type = kind
    except TypeError:
        continue
    prefs.get_devices()
    gpus = [d for d in prefs.devices if d.type == kind]
    if gpus:
        for d in prefs.devices:
            d.use = d.type == kind
        chosen = kind
        break

if chosen:
    bpy.context.scene.cycles.device = "GPU"
    print("GPU ON:", chosen, [d.name for d in prefs.devices if d.use])
else:
    print("GPU OFF: no supported GPU found, Cycles will render on the CPU")
