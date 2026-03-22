import matplotlib.pyplot as plt
import numpy as np

x = np.array([14.0, 14.8, 20, 24, 32, 80])
y = np.array([3.0, 2.15, 1.15, 1.15, 1.15, 1.15])

labels = [
    "q14 exact\nfixed-observable benchmark",
    "q14 hardware\ncheckpoint + ZNE",
    "q20\nseeded subset controls",
    "q24\nscale-up",
    "q32\npilot",
    "q80\nfirst subset pilot",
]

colors = ["#1F4E5F", "#3C7A89", "#8C5A2B", "#A66A35", "#C17D3C", "#A64B2A"]
sizes = [220, 190, 160, 160, 170, 240]

fig, ax = plt.subplots(figsize=(13, 8), dpi=160)
fig.patch.set_facecolor("#F7F4EE")
ax.set_facecolor("#F7F4EE")

ax.axhspan(2.6, 3.3, color="#DCEBED", alpha=0.85)
ax.axhspan(1.6, 2.5, color="#E8E1D3", alpha=0.85)
ax.axhspan(0.7, 1.5, color="#F1E6D8", alpha=0.9)

for yy in [1.5, 2.5]:
    ax.axhline(yy, color="#C9C1B5", lw=1.2, ls="--", zorder=0)

ax.plot(x, y, color="#5A574F", lw=2.2, alpha=0.8, zorder=1)

for xi, yi, c, s in zip(x, y, colors, sizes):
    ax.scatter(xi, yi, s=s, color=c, edgecolor="white", linewidth=1.8, zorder=3)

offsets = {
    0: (0.3, 0.10),
    1: (0.3, -0.18),
    2: (0.2, 0.10),
    3: (0.2, -0.18),
    4: (0.2, 0.10),
    5: (-6.5, 0.10),
}

for i, (xi, yi, txt) in enumerate(zip(x, y, labels)):
    dx, dy = offsets[i]
    ax.text(xi + dx, yi + dy, txt, fontsize=11, color="#1F1F1B", ha="left", va="center")

ax.text(82, 2.95, "True fixed-observable OLE", ha="right", va="center", fontsize=12, color="#1F1F1B", fontweight="bold")
ax.text(82, 2.05, "OLE-compatible hardware checkpoint", ha="right", va="center", fontsize=12, color="#1F1F1B", fontweight="bold")
ax.text(82, 1.10, "Subset-proxy locality evidence", ha="right", va="center", fontsize=12, color="#1F1F1B", fontweight="bold")

callout = (
    "Interpretation\n\n"
    "Right = larger system\n"
    "Higher = closer to formal OLE\n"
    "q80 = first large-scale hardware step,\n"
    "not full-q80 OLE closure"
)
ax.text(
    52, 2.85, callout, fontsize=11, color="#1F1F1B", ha="left", va="top",
    bbox=dict(boxstyle="round,pad=0.5", facecolor="#EFE8DB", edgecolor="#D1C7B6"),
)

ax.annotate("", xy=(80, 0.82), xytext=(14, 0.82), arrowprops=dict(arrowstyle="->", lw=2, color="#5A574F"))
ax.text(47, 0.74, "increasing hardware scale", ha="center", va="top", fontsize=11, color="#5A574F")

ax.set_xlim(10, 85)
ax.set_ylim(0.65, 3.25)
ax.set_xticks([14, 20, 24, 32, 80])
ax.set_xlabel("System size (qubits)", fontsize=14, color="#1F1F1B")
ax.set_yticks([1.1, 2.05, 2.95])
ax.set_yticklabels(["Subset-proxy", "Hardware checkpoint", "True OLE"], fontsize=12)
ax.tick_params(axis="x", labelsize=12, colors="#1F1F1B")
ax.tick_params(axis="y", colors="#1F1F1B")

for spine in ax.spines.values():
    spine.set_color("#B8B2A7")
    spine.set_linewidth(1.1)

ax.set_title("From q14 exact OLE to a first q80 hardware step", fontsize=22, color="#1F1F1B", pad=18)
ax.text(
    0.5, 1.01,
    "Conceptual trajectory: increasing scale, but not the same estimator class",
    transform=ax.transAxes, ha="center", va="bottom", fontsize=13, color="#5A574F",
)

fig.text(0.07, 0.035, "Conceptual map only: the y-axis is qualitative, not a measured quantity.", fontsize=10.5, color="#5A574F")

plt.tight_layout(rect=[0.03, 0.06, 0.98, 0.95])
out = "/mnt/c/Users/Lenna/SynologyDrive/qlab/onderzoek_blackhole_echo_status_2026-03-05_131816/files/q14_to_q80_trajectory_map.png"
plt.savefig(out, facecolor=fig.get_facecolor(), bbox_inches="tight")
print(out)
