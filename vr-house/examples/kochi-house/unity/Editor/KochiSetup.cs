// Kochi House VR - builds the walkthrough scene from the single Blender model (Assets/Models/KochiHouse.glb).
// Menu: Kochi > 1 Build scene, 2 Bake lighting. Also callable from the command line / script eval.
using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

public static class KochiSetup
{
    public const string ModelPath = "Assets/Models/KochiHouse/KochiHouse.gltf";
    public const string ScenePath = "Assets/Scenes/KochiHouse.unity";
    const float FF = 3.15f;

    // plan coordinates (x east, y north, z up, metres) -> Unity world.
    // glTF is (x, z, -y); glTFast mirrors X to go from right- to left-handed.
    public static Vector3 Plan(float x, float y, float z) => new Vector3(-x, z, -y);

    static readonly string[] NoOcclude = { "glass", "frost", "sheer" };
    static readonly string[] NoCollide = { "ledWarm", "ledPurple", "sheer", "screen" };
    static readonly string[] Emissive = { "ledWarm", "ledPurple", "screen" };
    static readonly string[] Floors = { "tile", "plank", "bathtile", "granite", "deck", "grass", "oak" };
    const string RigPath = "Assets/Samples/XR Interaction Toolkit/3.5.1/Starter Assets/Prefabs/XR Origin (XR Rig).prefab";

    static string ShellKind(Transform t)
    {
        for (var p = t; p != null; p = p.parent)
            if (p.name.StartsWith("SHELL_"))
            {
                var parts = p.name.Substring(6).Split('_');
                return parts[0];
            }
        return null;
    }

    [MenuItem("Kochi/1 Build scene")]
    public static void BuildScene()
    {
        System.IO.Directory.CreateDirectory("Assets/Materials");
        AssetDatabase.Refresh();
        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        var model = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
        if (model == null) { Debug.LogError("Kochi: model not found at " + ModelPath); return; }
        var house = (GameObject)PrefabUtility.InstantiatePrefab(model);
        house.name = "KochiHouse";

        var emissiveMats = new Dictionary<string, Material>();
        int colliders = 0, boxes = 0;
        foreach (var r in house.GetComponentsInChildren<MeshRenderer>(true))
        {
            var go = r.gameObject;
            var kind = ShellKind(go.transform);
            bool seeThrough = kind != null && NoOcclude.Contains(kind);

            var flags = StaticEditorFlags.BatchingStatic | StaticEditorFlags.ReflectionProbeStatic | StaticEditorFlags.OccludeeStatic;
            if (!seeThrough) flags |= StaticEditorFlags.ContributeGI | StaticEditorFlags.OccluderStatic;
            GameObjectUtility.SetStaticEditorFlags(go, flags);
            if (seeThrough)
            {
                r.shadowCastingMode = ShadowCastingMode.Off;          // glass and sheers must not block the sun in the bake
                r.receiveGI = ReceiveGI.LightProbes;
            }
            else r.receiveGI = ReceiveGI.Lightmaps;

            // glowing LED strips / screens: an emissive URP Lit material that also lights the room in the bake
            if (kind != null && Emissive.Contains(kind))
            {
                if (!emissiveMats.TryGetValue(kind, out var em))
                {
                    var src = r.sharedMaterial;
                    Color c = kind == "ledPurple" ? new Color(0.60f, 0.48f, 1f) : kind == "screen" ? new Color(0.13f, 0.2f, 0.33f) : new Color(1f, 0.85f, 0.66f);
                    em = new Material(Shader.Find("Universal Render Pipeline/Lit")) { name = "Emissive_" + kind };
                    em.SetColor("_BaseColor", c);
                    em.EnableKeyword("_EMISSION");
                    em.SetColor("_EmissionColor", c * (kind == "screen" ? 1.2f : 3.0f));
                    em.globalIlluminationFlags = MaterialGlobalIlluminationFlags.BakedEmissive;
                    AssetDatabase.DeleteAsset($"Assets/Materials/Emissive_{kind}.mat"); AssetDatabase.CreateAsset(em, $"Assets/Materials/Emissive_{kind}.mat");
                    emissiveMats[kind] = em;
                }
                r.sharedMaterial = em;
            }

            var mf = go.GetComponent<MeshFilter>();
            if (mf == null || mf.sharedMesh == null) continue;
            if (kind != null)
            {
                if (!NoCollide.Contains(kind)) { go.AddComponent<MeshCollider>().sharedMesh = mf.sharedMesh; colliders++; }
            }
            else
            {
                // furniture: a simple box you can't walk through (rugs and tiny items excluded)
                var b = r.bounds;
                if (b.size.y > 0.2f && b.size.x * b.size.z < 6f && b.size.x * b.size.z > 0.02f) { go.AddComponent<BoxCollider>(); boxes++; }
            }
        }
        // teleport onto any floor-type surface (only upward-facing hits count)
        int tele = 0;
        foreach (var mc in house.GetComponentsInChildren<MeshCollider>(true))
        {
            var kind = ShellKind(mc.transform);
            if (kind == null || !Floors.Contains(kind)) continue;
            var ta = mc.gameObject.AddComponent<UnityEngine.XR.Interaction.Toolkit.Locomotion.Teleportation.TeleportationArea>();
            ta.filterSelectionByHitNormal = true; ta.upNormalToleranceDegrees = 25f;
            ta.colliders.Clear(); ta.colliders.Add(mc);
            tele++;
        }
        Debug.Log($"Kochi: {colliders} mesh colliders on the shell, {boxes} furniture boxes, {emissiveMats.Count} emissive materials, {tele} teleport areas");

        // Quest rig from XR Interaction Toolkit Starter Assets: walk (left stick), snap turn (right stick), teleport, gravity
        var rigPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(RigPath);
        if (rigPrefab == null) Debug.LogError("Kochi: XR rig prefab not found at " + RigPath);
        else
        {
            var rig = (GameObject)PrefabUtility.InstantiatePrefab(rigPrefab);
            rig.transform.position = Plan(9.2f, 13.1f, 0f);
            var cc = rig.GetComponent<CharacterController>();
            if (cc) { cc.stepOffset = 0.3f; cc.slopeLimit = 50f; cc.radius = 0.2f; }
            var jumper = rig.AddComponent<RoomJumper>();
            jumper.origin = rig.GetComponent<Unity.XR.CoreUtils.XROrigin>();
            foreach (var cam in rig.GetComponentsInChildren<Camera>(true)) { cam.nearClipPlane = 0.05f; cam.farClipPlane = 200f; }
            new GameObject("XR Interaction Manager").AddComponent<UnityEngine.XR.Interaction.Toolkit.XRInteractionManager>();
        }

        AddLighting();
        System.IO.Directory.CreateDirectory("Assets/Scenes");
        EditorSceneManager.SaveScene(scene, ScenePath);
        EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
    }

