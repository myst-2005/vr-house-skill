# Workstation setup and tool connections

Set these up once and test each before starting a project. Commands are for Windows, because AutoCAD automation (COM) is Windows-only.

## Contents
1. Hardware
2. Core software
3. Claude and MCP connectors
4. AutoCAD connector (MCP)
5. Blender
6. Unity and the Unity connector
7. Meta Quest 3S
8. Video tools (optional)

## 1. Hardware

The reference build ran on a Windows 11 laptop with an NVIDIA RTX 2050 laptop GPU and 16 GB of RAM. That was enough for everything. It is too weak for PC VR (Quest Link), which is why the VR is a standalone Android app on the headset.

Leave plenty of free disk space on every drive. With Blender and Unity open together, Windows' page file grew to 19 GB, and a 991-frame render sequence is several GB.

## 2. Core software

- Python 3.11 (add to PATH) and Git.
- AutoCAD for Windows. The reference used AutoCAD 2027; any recent version with COM automation works.
- Blender 5.x (reference: 5.2).
- Unity Hub with Unity 6 (reference: 6000.3.x).
- FFmpeg and Node.js LTS, only for video.

A Python environment for documents and AutoCAD scripts:

```
python -m venv tools\.pdfenv
tools\.pdfenv\Scripts\pip install reportlab pypdf pillow pypdfium2 pyautocad
```

## 3. Claude and MCP connectors

Use Claude Code: the Claude desktop app's Code tab, or the CLI. Open the project folder as the working directory, so Claude can read and write files and run commands.

The desktop app lists MCP connectors in `%APPDATA%\Claude\claude_desktop_config.json` under `"mcpServers"`. Restart the app after each change. In the Claude Code CLI, `claude mcp add` does the same job.

## 4. AutoCAD connector (MCP)

The reference used the open-source server at https://github.com/vigneshpbmenon/autocad-mcp-server. It depends on `fastmcp` and `pyautocad`.

```
git clone https://github.com/vigneshpbmenon/autocad-mcp-server.git %USERPROFILE%\mcp-servers\autocad-mcp-server
cd %USERPROFILE%\mcp-servers\autocad-mcp-server
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

Config entry (replace `<you>`):

```json
{
  "mcpServers": {
    "autocad": {
      "command": "C:\\Users\\<you>\\mcp-servers\\autocad-mcp-server\\.venv\\Scripts\\python.exe",
      "args": ["C:\\Users\\<you>\\mcp-servers\\autocad-mcp-server\\server.py"]
    }
  }
}
```

**Start AutoCAD and open a drawing before starting Claude.** The connector attaches to the running AutoCAD.

The connector's tools are `draw_line`, `draw_polyline`, `draw_rectangle`, `draw_circle`, `draw_ellipse` and `draw_arc`. For text, dimensions, layers, saving DWG and plotting PDF, write Python scripts with `pyautocad` that drive the same AutoCAD. See `examples/kochi-house/autocad/export_plan.py` and `mep_sheets.py`.

Test: "Draw a 10,000 × 10,000 rectangle at 0,0 in AutoCAD."

## 5. Blender

No connector is needed: run Blender headless with Python scripts.

```
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b scene.blend --python tools\script.py -- [args]
```

- For GPU rendering, run `scripts/gpu_on.py` first in every headless Cycles session:

  ```
  blender -b scene.blend --python scripts\gpu_on.py --python render.py
  ```

  The device choice is a user preference, not saved in the .blend.
- Optional: a Blender MCP connector (an add-on inside Blender plus an MCP server) lets Claude drive a live Blender window and look at the viewport. Useful for interactive layout; the reference build used headless scripts.

Test: "Run Blender headless and print its version and the GPUs Cycles can see."

## 6. Unity and the Unity connector

1. In Unity Hub, install Unity 6 with **Android Build Support** (OpenJDK, Android SDK & NDK).
2. Create a project from the **VR** template (URP). Add these packages:

   | Package | Version used |
   |---|---|
   | glTFast | 6.21 |
   | OpenXR | 1.17 |
   | Meta OpenXR | 2.5 |
   | XR Interaction Toolkit | 3.5 |

3. Connect Claude through Unity's command-line tool, which can also run as an MCP server:

   ```json
   "unity": {
     "command": "C:\\Users\\<you>\\AppData\\Local\\Unity\\bin\\unity.exe",
     "args": ["mcp", "--project-path", "D:\\<Project>\\unity\\<UnityProject>"]
   }
   ```

4. With the Editor open, run C# inside it from a file. Inline code breaks on quotes.

   ```
   unity status --project-path <project>
   unity command script eval --file Temp/build.cs --project-path <project>
   ```

The reference project also put its whole build behind Editor menu items (`Kochi > Rebuild + bake (all)`, `Kochi > Build Quest APK`). That way a person can rebuild without Claude. See `examples/kochi-house/unity/Editor/`.

Test: "Check the Unity Editor is connected and list the scenes in the project."

## 7. Meta Quest 3S

1. In the Meta Horizon phone app, enable **Developer Mode** for the headset (needs a Meta developer account).
2. Connect with a USB **data** cable. A charge-only cable is not detected. Accept "Allow USB debugging" inside the headset.
3. Install with the `adb` that ships in Unity's Android module:

   ```
   "<Unity editor>\Data\PlaybackEngines\AndroidPlayer\SDK\platform-tools\adb.exe" install -r vr\House.apk
   ```

4. On the headset: Library → Unknown Sources.

## 8. Video tools (optional)

- **HyperFrames** (HTML compositions rendered to MP4): `npx hyperframes init` in a video folder. Needs Node.js and FFmpeg.
- **Music and sound effects:** `npx hyperframes auth login` (free HeyGen account). On Windows, use the HeyGen CLI's Windows zip from its release folder, because the `install.sh` is macOS/Linux only. Add its folder to PATH.
- **Voice:** ElevenLabs, model Eleven v3, for Malayalam with English words mixed in. The free on-device Kokoro voice can't speak Malayalam.
