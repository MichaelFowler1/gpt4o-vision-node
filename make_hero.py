#!/usr/bin/env python3
"""
Generate docs/hero.png - the README image.

An illustrative view of the Smart Camera Monitor pipeline: a browser webcam
frame is POSTed to the FastAPI backend, GPT-4o (JSON mode) returns the exact
structured schema defined in vision_backend.py (CAMERA_PROMPT), and the UI logs
it + speaks the summary aloud.

NOTE: illustrative - it does not call the OpenAI API (that needs a key and
incurs cost). The response schema and UI styling mirror the real code.

Run:  python make_hero.py     (needs matplotlib)
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, FancyArrowPatch

BG, INK, DIM = "#0b1017", "#e6ebf2", "#8493a6"
ACCENT, ALERT = "#3fa7ff", "#ffb020"

plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": INK})
fig = plt.figure(figsize=(13, 6.6), facecolor=BG)
ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
ax.set_xlim(0, 13); ax.set_ylim(0, 6.6)

fig.text(0.045, 0.90, "SMART CAMERA MONITOR  ·  GPT-4o VISION NODE",
         fontsize=16, fontweight="bold")
fig.text(0.045, 0.845, "webcam  →  GPT-4o vision  →  structured JSON alert + spoken summary",
         fontsize=9.5, color=DIM)

# ---------------- camera view ----------------
cam_x, cam_y, cam_w, cam_h = 0.55, 1.5, 4.2, 3.4
ax.add_patch(FancyBboxPatch((cam_x, cam_y), cam_w, cam_h,
             boxstyle="round,pad=0,rounding_size=0.12", facecolor="#05070c",
             edgecolor="#243247", lw=1.6))
# sky/ground
ax.add_patch(Rectangle((cam_x + 0.12, cam_y + 0.12), cam_w - 0.24, cam_h - 0.24,
             facecolor="#0f1720", edgecolor="none"))
ax.add_patch(Rectangle((cam_x + 0.12, cam_y + 0.12), cam_w - 0.24, 1.0,
             facecolor="#171f2b", edgecolor="none"))
# a car
car_x, car_y = cam_x + 0.9, cam_y + 1.05
ax.add_patch(FancyBboxPatch((car_x, car_y), 1.5, 0.5, boxstyle="round,pad=0,rounding_size=0.08",
             facecolor="#33506f", edgecolor="#5b82ad", lw=1))
ax.add_patch(FancyBboxPatch((car_x + 0.35, car_y + 0.42), 0.8, 0.35,
             boxstyle="round,pad=0,rounding_size=0.06", facecolor="#3d5f83", edgecolor="#5b82ad", lw=1))
ax.add_patch(Circle((car_x + 0.35, car_y), 0.16, facecolor="#11151b", edgecolor="#5b82ad"))
ax.add_patch(Circle((car_x + 1.15, car_y), 0.16, facecolor="#11151b", edgecolor="#5b82ad"))
# a person approaching (highlighted)
px, py = cam_x + 3.05, cam_y + 1.1
ax.add_patch(Circle((px, py + 0.75), 0.16, facecolor="#ffcf6b", edgecolor="none"))
ax.add_patch(FancyBboxPatch((px - 0.13, py), 0.26, 0.62, boxstyle="round,pad=0,rounding_size=0.05",
             facecolor="#ffcf6b", edgecolor="none"))
ax.add_patch(plt.Rectangle((px - 0.32, py - 0.12), 0.64, 1.25, fill=False,
             edgecolor=ALERT, lw=1.6))
ax.text(px, py + 1.28, "person", fontsize=7.5, color=ALERT, ha="center", fontweight="bold")
# LIVE badge + timestamp
ax.add_patch(Circle((cam_x + 0.42, cam_y + cam_h - 0.35), 0.08, facecolor="#ff4d4d"))
ax.text(cam_x + 0.58, cam_y + cam_h - 0.35, "LIVE", fontsize=8, color="#ff4d4d",
        va="center", fontweight="bold")
ax.text(cam_x + cam_w - 0.2, cam_y + cam_h - 0.35, "CAM-01  22:14:07", fontsize=7.5,
        color="#9fb2c9", va="center", ha="right")
ax.text(cam_x, cam_y - 0.35, "browser webcam (getUserMedia → canvas → JPEG)",
        fontsize=8, color=DIM)

# ---------------- arrow to GPT ----------------
ax.add_patch(FancyArrowPatch((cam_x + cam_w + 0.15, cam_y + cam_h / 2),
             (cam_x + cam_w + 1.15, cam_y + cam_h / 2),
             arrowstyle="-|>", mutation_scale=16, color=ACCENT, lw=2))
ax.text(cam_x + cam_w + 0.65, cam_y + cam_h / 2 + 0.35, "gpt-4o\njson_object",
        fontsize=8, color=ACCENT, ha="center", fontweight="bold")

# ---------------- structured JSON output ----------------
jx, jy, jw, jh = 6.7, 3.15, 5.9, 2.85
ax.add_patch(FancyBboxPatch((jx, jy), jw, jh, boxstyle="round,pad=0,rounding_size=0.1",
             facecolor="#0a0f18", edgecolor="#243247", lw=1.4))
ax.text(jx + 0.25, jy + jh - 0.32, "GPT-4o response  (schema from CAMERA_PROMPT)",
        fontsize=9, color=DIM, fontweight="bold")
json_lines = [
    ('{', INK),
    ('  "notable_objects": ["person", "car", "driveway"],', "#9fd0ff"),
    ('  "description": "A person is walking up the', "#cfe6ff"),
    ('       driveway toward the door.",', "#cfe6ff"),
    ('  "alert_needed": true,', "#ff8a8a"),
    ('  "spoken_summary": "Someone is approaching', "#a7e0b8"),
    ('       the front door.",', "#a7e0b8"),
    ('}', INK),
]
yy = jy + jh - 0.68
for txt, col in json_lines:
    ax.text(jx + 0.3, yy, txt, fontsize=8.6, family="monospace", color=col)
    yy -= 0.29

# ---------------- log feed (matches the app UI) ----------------
lx, ly, lw, lh = 6.7, 0.55, 5.9, 2.35
ax.add_patch(FancyBboxPatch((lx, ly), lw, lh, boxstyle="round,pad=0,rounding_size=0.1",
             facecolor="#0a0f18", edgecolor="#243247", lw=1.4))
ax.text(lx + 0.25, ly + lh - 0.3, "on-screen log  +  spoken summary (TTS)",
        fontsize=9, color=DIM, fontweight="bold")
# entry 1 (alert)
e1 = ly + lh - 0.62
ax.text(lx + 0.3, e1, "22:14:07", fontsize=7.5, color=DIM)
ax.add_patch(FancyBboxPatch((lx + 1.35, e1 - 0.08), 0.95, 0.26,
             boxstyle="round,pad=0,rounding_size=0.05", facecolor="#3a2f0a", edgecolor=ALERT, lw=1))
ax.text(lx + 1.82, e1 + 0.05, "⚠ ALERT", fontsize=7.5, color=ALERT, ha="center",
        va="center", fontweight="bold")
ax.text(lx + 0.3, e1 - 0.33, "A person is walking up the driveway toward the door.",
        fontsize=8.4, color=INK)
ax.text(lx + 0.3, e1 - 0.6, "Seen: person, car, driveway", fontsize=7.6, color=DIM)
# divider
ax.plot([lx + 0.3, lx + lw - 0.3], [ly + 0.78, ly + 0.78], color="#1b2740", lw=0.8)
# entry 2 (nominal)
e2 = ly + 0.55
ax.text(lx + 0.3, e2, "22:13:31", fontsize=7.5, color=DIM)
ax.text(lx + 0.3, e2 - 0.27, "Empty driveway, nothing moving.", fontsize=8.4, color=INK)
ax.text(lx + 0.3, e2 - 0.52, "Seen: driveway, hedge", fontsize=7.6, color=DIM)

fig.text(0.045, 0.03, "Illustrative — response schema and UI mirror vision_backend.py; the live app "
                      "calls GPT-4o with your OPENAI_API_KEY. Regenerate: python make_hero.py",
         fontsize=8, color=DIM)

os.makedirs("docs", exist_ok=True)
fig.savefig("docs/hero.png", dpi=140, facecolor=BG)
print("[+] wrote docs/hero.png")
