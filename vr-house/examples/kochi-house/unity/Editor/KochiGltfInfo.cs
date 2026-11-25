// minimal glTF JSON shape, used by the editor scripts to tag normal-map textures
[System.Serializable] public class KochiGltfInfo { public KMat[] materials; public KTex[] textures; public KImg[] images; }
[System.Serializable] public class KMat { public KTexRef normalTexture; public KTexRef occlusionTexture; public KPbr pbrMetallicRoughness; }
[System.Serializable] public class KPbr { public KTexRef metallicRoughnessTexture; }
[System.Serializable] public class KTexRef { public int index = -1; public float scale = 1; }
[System.Serializable] public class KTex { public int source; }
[System.Serializable] public class KImg { public string uri; }
