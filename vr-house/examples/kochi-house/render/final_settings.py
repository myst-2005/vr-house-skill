"""Final Cycles settings for the overnight exterior render (run after gpu_on.py)."""
import bpy

sc = bpy.context.scene
c = sc.cycles
c.samples = 56
c.use_adaptive_sampling = True
c.adaptive_threshold = 0.05
c.use_denoising = True
sc.render.use_persistent_data = True
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, 100
sc.render.image_settings.file_format = 'JPEG'
sc.render.image_settings.quality = 92
sc.render.filepath = r"D:\Kochi-Residence-Interior\video\blender\ext_cyc\f_"
sc.camera = bpy.data.objects["FilmCam"]
for o in sc.objects:
    if o.name.startswith("Grass_"):
        o.hide_render = False
print("KX final settings", c.samples, sc.camera.name)
