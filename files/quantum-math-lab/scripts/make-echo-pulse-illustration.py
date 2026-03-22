from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap


def main():
    repo_root = Path(__file__).resolve().parents[3]
    summary_path = (
        repo_root
        / "files"
        / "quantum-math-lab"
        / "results"
        / "hardware"
        / "summary"
        / "echo_pulse_popular_illustration_2026-03-22.png"
    )
    paper_path = repo_root / "paper" / "figure_echo_pulse_popular.png"

    x = np.linspace(0.0, 79.0, 260)
    y = np.linspace(0.0, 1.0, 220)
    X, Y = np.meshgrid(x, y)

    front_progress = np.clip((Y - 0.12) / 0.72, 0.0, 1.0)
    front_gate = np.clip((Y - 0.08) / 0.14, 0.0, 1.0)
    main_center = 12.0 + 34.0 * front_progress
    main_width = 8.2 + 12.5 * front_progress
    main_amp = 0.50 - 0.12 * front_progress
    main_front = (
        main_amp
        * front_gate
        * np.exp(-((X - main_center) ** 2) / (2.0 * main_width**2))
    )

    source_peak = 1.02 * np.exp(-((X - 4.3) ** 2) / (2.0 * 0.95**2)) * np.exp(
        -((Y - 0.055) ** 2) / (2.0 * 0.038**2)
    )

    trail_center = main_center - (6.0 + 7.0 * front_progress)
    trail_width = 7.0 + 11.0 * front_progress
    trail_amp = 0.06 * (1.0 - 0.25 * front_progress)
    trail = trail_amp * np.exp(-((X - trail_center) ** 2) / (2.0 * trail_width**2))

    echo_progress = np.clip((Y - 0.72) / 0.28, 0.0, 1.0)
    echo_center = 58.0 + 10.0 * echo_progress
    echo_width = 4.4 + 3.0 * echo_progress
    echo_amp = 0.20 * np.exp(-0.15 * echo_progress)
    echo = (
        echo_amp
        * np.exp(-((X - echo_center) ** 2) / (2.0 * echo_width**2))
        * np.exp(-((Y - 0.84) ** 2) / (2.0 * 0.09**2))
    )

    floor = 0.012 * np.exp(-2.1 * Y)
    Z = np.clip(main_front + source_peak + trail + echo + floor, 0.0, None)

    cmap = LinearSegmentedColormap.from_list(
        "echo_pulse",
        ["#061019", "#0f4365", "#1c8f9d", "#f0a644", "#fff1c2"],
        N=256,
    )

    fig = plt.figure(figsize=(12.5, 7.4), facecolor="#071017")
    ax = fig.add_subplot(111, projection="3d", facecolor="#071017")

    surface = ax.plot_surface(
        X,
        Y,
        Z,
        cmap=cmap,
        linewidth=0,
        antialiased=True,
        alpha=0.97,
        rcount=220,
        ccount=260,
    )
    ax.contourf(X, Y, Z, zdir="z", offset=0.0, levels=18, cmap=cmap, alpha=0.82)

    echo_peak_index = np.unravel_index(np.argmax(echo), echo.shape)
    echo_peak_x = float(X[echo_peak_index])
    echo_peak_y = float(Y[echo_peak_index])
    echo_peak_z = float(Z[echo_peak_index])
    ax.plot(
        [echo_peak_x, echo_peak_x],
        [echo_peak_y, echo_peak_y],
        [0.0, echo_peak_z],
        linestyle="--",
        linewidth=2.0,
        color="#8fe7dd",
        alpha=0.95,
    )
    ax.scatter(
        [echo_peak_x],
        [echo_peak_y],
        [echo_peak_z],
        s=120,
        color="#8fe7dd",
        edgecolors="#f5f3e8",
        linewidths=1.2,
        depthshade=False,
    )

    ax.view_init(elev=25, azim=-122)
    ax.set_xlim(0.0, 79.0)
    ax.set_ylim(0.0, 1.0)
    ax.set_zlim(0.0, float(Z.max()) * 1.08)

    ax.set_xlabel("qubit position", color="#d8ebf3", labelpad=12)
    ax.set_ylabel("echo depth / time", color="#d8ebf3", labelpad=12)
    ax.set_zlabel("relative response", color="#d8ebf3", labelpad=10)
    ax.tick_params(colors="#cfe4ec")
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.set_facecolor((0.05, 0.10, 0.14, 0.80))
        axis.pane.set_edgecolor((0.45, 0.56, 0.63, 0.35))
        axis.line.set_color("#7fa3b1")

    colorbar = fig.colorbar(surface, shrink=0.72, pad=0.08)
    colorbar.set_label("illustrative echo intensity", color="#d8ebf3")
    colorbar.ax.yaxis.set_tick_params(color="#d8ebf3")
    plt.setp(colorbar.ax.get_yticklabels(), color="#d8ebf3")

    fig.suptitle(
        "Illustrative scrambling front with residual echo",
        color="#f5f3e8",
        fontsize=18,
        fontweight="bold",
        y=0.96,
    )
    fig.text(
        0.06,
        0.90,
        "Popular illustration only; not fitted to measured data.",
        color="#d8ebf3",
        fontsize=10,
    )
    fig.text(0.11, 0.74, "local perturbation", color="#fff1c2", fontsize=12, weight="bold")
    fig.text(
        0.33,
        0.16,
        "broader, lower scrambling front",
        color="#f0c376",
        fontsize=12,
        weight="bold",
    )
    fig.text(0.71, 0.69, "smaller late residual echo", color="#8fe7dd", fontsize=12, weight="bold")
    fig.text(0.77, 0.63, "marked here", color="#8fe7dd", fontsize=10)

    fig.tight_layout()
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    paper_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(summary_path, dpi=220, facecolor=fig.get_facecolor(), bbox_inches="tight")
    fig.savefig(paper_path, dpi=220, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)

    print(summary_path)
    print(paper_path)


if __name__ == "__main__":
    main()
