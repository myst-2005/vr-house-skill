# Blender to Unity to Meta Quest

The VR app is the same Blender model, made walkable. The rules below each come from a failure in the reference build.

## The chain

```
Blender packs (shell + one .glb per room)
  → assemble_house.py          one scene, plan coordinates, texture UVs untouched
  → export_unity_gltf.py       .gltf + separate JPG textures, written into the Unity project
  → Unity editor script        scene, XR rig, colliders, teleport, lamps, probes
  → bake lightmaps             shell only
  → build Android APK          OpenXR + Meta OpenXR
  → adb install -r app.apk
```

Use `scripts/export_unity_gltf.py` for the export step. The `examples/kochi-house/` folder has the assembly script and the Unity editor scripts (`KochiSetup`, `KochiQuest`, `KochiFinish`, `RoomJumper`).

## Rules

1. **One model.** Don't rebuild the house separately for VR or the web. An early attempt rebuilt it from blocks in three.js, and it never matched the renders. The client should walk the house they saw.
2. **Export `.gltf` with separate textures,** not an embedded `.glb`. glTFast stores embedded textures uncompressed: the first Quest build was 1.8 GB. With separate files, Unity's texture importer compresses them (ASTC on Quest).
3. **No WebP.** glTFast can't read WebP. Convert to PNG or JPG during export.
4. **Don't lightmap-pack every mesh in Blender.** It overwrote the texture UVs. Let Unity generate lightmap UVs for the shell, bake the shell only, and put furniture on light probes.
5. **Standalone, not Link.** A laptop GPU like the RTX 2050 can't drive PC VR. Build for Android, so the app runs on the headset.
6. **Comfort:**
   - smooth walk on the left stick;
   - snap-turn on the right stick;
   - trigger to aim and release to teleport onto any floor;
   - A/X and B/Y to jump to the next or previous room;
   - stairs walkable; room-scale works too.
7. **Cables:** use a USB data cable and allow USB debugging. The reference lost time to a charge-only cable.
8. **Drive the Editor with files:** `unity command script eval --file Temp/x.cs`. Inline `--code` breaks on quotes. Put the build behind Editor menu items, so a person can rebuild without Claude.

## Optional: film-look drone shots from the VR scene

Render camera paths from the Unity scene with an offscreen camera:
- a Volume with ACES tone mapping, a little contrast and gentle bloom;
- SMAA anti-aliasing;
- hide sunlit-lawn meshes for a night look.

The reference got a 7 s ground-floor flight and a 6 s gaming-room flight this way (`examples/kochi-house/unity/Editor/KochiDrone.cs`).
