// Kochi: full rebuild = build scene, furniture on light probes, Unity lightmap UVs for the house shell, bake.
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class KochiFinish
{
    static Vector3 P(float x, float y, float z) => new Vector3(-x, z, -y);
    const float FF = 3.15f;

    [MenuItem("Kochi/Rebuild + bake (all)")]
    public static string RebuildAndBake()
    {
        AssetDatabase.DeleteAsset("Assets/Materials/Furniture");
        KochiSetup.BuildScene();
        AssetDatabase.CreateFolder("Assets", "Meshes");
        int shells = 0, furn = 0;
        foreach (var r in Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None))
        {
            bool isShell = false;
            for (var p = r.transform; p != null; p = p.parent) if (p.name.StartsWith("SHELL_")) { isShell = true; break; }
            var mf = r.GetComponent<MeshFilter>();
            if (isShell)
            {
                if (r.receiveGI != ReceiveGI.Lightmaps || mf == null || mf.sharedMesh == null) continue;
                var path = "Assets/Meshes/" + r.gameObject.name + ".asset";
                var m = Object.Instantiate(mf.sharedMesh); m.name = r.gameObject.name;
                UnwrapParam.SetDefaults(out var up); up.packMargin = 4f / 1024f;
                Unwrapping.GenerateSecondaryUVSet(m, up);
                AssetDatabase.DeleteAsset(path); AssetDatabase.CreateAsset(m, path);
                mf.sharedMesh = m;
                var mc = r.GetComponent<MeshCollider>(); if (mc) mc.sharedMesh = m;
                if (r.gameObject.name.StartsWith("SHELL_grass")) SetScale(r, 0.03f);
                else if (r.gameObject.name.StartsWith("SHELL_granite")) SetScale(r, 0.5f);
                shells++;
            }
            else
            {
                r.receiveGI = ReceiveGI.LightProbes;              // furniture: lit by probes, still bounces light
                r.lightProbeUsage = UnityEngine.Rendering.LightProbeUsage.BlendProbes;
                furn++;
            }
        }
        AddProbes();
        foreach (var l in Object.FindObjectsByType<Light>(FindObjectsSortMode.None))
        {
            if (l.type == LightType.Point) { l.intensity *= 1.3f; l.range = 8f; }
            if (l.type == LightType.Directional) l.intensity = 1.6f;
        }
        var s = new LightingSettings
        {
            name = "KochiLighting", bakedGI = true, realtimeGI = false,
            lightmapper = LightingSettings.Lightmapper.ProgressiveGPU,
            lightmapResolution = 20f, lightmapPadding = 3, lightmapMaxSize = 2048,
            directSampleCount = 32, indirectSampleCount = 384, environmentSampleCount = 128, maxBounces = 4,
            indirectScale = 1.2f, albedoBoost = 1.1f,
            ao = true, aoMaxDistance = 0.5f, aoExponentIndirect = 1f, aoExponentDirect = 0f,
            lightmapCompression = LightmapCompression.NormalQuality,
            directionalityMode = LightmapsMode.NonDirectional,
            mixedBakeMode = MixedLightingMode.Subtractive,
        };
        AssetDatabase.DeleteAsset("Assets/Scenes/KochiLighting.lighting");
        AssetDatabase.CreateAsset(s, "Assets/Scenes/KochiLighting.lighting");
        Lightmapping.lightingSettings = s;
        EditorSceneManager.MarkSceneDirty(UnityEngine.SceneManagement.SceneManager.GetActiveScene());
        EditorSceneManager.SaveOpenScenes();
        Lightmapping.Clear();
        return $"shell {shells}, furniture {furn}, bake started {Lightmapping.BakeAsync()}";
    }

    static void SetScale(Renderer r, float v)
    {
        var so = new SerializedObject(r);
        so.FindProperty("m_ScaleInLightmap").floatValue = v;
        so.ApplyModifiedPropertiesWithoutUndo();
    }

    static void AddProbes()
    {
        var go = new GameObject("Light probes");
        var lpg = go.AddComponent<LightProbeGroup>();
        var rooms = new (float x1, float x2, float y1, float y2, float z)[] {
            (5.5f, 9.76f, 8.75f, 13.56f, 0f), (5.0f, 9.76f, 5.0f, 8.75f, 0f), (5.5f, 9.76f, 0.23f, 4.9f, 0f), (0.23f, 3.58f, 0.23f, 3.89f, 0f),
            (3.0f, 5.39f, 8.75f, 11.6f, 0f), (2.9f, 5.39f, 4.0f, 8.75f, 0f), (0.23f, 2.89f, 4.0f, 5.32f, 0f), (3.7f, 5.39f, 0.23f, 2.67f, 0f),
            (3.0f, 5.39f, 11.7f, 13.79f, -0.15f), (0f, 2.89f, 8.75f, 13.9f, -0.45f), (0.23f, 2.89f, 5.43f, 8.6f, 0f),
            (5.5f, 9.76f, 9.29f, 13.56f, FF), (3.0f, 9.76f, 4.0f, 6.5f, FF), (0.23f, 3.58f, 8.75f, 13.56f, FF), (2.9f, 5.39f, 6.5f, 11.0f, FF),
            (0.23f, 9.76f, 0.23f, 3.78f, FF), (5.5f, 7.19f, 6.62f, 9.17f, FF), (7.3f, 9.76f, 6.62f, 9.17f, FF), (3.7f, 5.39f, 11.12f, 13.56f, FF), (0.23f, 2.89f, 4.0f, 5.32f, FF),
        };
        var pts = new List<Vector3>();
        foreach (var rm in rooms)
        {
            int nx = Mathf.Max(2, Mathf.CeilToInt((rm.x2 - rm.x1) / 0.9f)), ny = Mathf.Max(2, Mathf.CeilToInt((rm.y2 - rm.y1) / 0.9f));
            for (int i = 0; i <= nx; i++) for (int j = 0; j <= ny; j++) foreach (var h in new[] { 0.4f, 1.3f, 2.3f })
                pts.Add(P(Mathf.Lerp(rm.x1 + 0.15f, rm.x2 - 0.15f, i / (float)nx), Mathf.Lerp(rm.y1 + 0.15f, rm.y2 - 0.15f, j / (float)ny), rm.z + h));
        }
        lpg.probePositions = pts.ToArray();
    }
}
