---
name: vr-house
description: Design a house from a client brief and turn it into a walk-through VR house with AI. It covers the brief and a building-rules check, AutoCAD floor plans, electrical, lighting and plumbing sheets, interior design, a Blender 3D model and renders, a priced bill of quantities (BOQ), a client presentation PDF, and a Meta Quest VR app built in Unity, plus an optional photoreal exterior film. Use this skill whenever someone wants to design a house, villa or apartment interior from a brief, draw floor plans in AutoCAD with AI, make a BOQ or interior cost estimate, model or render a house in Blender, put a Blender model into Unity or VR, or build a Meta Quest walk-through of a building. Use it even if they only mention one of these stages or ask how the MYST Edge Kochi house was built.
---

# VR House: from one client message to a walk-through house

This skill reproduces a workflow that took a real client brief (a family of five, a 40 × 60 ft plot in Kochi, a ₹15 lakh interior budget) to plans, services sheets, a BOQ, renders and a Meta Quest VR app in 6 h 40 min. One AI did it, working through 14 specialist roles.

The point is not "design a house in one prompt". Work like a practice does: one role at a time, in order, with a person reviewing at three checkpoints. Mistakes in architecture cascade: a wrong setback moves every wall, and a wrong wall breaks every sheet after it. The checkpoints stop that.

## 0. Check the workstation first

Before any design work, confirm the tools respond. If one is missing, read `references/setup.md` and help the user install and connect it.

| Tool | How Claude uses it | Quick test |
|---|---|---|
| AutoCAD (Windows) + AutoCAD MCP connector | Draws shapes live; Python `pyautocad` scripts add text, dimensions, layers, DWG save and PDF plots | Draw a 10,000 × 10,000 rectangle at 0,0 |
| Blender 5.x | Headless Python: `blender -b file.blend --python script.py` | Print the version and the GPUs Cycles sees |
| Unity 6 + Android Build Support | The Unity CLI (`unity mcp`, `unity command script eval --file`) | List the scenes in the project |
| Meta Quest 3S | `adb install -r app.apk` over a USB **data** cable | `adb devices` shows the headset |
| Python venv | reportlab, pypdf, pillow, pypdfium2, pyautocad, for documents and AutoCAD scripts | Import them |

Only test what this request needs. A user who only wants a BOQ doesn't need Unity.

## 1. Set up the project folder

```
<Project>\
  brief\          client message, reference photos, notes
  tools\          Python scripts you write (AutoCAD export, MEP sheets, presentation, Blender export)
  vr\             the assembled Blender model, exports, the Quest APK
  unity\          the Unity project
  video\          renders and films (optional)
  Deliverables\   finished PDFs, images, videos
```

Keep every script in `tools\`, so the whole package can be rebuilt after a design change: one changed wall reruns the plans, sheets, model, BOQ and VR.

## 2. The 14 roles and the three checkpoints

| Stage | Roles (checkpoints in bold) |
|---|---|
| Brief | Brief analyst, **Policy reviewer (building rules)** |
| Design | Architect planner, Structural engineer |
| Services | Electrical engineer, Plumbing engineer |
| Interiors | Interior designer, Interior 3D modeler, Interior renderer |
| Cost | **Cost estimator (BOQ)** |
| Visuals & VR | Exterior 3D artist, VR / Unity developer |
| Delivery | **Presentation & QA**, Coordinator |

At each bold checkpoint, stop, show the user what you have and the assumptions behind it, and wait for their go-ahead. Name the role you are working as in each update, so the user knows which hat you're wearing.

## 3. The nine stages

Read `references/pipeline.md` for the full detail of each stage, with an example prompt and what the professional must check. In short:

1. **Brief and rules first** (checkpoint). Turn the message and photos into requirements, constraints and open questions. Then state the building-rule assumptions before drawing anything: setbacks, ground coverage, FAR/height if relevant. Kerala uses KMBR; use the local code for other places. Flag every assumption "to verify with the local body". Never call a design approved or compliant.
2. **Options.** Test a first option against the brief. Propose a better one if it fails, and let the client choose.
3. **Plans in AutoCAD.** Dimensioned plans for every floor: walls (for example 230 mm external, 115 mm internal), openings, room names with clear sizes, dimension strings, setback lines, and an areas block. Save the DWG and plot a PDF marked "for client approval, not for construction".
4. **Structure and services.** Structural notes for an engineer. Then, from the same plan: electrical and switchboards (E1), lighting and false ceiling (L1), flooring and plumbing (P1). These are layouts, not engineering calculations; say so on the sheets.
5. **Interiors.** Furniture layout, a furniture and finishes specification, and a material palette tied to the client's taste.
6. **3D and renders.** Build the house and furniture in Blender from the plans. Use real models (Poly Haven CC0, Sketchfab CC-BY with credits) and render the key interior and exterior views.
7. **BOQ** (checkpoint). Itemise everything at current local rates (material, fabrication, installation, tax). Make the total land on the budget with a small contingency, and list anything that doesn't fit as phase 2 instead of dropping it. Compute every figure in a script from quantity × rate, so the numbers can't drift between pages.
8. **Presentation and QA** (checkpoint). One client PDF: summary with assumptions, all sheets, views, specification, BOQ summary and detail, deferred items. Check that numbers match across pages.
9. **VR on a Meta Quest.** Export the same Blender model to Unity, set up the XR rig, locomotion, teleport and colliders, bake the lighting, build an Android APK and install it on the headset. Read `references/unity-quest.md` first: several of its rules cost hours if missed.

## 4. Rules that save the most time

The full list, with the failure that taught each one, is in `references/lessons.md`. These matter most:

- **One model, end to end.** Blender is the single source of truth, and the same model goes to Unity. A separately rebuilt VR scene never matches the renders.
- **Export .gltf with separate textures, not an embedded .glb.** Embedded textures went into the Quest build uncompressed (1.8 GB). Convert WebP textures to PNG or JPG first, because glTFast can't read WebP.
- **Bake lightmaps for the building shell only;** light the furniture with light probes. Lightmap-packing every mesh overwrote the texture UVs.
- **In headless Blender, switch the GPU on in every script** (`scripts/gpu_on.py`). It's a user preference, not saved in the .blend, so otherwise Blender silently renders on the CPU, about 7× slower.
- **Before any long render, check alignment:** furniture on floors, nothing through walls, close-up renders through each window. Imported models arrive 5–20 cm off.
- **Leave lots of free disk space and close Unity while Blender renders.** The page file grew to 19 GB with both open.

## 5. Optional: photoreal film and reels

For marketing assets made from the same model (a path-traced day-to-night exterior, VR drone shots, a launch film, a Malayalam/English reel), read `references/rendering.md`.

## 6. What to claim, and what not to

The work is used to sell to architects, so overclaiming destroys trust. Say:
- "Designed and visualised", not "built".
- "One AI working through 14 roles", not "14 AI agents".
- "For client approval", not "construction-ready".
- "Checked against the building rules; to verify with the local body", not "approved".

The BOQ total is the budget it was given, not the cost of the house. Professionals keep design judgment, structural sign-off, approvals, vendor quotes and the final check of every drawing. Put this split ("AI drafts, architects decide") in the presentation.

## 7. Reference implementation

`examples/kochi-house/` (inside this skill folder) holds the real scripts from the Kochi project: AutoCAD export and MEP sheets, the presentation builder with the BOQ, the Blender assembly and export, the Unity editor scripts, and the photoreal render pipeline. Their paths are project-specific. Read them for patterns, then write versions for the current project. Don't run them unchanged.
