import bpy
from mathutils import Vector

sc = bpy.context.scene
sc.frame_set(600)
cd = bpy.data.cameras.new("Inspect")
cd.lens = 28
cd.clip_end = 2000
cam = bpy.data.objects.new("Inspect", cd)
sc.collection.objects.link(cam)
sc.camera = cam
sc.render.resolution_x, sc.render.resolution_y = 960, 540
sc.cycles.samples = 64
sc.render.use_motion_blur = False
shots = {
    "4_living_east": ((12.4, 13.5, 2.3), (6.0, 10.5, 1.2)),
    "7_gaming_shelves": ((6.0, -4.0, 5.6), (6.0, 6.3, 5.0)),
}
for name, (eye, tgt) in shots.items():
    cam.location = eye
    cam.rotation_euler = (Vector(tgt) - Vector(eye)).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = rf"D:\Kochi-Residence-Interior\video\blender\close_{name}.jpg"
    bpy.ops.render.render(write_still=True)
    print("KX", name)
