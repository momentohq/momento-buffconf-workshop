import math
from typing import Callable

import numpy as np
import pandas as pd
import plotly.express as px  # type: ignore
from IPython.display import clear_output

np.random.seed(42)  # For reproducibility


def plot_1d(df: pd.DataFrame, feature: str, spread=0.08) -> None:
    """
    Number-line scatter where duplicates get small ±y offsets.
    Each candy still keeps its true x-value; y is just cosmetic.
    """
    df = df.copy()
    # --- build deterministic y-offsets for groups with the same x -------------
    groups = df.groupby(feature, sort=False).cumcount()  # index within each x
    sizes = df.groupby(feature)[feature].transform("size")  # group size
    # fan each group symmetrically around 0 :  e.g. n=5 → [-2,-1,0,1,2]/2
    df["y"] = (groups - (sizes - 1) / 2) / (sizes.max()) * spread

    fig = px.scatter(
        df,
        x=feature,
        y="y",
        hover_name=df.index,  # use the index (candy name) for hover
        height=220,
    )
    fig.update_traces(
        marker=dict(size=14, color="#636efa"), hovertemplate="%{hovertext}"
    )
    fig.update_yaxes(visible=False, range=[-spread * 1.2, spread * 1.2])
    fig.update_layout(
        xaxis=dict(title=f"{feature} intensity →", range=[-0.05, 1.05]),
        margin=dict(l=20, r=20, t=20, b=10),
        showlegend=False,
    )
    fig.show()


def scatter_2d_with_df(
    df: pd.DataFrame,
) -> Callable[[str, str], None]:
    def scatter_2d_inner(x_axis: str, y_axis: str) -> None:
        """
        Inner function to handle the actual plotting.
        """
        clear_output(wait=True)  # Clear previous output in Jupyter
        return scatter_2d(df, x_axis, y_axis)

    return scatter_2d_inner


def scatter_2d(df: pd.DataFrame, x_axis: str, y_axis: str, r_base=0.015) -> None:
    """
    2-D scatter with radial jitter for exact duplicates.
    r_base sets jitter radius (~1.5 % of axis span by default).
    """
    df = df[[x_axis, y_axis]].rename(columns={x_axis: "x", y_axis: "y"})
    # ---- assign polar offsets for duplicate (x,y) tuples ---------------------
    df["dup_idx"] = df.groupby(["x", "y"]).cumcount()
    dup_count = df.groupby(["x", "y"])["x"].transform("size")

    # polar coords: equally spaced angles, constant radius
    angles = 2 * math.pi * df["dup_idx"] / dup_count.clip(lower=1)
    df["x_jit"] = df["x"] + r_base * np.cos(angles)
    df["y_jit"] = df["y"] + r_base * np.sin(angles)

    fig = px.scatter(
        df,
        x="x_jit",
        y="y_jit",
        hover_name=df.index,
        height=460,
    )
    fig.update_traces(
        marker=dict(size=16, color="#ef553b"), hovertemplate="%{hovertext}"
    )
    fig.update_layout(
        xaxis=dict(title=x_axis, range=[-0.05, 1.05]),
        yaxis=dict(title=y_axis, range=[-0.05, 1.05]),
        margin=dict(l=20, r=20, t=40, b=10),
        title=f"2-D candy space: {x_axis} × {y_axis}",
        showlegend=False,
    )
    fig.show()
