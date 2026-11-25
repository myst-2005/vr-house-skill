"""Download the Poly Haven (CC0) assets used by the realism pass into video/blender/ph/."""
import json
import os
import urllib.request

OUT = r"D:\Kochi-Residence-Interior\video\blender\ph"
os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "kochi-house-film/1.0"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
        return r.read()


def save(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(get(url))


TEXTURES = ["aerial_grass_rock", "aerial_asphalt_01", "painted_plaster_wall", "damaged_plaster", "clay_roof_tiles_02",
            "rectangular_paving", "concrete_wall_006", "bark_brown_02"]
for name in TEXTURES:
    files = json.loads(get(f"https://api.polyhaven.com/files/{name}"))
    for key, want in (("Diffuse", "diff"), ("nor_gl", "nor"), ("Rough", "rough")):
        if key in files and "2k" in files[key]:
            url = files[key]["2k"]["jpg"]["url"]
            save(url, os.path.join(OUT, "tex", f"{name}_{want}.jpg"))
    print("tex", name)

for name in ["kloofendal_48d_partly_cloudy_puresky", "belfast_sunset_puresky"]:
    files = json.loads(get(f"https://api.polyhaven.com/files/{name}"))
    save(files["hdri"]["2k"]["exr"]["url"], os.path.join(OUT, "hdri", f"{name}_2k.exr"))
    print("hdri", name)

for name in ["shrub_02", "street_lamp_01"]:
    files = json.loads(get(f"https://api.polyhaven.com/files/{name}"))
    g = files["gltf"]["1k"]["gltf"]
    base = os.path.join(OUT, "models", name)
    save(g["url"], os.path.join(base, f"{name}_1k.gltf"))
    for rel, info in g.get("include", {}).items():
        save(info["url"], os.path.join(base, rel))
    print("model", name)

total = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(OUT) for f in fs)
print("total MB", round(total / 1e6, 1))
