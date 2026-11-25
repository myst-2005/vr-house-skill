# The nine stages in detail

Each stage lists the role, what to do, what it produces, what the professional must check, and an example prompt. The examples are templates: adapt them to the project.

## Contents
1. Brief and rules first (checkpoint)
2. Options
3. Plans in AutoCAD
4. Structure and services (E1, L1, P1)
5. Interiors
6. 3D and renders
7. BOQ (checkpoint)
8. Presentation and QA (checkpoint)
9. VR on a Meta Quest

---

## 1. Brief and rules first (checkpoint)

**Roles:** Brief analyst, then Policy reviewer.

Turn the client's message and reference photos into a numbered requirements list, constraints and open questions. Then state the building-rule assumptions before any drawing:
- setbacks on every side;
- maximum ground coverage;
- FAR and height, if they apply;
- parking, and any special rules.

In Kerala this is KMBR (Kerala Municipality Building Rules); elsewhere, use the local code. Write every assumption as "assumed, verify with the local body".

**Produces:** a brief summary, the rule assumptions (the reference used front 3.0 m, rear 1.5 m, sides 1.2 / 1.0 m and reported coverage as 62% of the plot), and the open questions.

**Professional checks:** every rule assumption. Nothing is drawn until this is agreed.

> Here is a client brief for a house on a 40 × 60 ft plot in Kochi, road to the north: [paste brief and attach reference photos]. Act as a brief analyst: list every requirement, constraint and open question. Then act as a KMBR policy reviewer: state the setbacks and coverage you assume, and flag what must be verified with the local body. Don't draw anything yet.

Reference photos matter. In the reference project the client sent three, and the design followed one closely: a rounded, fluted-timber first floor with a white rim and full-glass ends. Describe what you take from each photo.

## 2. Options

**Role:** Architect planner.

Sketch a first option and test it against the brief: rooms, areas, circulation, the rules, the budget. If it fails, say why and propose a better one. The reference drew a single-storey Option A, then moved to a two-storey Option B. Let the client choose before detailed drawing.

## 3. Plans in AutoCAD

**Role:** Architect planner.

Draw every floor with:
- walls (230 mm external, 115 mm internal is a common Kerala default);
- doors and windows;
- room names with clear sizes;
- dimension strings;
- setback lines;
- a notes block with plot size, areas per floor, total built-up area, ground coverage, the setback assumptions, and "changes from the brief".

Use the MCP tools for geometry. Write a `pyautocad` script for text, dimensions, layers, saving the DWG and plotting an A3 PDF (see `examples/kochi-house/autocad/export_plan.py`).

Title every sheet "FOR CLIENT APPROVAL - NOT A CONSTRUCTION DRAWING".

**Professional checks:** room sizes, circulation, stairs, door swings, the areas block.

> Act as the architect planner. Draw the Option B ground and first floor plans in AutoCAD: 230 mm external and 115 mm internal walls, all rooms named with clear sizes, dimension strings, setback lines and an areas block. Then save the DWG and plot a PDF titled for client approval.

## 4. Structure and services (E1, L1, P1)

**Roles:** Structural engineer, Electrical engineer, Plumbing engineer.

Add structural notes: indicative columns, cantilevers to be designed by a structural engineer, floor-to-floor height. Then draw three sheets on copies of the plan:
- **E1, electrical and switchboards:** points, sockets, boards, AC and appliance points;
- **L1, lighting and false ceiling:** fittings, cove lines, ceiling outlines;
- **P1, flooring and plumbing:** floor finishes per room, wet points, drains.

One parameterised script that draws any of the three keeps them consistent (see `examples/kochi-house/autocad/mep_sheets.py`).

**Professional checks:** these are layouts, not calculations. A structural engineer designs the structure; MEP consultants size loads, cables, pipes and the septic or sewer connection. Say so on the sheets.

## 5. Interiors

**Role:** Interior designer.

Lay out every room's furniture (a furniture layout sheet), write a furniture and finishes specification (item, size, material, finish per room), and set a palette tied to the client's taste. The reference used warm minimalism: travertine, fluted oak, walnut, oatmeal fabrics, matte finishes, cove lighting, and a moodier palette for the gaming room.

## 6. 3D and renders

**Roles:** Interior 3D modeler, Interior renderer, Exterior 3D artist.

Build the house in Blender from the plan coordinates, so it lines up with the drawings. Furnish it with real models:
- **Poly Haven:** CC0, no credit needed.
- **Sketchfab:** CC-BY, credit the author wherever renders are shared. Keep a `3D-Model-Credits.txt`.

Model whatever is custom (walls, ceilings, a TV wall, cabinetry) yourself. Render the key views: the reference made 4 interior and 3 exterior renders. Keep furniture in per-room "packs" (one .glb per room), so the same pieces can be reassembled for VR.

**Professional checks:** that the 3D matches the drawings and the references.

## 7. BOQ (checkpoint)

**Role:** Cost estimator.

Itemise every item at current local market rates, including material, fabrication, installation and tax. Group the items into sections:

| Section | Reference amount |
|---|---|
| A. Kitchen | ₹1,91,760 |
| B. Wardrobes | ₹2,97,400 |
| C. Feature walls and desks | ₹1,78,610 |
| D. False ceiling | ₹1,32,520 |
| E. Lighting and fans | ₹1,62,500 |
| F. Loose furniture | ₹3,90,000 |
| G. Soft furnishings | ₹1,17,700 |
| H. Contingency | ₹29,510 |

Make the total land on the budget with a small contingency (reference: core ₹14,70,490 + 2% contingency = ₹15,00,000). List what doesn't fit in a phase-2 table (reference: ₹1,63,660) rather than dropping it. State the cost per sq ft and the rate accuracy (±10%), and tell the client to get three vendor quotes.

Compute every figure in the presentation script from quantity × rate. Typed totals drift.

**Professional checks:** the rates and scope; vendor quotes before ordering.

> Act as the cost estimator. Build an itemised BOQ for the interiors at current Kochi market rates (material, fabrication, installation, GST). The total must equal the ₹15,00,000 budget including a 2% contingency. Move anything that doesn't fit to a separate phase-2 list; don't drop items silently.

## 8. Presentation and QA (checkpoint)

**Roles:** Presentation & QA, Coordinator.

Build one client PDF in this order: contents · design summary with assumptions and open items · plans · furniture · E1 · L1 · P1 · exterior views · materials · interior views · specification · BOQ summary · BOQ detail · deferred items. The reference was 20 A3 pages, built with reportlab and pypdf (see `examples/kochi-house/documents/build_presentation.py`).

QA before sending:
- numbers match across pages;
- every assumption is listed;
- every sheet is marked for client approval;
- the brief-versus-design changes are explained (the reference grew from 1,500–1,600 sq ft to about 2,550 sq ft, and from 3 to 4 bathrooms, with the budget held by phasing).

## 9. VR on a Meta Quest

**Role:** VR / Unity developer.

Read `unity-quest.md`. In short:
1. Assemble one Blender scene: the shell plus every furniture pack.
2. Export `.gltf` with separate textures into the Unity project.
3. In Unity, run an editor script that builds the scene: XR rig, locomotion, teleport areas, colliders, lamps, reflection and light probes.
4. Bake lightmaps for the shell only.
5. Build the Android APK and `adb install` it.

**Professional checks:** walk every room on the headset. Check scale, stairs, lighting and comfort (a steady frame rate, snap turning).
