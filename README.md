# VR House: a Claude skill from client brief to walk-through house

**One message from a client became a fully designed, costed house they could walk through on a Meta Quest, in 6 h 40 min, done by one AI.**

`vr-house` is a Claude skill that reproduces that workflow. Claude works through 14 specialist roles in order, with three checkpoints where a person reviews before anything moves on:

```
Client message + photos → Rules check (KMBR) → Plans (AutoCAD) → E1 · L1 · P1 → Interiors
  → 3D + renders (Blender) → BOQ → Presentation + QA → Unity → Meta Quest 3S
```

Built by [MYST Edge](#learn-it-with-myst-edge) on a real project: a family of five, a 40 × 60 ft plot in Kochi, Kerala, and a ₹15 lakh interior budget. Brief received at 14:15 on 11 Nov 2026; playable in VR at 20:56.

## What you get

| Stage | Output |
|---|---|
| Brief and rules | Requirements, building-rule assumptions (setbacks, coverage) flagged for the local body |
| Plans | Dimensioned AutoCAD plans (DWG + PDF) with an areas and setbacks block |
| Services | Electrical (E1), lighting and false ceiling (L1), flooring and plumbing (P1) sheets |
| Interiors | Furniture layout and specification |
| 3D | Blender model, interior and exterior renders |
| Cost | Itemised BOQ landing on the budget, with contingency and phase-2 items |
| Presentation | One client PDF (20 pages in the reference) |
| VR | A standalone Meta Quest app: walk both floors, teleport, jump room to room |
| Optional | Photoreal day-to-night exterior (Cycles), a launch film, a Malayalam + English reel |

## Install

**Claude Code** (desktop app Code tab or CLI): copy the `vr-house` folder into your skills folder.

```bash
git clone https://github.com/myst-2005/vr-house-skill.git
cp -r vr-house-skill/vr-house ~/.claude/skills/            # all projects
# or: cp -r vr-house-skill/vr-house <your-project>/.claude/skills/   (one project)
```

On Windows: `xcopy /E /I vr-house-skill\vr-house %USERPROFILE%\.claude\skills\vr-house`.

**Claude apps:** download `vr-house.skill` from the [latest release](https://github.com/myst-2005/vr-house-skill/releases) and add it in your Skills settings.

Then ask something like:

> Here's a client brief for a two-storey house on a 40 × 60 ft plot in Kochi with a ₹15 lakh interior budget [paste brief + photos]. Take it from brief to a Meta Quest walk-through.

## Requirements

- Windows PC (AutoCAD automation is Windows-only). The reference ran on a laptop with an RTX 2050 GPU and 16 GB RAM.
- **Claude Code**, plus:
  - **AutoCAD** with the open-source [AutoCAD MCP server](https://github.com/vigneshpbmenon/autocad-mcp-server)
  - **Blender 5.x** (run headless)
  - **Unity 6** with Android Build Support, glTFast, OpenXR, Meta OpenXR and XR Interaction Toolkit, through Unity's CLI / MCP
  - **Python 3.11**
- **Meta Quest 3S** with Developer Mode and a USB data cable.
- Optional, for video: HyperFrames, FFmpeg, ElevenLabs v3, a HeyGen account.

Full setup, with every connector config and a test for each: [`vr-house/references/setup.md`](vr-house/references/setup.md).

## What's inside

```
vr-house/
  SKILL.md                    the workflow Claude follows
  references/
    setup.md                  workstation, MCP connectors, Unity, Quest
    pipeline.md               the nine stages: what to do, checks, example prompts
    unity-quest.md            Blender → Unity → Quest rules
    rendering.md              photoreal exterior, film, reels (optional)
    lessons.md                every problem we hit and the fix
  scripts/
    gpu_on.py                 force GPU rendering in headless Blender
    export_unity_gltf.py      Blender → .gltf with separate textures for Unity
    fix_textures.py           unplug missing textures (pink renders)
  examples/kochi-house/       the real scripts from the reference project (paths are project-specific)
docs/
  MYST-Edge_Build-Guide_AI-House-to-VR.pdf   the illustrated build guide
```

## AI drafts, architects decide

The skill keeps people in charge of design judgment, structural design and sign-off, statutory approvals, vendor quotes and the final check of every drawing. Its drawings are for client approval, not construction. Building-rule assumptions are flagged for verification, never claimed as approved.

## Credits

Furniture models in the reference project:
- **Sketchfab (CC-BY 4.0):** "Corner Sofa" by trystyrobot, "Dining Table Set" by uka.studio, "Bed FORSSA" by leonardgraylar, "Gaming Chair" by Kiiba, "Gaming Desktop PC" by Yolala3d.
- **Poly Haven (CC0):** furniture, textures and skies.

No third-party models are included in this repository; see [`examples/kochi-house/3D-Model-Credits.txt`](vr-house/examples/kochi-house/3D-Model-Credits.txt).

## Learn it with MYST Edge

MYST Edge runs hands-on AI training for architecture practices, on one of your live projects. Contact **Nazil**, Founder of MYST International and Lead of MYST Edge: nazil@myst.international · +91 99956 22088.

## License

MIT, see [LICENSE](LICENSE).