    static void AddLighting()
    {
        // sky + sun
        var sky = new Material(Shader.Find("Skybox/Procedural")) { name = "KochiSky" };
        sky.SetFloat("_SunSize", 0.04f); sky.SetFloat("_AtmosphereThickness", 0.9f); sky.SetFloat("_Exposure", 1.25f);
        AssetDatabase.DeleteAsset("Assets/Materials/KochiSky.mat"); AssetDatabase.CreateAsset(sky, "Assets/Materials/KochiSky.mat");
        RenderSettings.skybox = sky;
        RenderSettings.ambientMode = AmbientMode.Skybox;
        RenderSettings.ambientIntensity = 1.0f;

        var sunGo = new GameObject("Sun");
        var sun = sunGo.AddComponent<Light>();
        sun.type = LightType.Directional; sun.color = new Color(1f, 0.92f, 0.8f); sun.intensity = 2.2f;
        sun.shadows = LightShadows.Soft; sun.lightmapBakeType = LightmapBakeType.Baked;
        sunGo.transform.rotation = Quaternion.LookRotation(-new Vector3(-20f, 30f, -10f).normalized);   // same sun as the design renders
        RenderSettings.sun = sun;

        // warm ceiling lamps, same positions as the lighting plan (all baked)
        var lamps = new (string, float, float, float, Color, float)[]
        {
            ("Living", 7.6f, 11.0f, 2.75f, new Color(1f, 0.79f, 0.56f), 2.6f), ("Dining", 7.4f, 6.6f, 2.75f, new Color(1f, 0.79f, 0.56f), 2.2f),
            ("Kitchen", 7.6f, 3.2f, 2.75f, new Color(1f, 0.94f, 0.87f), 2.2f), ("Mother", 1.9f, 2.1f, 2.75f, new Color(1f, 0.79f, 0.56f), 1.6f),
            ("Office", 4.1f, 10.2f, 2.75f, new Color(1f, 0.94f, 0.87f), 1.6f), ("Hall", 3.8f, 6.0f, 2.75f, new Color(1f, 0.85f, 0.7f), 1.2f),
            ("Master", 7.6f, 11.4f, FF + 2.65f, new Color(1f, 0.79f, 0.56f), 2.2f), ("Gaming", 6.4f, 5.2f, FF + 2.65f, new Color(0.6f, 0.48f, 1f), 1.8f),
            ("Children", 1.9f, 11.0f, FF + 2.65f, new Color(1f, 0.82f, 0.63f), 2.0f), ("Lobby", 4.2f, 8.4f, FF + 2.65f, new Color(1f, 0.85f, 0.7f), 1.2f),
            ("Bath GF", 1.5f, 4.7f, 2.75f, Color.white, 0.9f), ("Bath mother", 4.5f, 1.5f, 2.75f, Color.white, 0.9f),
            ("Bath kids", 4.5f, 12.3f, FF + 2.65f, Color.white, 0.9f), ("Bath master", 8.5f, 7.9f, FF + 2.65f, Color.white, 0.9f),
        };
        var lampRoot = new GameObject("Lamps");
        foreach (var (n, x, y, z, c, i) in lamps)
        {
            var go = new GameObject("Lamp " + n);
            go.transform.SetParent(lampRoot.transform);
            go.transform.position = Plan(x, y, z);
            var l = go.AddComponent<Light>();
            l.type = LightType.Point; l.color = c; l.intensity = i; l.range = 7f;
            l.shadows = LightShadows.Soft; l.lightmapBakeType = LightmapBakeType.Baked;
        }

        // reflection probes per room (box projected) for believable reflections on floors, steel and glass
        var probes = new (string, float, float, float, float, float, float)[]
        {
            ("Living", 5.5f, 9.76f, 8.75f, 13.56f, 0f, 3f), ("Dining", 5.0f, 9.76f, 5.0f, 8.75f, 0f, 3f), ("Kitchen", 5.5f, 9.76f, 0.23f, 4.9f, 0f, 3f),
            ("Mother", 0.23f, 3.58f, 0.23f, 3.89f, 0f, 3f), ("Office", 3.0f, 5.39f, 8.75f, 11.6f, 0f, 3f), ("Hall", 2.9f, 5.39f, 4.0f, 8.75f, 0f, 3f),
            ("Master", 5.5f, 9.76f, 9.29f, 13.56f, FF, FF + 2.9f), ("Gaming", 3.0f, 9.76f, 4.0f, 6.5f, FF, FF + 2.9f),
            ("Children", 0.23f, 3.58f, 8.75f, 13.56f, FF, FF + 2.9f), ("Lobby", 2.9f, 5.39f, 6.5f, 11.0f, FF, FF + 2.9f),
            ("Terrace", 0.23f, 9.76f, 0.23f, 3.78f, FF, FF + 3f), ("Porch", 0f, 2.9f, 8.75f, 13.9f, -0.45f, 3f),
        };
        var probeRoot = new GameObject("Reflection probes");
        foreach (var (n, x1, x2, y1, y2, z1, z2) in probes)
        {
            var go = new GameObject("Probe " + n);
            go.transform.SetParent(probeRoot.transform);
            go.transform.position = Plan((x1 + x2) / 2, (y1 + y2) / 2, z1 + 1.4f);
            var p = go.AddComponent<ReflectionProbe>();
            p.mode = ReflectionProbeMode.Baked; p.boxProjection = true; p.resolution = 128;
            p.size = new Vector3(x2 - x1, z2 - z1, y2 - y1);
            p.center = Plan((x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2) - go.transform.position;
        }
    }

    [MenuItem("Kochi/2 Bake lighting")]
    public static void Bake()
    {
        var s = new LightingSettings
        {
            name = "KochiLighting",
            bakedGI = true, realtimeGI = false,
            lightmapper = LightingSettings.Lightmapper.ProgressiveGPU,
            lightmapResolution = 14f, lightmapPadding = 3, lightmapMaxSize = 2048,
            directSampleCount = 32, indirectSampleCount = 256, environmentSampleCount = 128, maxBounces = 3,
            ao = true, aoMaxDistance = 0.6f, aoExponentIndirect = 1f, aoExponentDirect = 0f,
            lightmapCompression = LightmapCompression.NormalQuality,
            directionalityMode = LightmapsMode.NonDirectional,
            mixedBakeMode = MixedLightingMode.Subtractive,
        };
        AssetDatabase.DeleteAsset("Assets/Scenes/KochiLighting.lighting"); AssetDatabase.CreateAsset(s, "Assets/Scenes/KochiLighting.lighting");
        Lightmapping.lightingSettings = s;
        Lightmapping.Bake();
        EditorSceneManager.SaveOpenScenes();
    }
}
