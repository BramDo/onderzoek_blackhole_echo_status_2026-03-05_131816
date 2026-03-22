import matplotlib.pyplot as plt
import numpy as np

depth = np.array([1, 2])

overlap = np.array([0.00669, 0.06551])
overlap_err = np.array([0.00293, 0.03523])

far_disjoint = np.array([0.99089, 0.95661])
far_disjoint_err = np.array([0.00027, 0.00227])

fig, ax = plt.subplots(figsize=(12, 9), dpi=150)
fig.patch.set_facecolor("#F7F4EE")
ax.set_facecolor("#F7F4EE")

overlap_color = "#A64B2A"
disjoint_color = "#224C63"
text_color = "#1F1F1B"

ax.errorbar(
    depth,
    overlap,
    yerr=overlap_err,
    fmt="o-",
    color=overlap_color,
    linewidth=3,
    markersize=9,
    capsize=4,
    label="Overlap (q=0)",
)

ax.errorbar(
    depth,
    far_disjoint,
    yerr=far_disjoint_err,
    fmt="o-",
    color=disjoint_color,
    linewidth=3,
    markersize=9,
    capsize=4,
    label="Far-disjoint (q=79)",
)

ax.set_title("q80 hardware pilot", fontsize=24, color=text_color, pad=24)
ax.text(
    0.5,
    1.02,
    "Subset S_A = 0..9 | overlap vs far-disjoint control",
    transform=ax.transAxes,
    ha="center",
    va="bottom",
    fontsize=14,
    color=text_color,
)

ax.set_xlabel("Depth", fontsize=15, color=text_color)
ax.set_ylabel("Readout-mitigated subset echo", fontsize=15, color=text_color)

ax.set_xticks([1, 2])
ax.set_xlim(0.85, 2.15)
ax.set_ylim(0, 1.05)

ax.tick_params(axis="both", labelsize=12, colors=text_color)

for spine in ax.spines.values():
    spine.set_color("#B8B2A7")
    spine.set_linewidth(1.2)

ax.grid(axis="y", color="#D9D2C3", linewidth=1, alpha=0.6)
ax.grid(axis="x", visible=False)

ax.legend(frameon=False, fontsize=13, loc="center left", bbox_to_anchor=(1.02, 0.55))

ax.annotate("0.0067", (1, 0.00669), xytext=(8, 10), textcoords="offset points", fontsize=11, color=overlap_color)
ax.annotate("0.0655", (2, 0.06551), xytext=(8, 10), textcoords="offset points", fontsize=11, color=overlap_color)
ax.annotate("0.9909", (1, 0.99089), xytext=(8, -18), textcoords="offset points", fontsize=11, color=disjoint_color)
ax.annotate("0.9566", (2, 0.95661), xytext=(8, -18), textcoords="offset points", fontsize=11, color=disjoint_color)

callout = "Separation preserved at q80\n\nd1: +0.984\nd2: +0.891"
ax.text(
    1.02,
    0.92,
    callout,
    transform=ax.transAxes,
    fontsize=12,
    color=text_color,
    va="top",
    ha="left",
    bbox=dict(boxstyle="round,pad=0.5", facecolor="#EFE8DB", edgecolor="#D1C7B6"),
)

fig.text(
    0.08,
    0.04,
    "First q80 subset-proxy hardware pilot | Claim scope: subset-locality evidence, not full-q80 closure",
    fontsize=11,
    color="#5A574F",
)

plt.tight_layout(rect=[0.04, 0.07, 0.86, 0.95])
out = "/mnt/c/Users/Lenna/SynologyDrive/qlab/onderzoek_blackhole_echo_status_2026-03-05_131816/files/q80_hardware_pilot_linkedin.png"
plt.savefig(out, facecolor=fig.get_facecolor(), bbox_inches="tight")
print(out)
