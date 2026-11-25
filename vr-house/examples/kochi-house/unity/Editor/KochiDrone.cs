// Renders the "drone" flythrough of the baked house to numbered JPGs for the launch film.
using System.Collections.Generic;
using System.IO;
using UnityEngine;

public static class KochiDrone
{
    static Vector3 P(float x, float y, float z) => new Vector3(-x, z, -y);   // plan (x east, y north, z up) -> Unity
    const float FF = 3.15f;

    // shot A, ground floor: from just inside the front glass, across the living room to the dining table and the stair
    public static readonly Vector3[] PathA =
    {
        P(8.4f, 13.25f, 1.85f), P(8.0f, 11.6f, 1.65f), P(7.5f, 10.0f, 1.5f), P(7.0f, 8.6f, 1.45f), P(6.6f, 7.7f, 1.45f),
    };
    public static readonly Vector3[] LookA =
    {
        P(6.8f, 9.0f, 1.0f), P(6.0f, 9.8f, 1.1f), P(7.4f, 6.8f, 1.0f), P(7.6f, 5.6f, 1.0f), P(8.0f, 3.6f, 1.1f),
    };
    // shot B, first floor: lobby, through the gaming-room door, up to the desk
    public static readonly Vector3[] PathB =
    {
        P(4.65f, 7.05f, FF + 1.55f), P(4.8f, 6.1f, FF + 1.5f), P(6.2f, 5.1f, FF + 1.45f), P(7.2f, 5.0f, FF + 1.35f),
    };
    public static readonly Vector3[] LookB =
    {
        P(5.0f, 4.9f, FF + 1.25f), P(7.0f, 5.4f, FF + 1.2f), P(7.8f, 6.3f, FF + 1.1f), P(7.8f, 6.4f, FF + 1.0f),
    };
    static Vector3 CatmullRom(Vector3[] p, float t)
    {
        int n = p.Length - 1;
        float s = Mathf.Clamp01(t) * n;
        int i = Mathf.Min((int)s, n - 1);
        float u = s - i;
        Vector3 p0 = p[Mathf.Max(i - 1, 0)], p1 = p[i], p2 = p[i + 1], p3 = p[Mathf.Min(i + 2, n)];
        return 0.5f * (2 * p1 + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u * u * u);
    }

    static float Ease(float t) => t * t * (3 - 2 * t);

    public static string Render(Vector3[] Path, Vector3[] Look, string outDir, int frames, int width, int height, bool preview)
    {
        Directory.CreateDirectory(outDir);
        var go = new GameObject("DroneCam");
        var cam = go.AddComponent<Camera>();
        cam.fieldOfView = 68; cam.nearClipPlane = 0.05f; cam.farClipPlane = 300f;
        cam.clearFlags = CameraClearFlags.SolidColor;
        cam.backgroundColor = new Color(0.03f, 0.05f, 0.11f);       // night outside the windows
        // film look for the video (not used in the Quest app): ACES tone mapping, a little contrast, gentle bloom on lamps
        var camData = UnityEngine.Rendering.Universal.CameraExtensions.GetUniversalAdditionalCameraData(cam);
        camData.renderPostProcessing = true;
        camData.antialiasing = UnityEngine.Rendering.Universal.AntialiasingMode.SubpixelMorphologicalAntiAliasing;
        camData.antialiasingQuality = UnityEngine.Rendering.Universal.AntialiasingQuality.High;
        var volGo = new GameObject("DroneLook");
        var vol = volGo.AddComponent<UnityEngine.Rendering.Volume>();
        vol.isGlobal = true; vol.priority = 100;
        var prof = ScriptableObject.CreateInstance<UnityEngine.Rendering.VolumeProfile>();
        var tm = prof.Add<UnityEngine.Rendering.Universal.Tonemapping>(true);
        tm.mode.Override(UnityEngine.Rendering.Universal.TonemappingMode.ACES);
        var ca = prof.Add<UnityEngine.Rendering.Universal.ColorAdjustments>(true);
        ca.postExposure.Override(0.45f); ca.contrast.Override(12f); ca.saturation.Override(6f);
        var bl = prof.Add<UnityEngine.Rendering.Universal.Bloom>(true);
        bl.threshold.Override(1.05f); bl.intensity.Override(0.35f); bl.scatter.Override(0.6f);
        vol.sharedProfile = prof;
        // night outside: hide the sunlit lawn so the windows read as night, like the exterior shot before it
        var hidden = new List<Renderer>();
        foreach (var r in Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None))
            if (r.enabled && r.gameObject.name.StartsWith("SHELL_grass")) { r.enabled = false; hidden.Add(r); }
        var rt = new RenderTexture(width, height, 24) { antiAliasing = 8 };
        cam.targetTexture = rt;
        var tex = new Texture2D(width, height, TextureFormat.RGB24, false);
        var list = new List<int>();
        if (preview) { for (int k = 0; k < 9; k++) list.Add(k * (frames - 1) / 8); } else for (int f = 0; f < frames; f++) list.Add(f);
        Vector3 smoothLook = CatmullRom(Look, 0);
        foreach (var f in list)
        {
            float t = Ease(f / (float)(frames - 1));
            var pos = CatmullRom(Path, t);
            var look = CatmullRom(Look, t);
            go.transform.position = pos;
            go.transform.rotation = Quaternion.LookRotation(look - pos, Vector3.up);
            cam.Render();
            RenderTexture.active = rt;
            tex.ReadPixels(new Rect(0, 0, width, height), 0, 0);
            tex.Apply();
            File.WriteAllBytes(Path_(outDir, f), tex.EncodeToJPG(92));
        }
        RenderTexture.active = null;
        Object.DestroyImmediate(go);
        Object.DestroyImmediate(volGo);
        foreach (var r in hidden) r.enabled = true;
        rt.Release();
        return $"rendered {list.Count} frames to {outDir}";
    }

    static string Path_(string dir, int f) => System.IO.Path.Combine(dir, $"d_{f:0000}.jpg");
}
