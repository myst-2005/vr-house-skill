"""Save the active drawing as DWG and plot model-space extents to an A3 landscape PDF."""
import os
import sys
import time

from pyautocad import Autocad

out_dir = sys.argv[1]
base = sys.argv[2] if len(sys.argv) > 2 else "Kochi-Residence_Option-A_Ground-Floor-Plan"
dwg = os.path.join(out_dir, base + ".dwg")
pdf = os.path.join(out_dir, base + ".pdf")

acad = Autocad(create_if_not_exists=False)
doc = acad.doc

doc.SaveAs(dwg)
print("saved", dwg)

doc.SetVariable("BACKGROUNDPLOT", 0)
lay = doc.ActiveLayout  # Model
lay.ConfigName = "DWG To PDF.pc3"
lay.RefreshPlotDeviceInfo()
media = [m for m in lay.GetCanonicalMediaNames()]
pick = next((m for m in media if m.startswith("ISO_A3_(420.00_x_297.00")), None) \
    or next((m for m in media if "A3" in m and "full_bleed" in m.lower()), None) \
    or next((m for m in media if "A3" in m), None)
print("paper:", pick)
lay.CanonicalMediaName = pick
lay.PaperUnits = 1          # millimetres
lay.PlotType = 1            # acExtents
lay.StandardScale = 0       # acScaleToFit
lay.CenterPlot = True
lay.PlotRotation = 1 if "297.00_x_420.00" in pick else 0   # landscape
acad.app.ZoomExtents()
doc.Regen(1)
try:
    lay.StyleSheet = "monochrome.ctb"
    lay.PlotWithPlotStyles = True
except Exception as e:
    print("plot style not set:", e)

ok = doc.Plot.PlotToFile(pdf)
for _ in range(30):
    if os.path.exists(pdf) and os.path.getsize(pdf) > 0:
        break
    time.sleep(1)
print("plot result:", ok, "| pdf exists:", os.path.exists(pdf),
      "| size:", os.path.getsize(pdf) if os.path.exists(pdf) else 0)
