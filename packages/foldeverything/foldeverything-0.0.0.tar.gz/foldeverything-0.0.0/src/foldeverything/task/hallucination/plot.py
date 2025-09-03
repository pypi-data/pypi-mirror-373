"""Plotting utilities for protein hallucination results.

This module provides functions for visualizing the results of protein hallucination,
including loss curves, mutation trajectories, and sequence evolution.
"""

import collections
import tempfile
from io import BytesIO, StringIO
from typing import List

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import pandas as pd
import seaborn as sns
import wandb

def plot_distogram_animation(hallucinator):
    plt.figure()
    heatmap_frames = hallucinator.trajectories[-1]["entropy"]   # list/array of 2D arrays

    points_per_frame = None
    if hallucinator.trajectories[-1]["pairs_to_optimize"]:
        points_per_frame = hallucinator.trajectories[-1]["pairs_to_optimize"]

    fig, ax = plt.subplots()

    ax.text(
        0.00,
        1.05,
        "Distogram entropy",
        horizontalalignment="left",
        verticalalignment="bottom",
        transform=ax.transAxes,
        fontsize=12)
    
    protein_text = ax.text(
        0.00,
        1.01,
        "",
        horizontalalignment="left",
        verticalalignment="bottom",
        transform=ax.transAxes,
        fontsize=10)

    ax.text(
        1.15,
        -0.20,
        "Blue circles indicate pair(s) selected for optimization",
        horizontalalignment="right",
        verticalalignment="bottom",
        transform=ax.transAxes,
        fontsize=10)

    # 1) draw the first heatmap without its cbar, grab its QuadMesh
    g = sns.heatmap(heatmap_frames[0], ax=ax, cbar=False)
    mesh = g.collections[0]

    # 2) add one static colorbar
    fig.colorbar(mesh, ax=ax)

    # 3) plot the initial set of circles with a transparent fill
    scatter = None
    if points_per_frame is not None:
        pts0 = np.asarray(points_per_frame[0])  # shape (N,2)
        scatter = ax.scatter(
            pts0[:, 0], pts0[:, 1],
            s=80,                   # circle size
            facecolors='none',      # hollow
            edgecolors='blue',     # outline color
            linewidths=1.5,
            marker='o'
        )

    plt.tight_layout()

    seqs = hallucinator.trajectories[-1]["sequence"]

    seq_text = ax.text(0.5, -0.25, seqs[0], horizontalalignment="center", verticalalignment="bottom", transform=ax.transAxes, fontsize=5, fontfamily="monospace")

    def update(frame):
        # Update title
        params_string_pieces = []
        items = dict(hallucinator.trajectories[-1]["iterator_parameters"][frame])
        protocol = items.pop("protocol")
        for key, value in items.items():
            params_string_pieces.append(f"{key}: {value:.2f}")
        params_string = ", ".join(params_string_pieces)

        seq_text.set_text(seqs[frame])

        if hallucinator.trajectories[-1]["include_target"][frame]:
            protein_text.set_text("Target + Binder")
        else:
            protein_text.set_text("Binder")

        ax.set_title(f"Step {frame} \n{protocol} {params_string}", horizontalalignment="left", fontsize=10, y=1.02)
        # update heatmap data (QuadMesh stores a flat array internally)
        mesh.set_array(heatmap_frames[frame].ravel())
        # update scatter offsets
        if points_per_frame is not None:
            pts = np.asarray(points_per_frame[frame])
            scatter.set_offsets(pts)
        result = [mesh, scatter, seq_text, protein_text]
        return [item for item in result if item is not None]

    anim = FuncAnimation(
        fig, update,
        frames=[index for index in range(len(heatmap_frames)) if heatmap_frames[index] is not None],
        interval=200,   # ms between frames
        blit=True
    )
    return anim

    

