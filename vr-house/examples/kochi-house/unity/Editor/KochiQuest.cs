// Quest (Android, OpenXR) build settings + APK build for the Kochi House walkthrough.
using System.Linq;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.XR.Management;
using UnityEngine;
using UnityEngine.XR.Management;
using UnityEngine.XR.OpenXR;

public static class KochiQuest
{
    public const string ApkPath = "D:/Kochi-Residence-Interior/vr/KochiHouseVR.apk";

    [MenuItem("Kochi/3 Configure for Quest")]
    public static string Configure()
    {
        var log = new System.Text.StringBuilder();
        if (EditorUserBuildSettings.activeBuildTarget != BuildTarget.Android)
            log.Append("switch to Android: " + EditorUserBuildSettings.SwitchActiveBuildTarget(BuildTargetGroup.Android, BuildTarget.Android) + "; ");
        EditorUserBuildSettings.androidBuildSubtarget = MobileTextureSubtarget.ASTC;

        PlayerSettings.companyName = "Kochi Residence";
        PlayerSettings.productName = "Kochi House VR";
        PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.Android, "com.kochiresidence.housevr");
        PlayerSettings.SetScriptingBackend(NamedBuildTarget.Android, ScriptingImplementation.IL2CPP);
        PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
        PlayerSettings.Android.minSdkVersion = (AndroidSdkVersions)32;
        PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android, false);
        PlayerSettings.SetGraphicsAPIs(BuildTarget.Android, new[] { UnityEngine.Rendering.GraphicsDeviceType.Vulkan });
        PlayerSettings.colorSpace = ColorSpace.Linear;
        PlayerSettings.defaultInterfaceOrientation = UIOrientation.LandscapeLeft;
        PlayerSettings.SetMobileMTRendering(NamedBuildTarget.Android, true);

        // XR plug-in management: OpenXR on Android, with Meta Quest support on
        var gs = XRGeneralSettingsPerBuildTarget.XRGeneralSettingsForBuildTarget(BuildTargetGroup.Android);
        if (gs == null) { log.Append("no XR general settings for Android; "); }
        else
        {
            var mgr = gs.Manager;
            gs.InitManagerOnStart = true;
            bool has = mgr.activeLoaders.Any(l => l is OpenXRLoader);
            if (!has) log.Append("assign OpenXR loader: " + UnityEditor.XR.Management.Metadata.XRPackageMetadataStore.AssignLoader(mgr, "UnityEngine.XR.OpenXR.OpenXRLoader", BuildTargetGroup.Android) + "; ");
            foreach (var l in mgr.activeLoaders) log.Append("loader " + l.GetType().Name + "; ");
        }
        var oxr = OpenXRSettings.GetSettingsForBuildTargetGroup(BuildTargetGroup.Android);
        if (oxr != null)
        {
            foreach (var f in oxr.GetFeatures())
            {
                var t = f.GetType().Name;
                // Meta Quest support + controller profiles on; Android XR / hand-tracking extras off (smaller, simpler)
                if (t.Contains("MetaQuestFeature") || t.Contains("OculusTouchControllerProfile") || t.Contains("MetaQuestTouchPlusControllerProfile") || t.Contains("MetaQuestTouchProControllerProfile"))
                    f.enabled = true;
                if (t.Contains("OculusQuestFeature")) f.enabled = false;     // legacy duplicate of MetaQuestFeature
                if (t.StartsWith("AndroidXR") || t.Contains("HandTracking") || t.Contains("HandInteraction") || t.Contains("PalmPose") || t.Contains("HandCommonPoses"))
                    f.enabled = false;
                if (f.enabled) log.Append("on: " + t + "; ");
            }
            oxr.renderMode = OpenXRSettings.RenderMode.SinglePassInstanced;
        }
        AssetDatabase.SaveAssets();
        return log.ToString();
    }

    [MenuItem("Kochi/4 Build Quest APK")]
    public static string Build()
    {
        var opts = new BuildPlayerOptions
        {
            scenes = new[] { KochiSetup.ScenePath },
            locationPathName = ApkPath,
            target = BuildTarget.Android,
            options = BuildOptions.None,
        };
        var report = BuildPipeline.BuildPlayer(opts);
        var s = report.summary;
        return $"{s.result} in {s.totalTime.TotalMinutes:0.0} min, {s.totalSize / 1e6:0} MB, errors {s.totalErrors}";
    }
}
