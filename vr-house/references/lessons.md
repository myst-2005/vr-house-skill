# Lessons learned

Every one of these happened in the reference build.

| Problem | Fix |
|---|---|
| A separate web/VR rebuild of the house never matched the Blender look | One model: build in Blender, export that same model to Unity |
| An embedded `.glb` stored textures uncompressed, giving a 1.8 GB Quest build | Export `.gltf` with separate texture files |
| glTFast can't read WebP textures | Convert WebP to PNG/JPG during export |
| Lightmap-packing every mesh in Blender overwrote the texture UVs | Bake the shell only in Unity; put furniture on light probes |
| The Quest wasn't detected over USB | Use a data cable and allow USB debugging |
| The laptop GPU is too weak for PC VR | Build a standalone Android app for the Quest |
| EEVEE renders looked cartoonish | Cycles with PBR textures, photographed skies and real foliage |
| An infinite world volume (haze) in EEVEE blacked out the sun | Don't use a world volume in EEVEE |
| Headless Blender silently rendered on the CPU, about 7× slower | Run `gpu_on.py` at the start of every headless render |
| Imported furniture floated or sank 5–20 cm; a light panel leaked into a bedroom; a slab cut through the car | Automated floor and wall alignment check, plus close-up renders through every window, before the long render |
| Missing texture slots rendered bright pink | Unplug empty image-texture nodes (`fix_textures.py`) |
| Disks filled: the page file grew to 19 GB with Blender and Unity open | Keep plenty of free space; close Unity while Blender renders |
| The C: drive at 0 MB stalled everything | Check free space before long jobs; clear package caches |
| The Unity CLI's inline `--code` broke on quotes | Pass C# as a file: `--file Temp/x.cs` |
| The HeyGen CLI `install.sh` failed on Windows | Use the Windows zip from the release folder |
| The free on-device voice can't speak Malayalam | ElevenLabs v3 |
| The client wanted the interior visible through the exterior glass | Import the real furniture packs into the exterior scene |
| Fixed numbers typed into documents drift | Compute every BOQ figure in the build script from quantity × rate |