def plot_loss(hallucinator: "BinderHallucination") -> plt.Figure:
    """Plot the loss curves for intra and inter contact losses during hallucination.
    
    Args:
        hallucinator: The BinderHallucination instance containing the optimization trajectory
        design_prefix: Prefix for organizing plots by design (e.g., "design_1")
        final_prediction_cif_paths: List of paths to final prediction cif files
    Returns:
        A matplotlib Figure containing the loss plot
    """
    plt.figure()
    intra_contact_loss = hallucinator.trajectories[-1]["intra_contact_loss"]
    inter_contact_loss = hallucinator.trajectories[-1]["inter_contact_loss"]

    if len(intra_contact_loss) == 0 and len(inter_contact_loss) == 0:
        return plt.gcf()

    if len(intra_contact_loss) > 0:
        pd.Series(intra_contact_loss).plot(kind='line', label="Intra-contact")
    if len(inter_contact_loss) > 0:
        pd.Series(inter_contact_loss).plot(kind='line', label="Inter-contact")
    plt.legend(loc="upper left")
    sns.despine()
    plt.title("Loss")
    plt.ylabel("Distogram entropy")
    plt.xlabel("Step")
    plt.ylim(ymin=0)

    # Highlight places where the stage label changes
    for i in range(len(hallucinator.trajectories[-1]["stage"])):
        if hallucinator.trajectories[-1]["stage"][i] != hallucinator.trajectories[-1]["stage"][i-1]:
            plt.axvline(i, color="red")
            # Indicate the stage label. Write the text vertically.
            plt.text(
                i + int(len(hallucinator.trajectories[-1]["intra_contact_loss"]) * 0.05),
                0.2,
                hallucinator.trajectories[-1]["stage"][i],
                color="red",
                fontsize=8,
                verticalalignment="bottom",
                rotation=90
            )
    return plt.gcf()


def plot_mutations(hallucinator: "BinderHallucination") -> plt.Figure:
    """Plot mutation trajectories during hallucination.
    
    Creates two subplots:
    1. Mutations with respect to previous step
    2. Mutations with respect to first step
    
    Args:
        hallucinator: The BinderHallucination instance containing the optimization trajectory
        
    Returns:
        A matplotlib Figure containing the mutation plots
    """
    mutations_with_respect_to_previous = hallucinator.trajectories[-1]["num_mutations"]
    first_seq = hallucinator.trajectories[-1]["sequence"][0]

    mutations_with_respect_to_first = [
        sum(1 for a, b in zip(first_seq, seq) if a.lower() != b.lower())
        for seq in hallucinator.trajectories[-1]["sequence"]
    ]

    plt.figure(figsize=(10, 5))
    
    # Plot mutations with respect to previous step
    plt.subplot(1, 2, 1)
    pd.Series(mutations_with_respect_to_previous).plot(kind='line')
    sns.despine()
    plt.title("Mutations with respect to previous step")
    plt.ylabel("Mutations (count)")
    plt.xlabel("Step")

    # Highlight stage changes
    for i in range(len(hallucinator.trajectories[-1]["stage"])):
        if hallucinator.trajectories[-1]["stage"][i] != hallucinator.trajectories[-1]["stage"][i-1]:
            plt.axvline(i, color="red")
            plt.text(
                i + int(len(hallucinator.trajectories[-1]["intra_contact_loss"]) * 0.05),
                0.2,
                hallucinator.trajectories[-1]["stage"][i],
                color="red",
                fontsize=8,
                verticalalignment="bottom",
                rotation=90
            )

    # Plot mutations with respect to first step
    plt.subplot(1, 2, 2)
    pd.Series(mutations_with_respect_to_first).plot(kind='line')
    sns.despine()
    plt.title(f"Mutations with respect to first step (seq length: {len(first_seq)})")
    plt.ylabel("Mutations (count)")
    plt.xlabel("Step")

    # Highlight stage changes
    for i in range(len(hallucinator.trajectories[-1]["stage"])):
        if hallucinator.trajectories[-1]["stage"][i] != hallucinator.trajectories[-1]["stage"][i-1]:
            plt.axvline(i, color="red")
            plt.text(
                i + int(len(hallucinator.trajectories[-1]["intra_contact_loss"]) * 0.05),
                0.2,
                hallucinator.trajectories[-1]["stage"][i],
                color="red",
                fontsize=8,
                verticalalignment="bottom",
                rotation=90
            )

    plt.tight_layout()
    return plt.gcf()


