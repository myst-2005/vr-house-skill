# Photoreal exterior, film and reels (optional)

These are marketing assets made from the same model after the client package.

## Photoreal day-to-night exterior (Blender Cycles)

Quick real-time renders (EEVEE) looked cartoonish to the client. What fixed it:

**Engine**
- Cycles path tracing on the GPU (OptiX), with denoising.
- Reference settings: 56 samples with adaptive sampling, persistent data, motion blur.
- Speed on an RTX 2050: about 19 s per 1920 × 1080 frame.
- 991 frames took about 5 h overnight. Render only the frames the film uses.

**Materials and setting**
- Poly Haven PBR textures for grass, asphalt, plaster, roof tiles, paving, concrete walls and bark, box-projected so no UVs are needed.
- Two photographed skies: a cloudy day sky and a sunset sky, blended by sun height over a night colour.
- Coconut palms with real drooping fronds: alpha-textured cards, not flat blades.
- 3D grass on the near lawns.
- Neighbour houses with plinths, porches, pillars, sunshades and tiled roofs.
- A ring of distant houses and palms, so the horizon isn't empty.

**Interiors through the glass**
- Import the real furniture packs into the exterior scene, parented to per-floor empties, so they rise with the floors in a "house builds itself" animation.

**Before the long render**
- Run an alignment check: raycast each piece to the floor under it, and check overlap with the walls.
- Render close-ups through every window.

The reference found:
- ground-floor furniture 5 cm into the floor;
- sit-out chairs 20 cm sunk;
- a floor slab cutting through the car at wheel height;
- a porch light panel floating inside a bedroom;
- pink wheel rims, from empty texture slots (unplug them; see `scripts/fix_textures.py`).

Scripts: `examples/kochi-house/render/`. `realism.py`, `realism2.py` and `photoreal.py` set up the look; `align_check.py` and `align_fix.py` run the alignment pass; `cycles_setup.py` and `final_settings.py` configure the render. Always run `scripts/gpu_on.py` first.

## Launch film (HyperFrames)

The reference made a 61 s launch film in HyperFrames, with HTML compositions rendered to MP4:
- **Picture:** the exterior footage, the real drawings drawing in, a proof montage (E1, P1, renders, the BOQ total), the VR flights, a "6 h 40 min" claim and an end card.
- **Sound:** voiceover, a music bed, a few sound effects; final mix at about −16 LUFS for social video.

## Malayalam + English reel

The reel was 45 s, 9:16.
- **Voice:** ElevenLabs Eleven v3. Generate it scene by scene, so each line lands on its picture. Spell numbers the way they should be read, and check "Claude" and "BOQ" are pronounced right.
- **Picture:** reframe 16:9 footage to 9:16 using a crop centre per shot, so the window stays on the subject.
- **Opening:** an AI-generated plot photo is fine, but never caption it as the real site.
- **Rules beat:** a "rules first" beat showing the building-rules notes from the plan sheet.
- **Reference beat:** the client's reference photo shown beside the finished house. Check you have the rights to the reference images first.
