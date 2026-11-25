"""Add the built-in joinery the furniture packs rely on (from the VR design): living TV wall + TV + console,
and the gaming room's three wall shelves. Parented to the floor empties so they rise with the furniture."""
import bpy
from mathutils import Matrix

sc = bpy.context.scene
GF, FF = 0.45, 3.7


def mat(name, color, rough, metal=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


trav = mat("J_Travertine", (0.66, 0.56, 0.43), 0.45)
walnut = mat("J_Walnut", (0.16, 0.09, 0.05), 0.4)
oak = mat("J_Oak", (0.55, 0.38, 0.22), 0.5)
tv = mat("J_TVGlass", (0.01, 0.01, 0.012), 0.05)


def box(name, x1, x2, y1, y2, z1, z2, m, parent):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2))
    o = bpy.context.object
    o.name = name
    o.scale = (x2 - x1, y2 - y1, z2 - z1)
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(m)
    o.parent = parent
    o.matrix_parent_inverse = Matrix.Identity(4)
    return o


gfe, ffe = sc.objects["FurnitureGF"], sc.objects["FurnitureFF"]
# living: travertine TV wall, fluted oak either side, TV, floating walnut console
box("J_TVWall", 5.5, 5.56, 9.5, 11.1, GF, GF + 2.7, trav, gfe)
y = 8.9
k = 0
while y < 12.04:
    if y < 9.5 or y > 11.1:
        box(f"J_Slat{k}", 5.52, 5.56, y, y + 0.03, GF, GF + 2.7, oak, gfe)
        k += 1
    y += 0.045
box("J_TV", 5.56, 5.6, 9.58, 11.02, GF + 1.05, GF + 1.88, tv, gfe)
box("J_Console", 5.56, 6.0, 9.0, 11.6, GF + 0.25, GF + 0.62, walnut, gfe)
# gaming room: three walnut wall shelves on the slat wall
for i, z in enumerate((1.2, 1.6, 2.0)):
    box(f"J_GameShelf{i}", 5.6, 6.4, 6.25, 6.45, FF + z, FF + z + 0.03, walnut, ffe)
print("KX joinery added, slats", k)
bpy.ops.wm.save_mainfile()
