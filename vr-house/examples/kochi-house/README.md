# Reference implementation: the Kochi house

These are the real scripts from the project the skill is built on. They hard-code that project's paths (`D:\Kochi-Residence-Interior\...`), plan coordinates and object names, so read them for patterns. Don't run them unchanged: ask Claude to write the equivalent for your project.

| Folder | Scripts | What they show |
|---|---|---|
| `autocad/` | `export_plan.py`, `mep_sheets.py` | Driving a running AutoCAD with `pyautocad`: layers, text, dimensions, saving DWG, plotting A3 PDF. One parameterised script draws the E1, L1 or P1 sheet. |
| `documents/` | `build_presentation.py` | The 20-page client PDF (reportlab + pypdf), with every BOQ figure computed from quantity × rate |
| `blender/` | `assemble_house.py`, `export_house_glb.py`, `export_unity_gltf.py`, `vr_place.py` | One Blender scene from the shell plus per-room furniture packs, and the export to Unity |
| `unity/Editor/` | `KochiSetup.cs`, `KochiQuest.cs`, `KochiFinish.cs`, `KochiDrone.cs`, `KochiGltfInfo.cs` | Scene build (XR rig, colliders, teleport, lamps, probes), OpenXR/Android config and APK build, rebuild + bake, film-look drone renders |
| `unity/Scripts/` | `RoomJumper.cs` | A/X and B/Y to jump room to room in VR |
| `render/` | `build_exterior_anim.py`, `realism.py`, `realism2.py`, `photoreal.py`, `cycles_setup.py`, `final_settings.py`, `align_check.py`, `align_fix.py`, `add_joinery.py`, `closeups.py`, `fetch_polyhaven.py`, `make_frond_tex.py` | The photoreal day-to-night exterior: animation, PBR materials and skies, furniture through the glass, the alignment check before the final Cycles render |

3D model credits: `3D-Model-Credits.txt`. No third-party models are included here.
