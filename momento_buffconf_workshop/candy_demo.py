from dataclasses import dataclass, field

import matplotlib.pyplot as plt  # type: ignore
import pandas as pd
import plotly.express as px  # type: ignore
from ipywidgets import Dropdown, interact  # type: ignore
from sklearn.manifold import TSNE  # type: ignore

from .plot import plot_1d, scatter_2d, scatter_2d_with_df


@dataclass
class CandyDemo1D:
    positions: pd.Series = field(
        default_factory=lambda: pd.Series(
            {
                "Snickers": -2.0,
                "MilkyWay": -1.8,
                "M&M": -1.6,
                "ReesesCups": -1.4,
                "HersheysBar": -1.2,
                "SourPatch": 0.2,
                "Skittles": 0.4,
                "Nerds": 0.6,
                "HotTamales": 0.8,
                "RedVines": 1.0,
                "BigLeagueChew": 1.4,
                "HubbaBubba": 1.6,
                "JollyRancher": 2.0,
                "Jawbreaker": 2.2,
                "TootsiePop": 2.4,
            }
        )
    )

    def plot(self) -> None:
        # Plotting the 1-D candy layout ---------------------------------------------
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.scatter(
            self.positions.values.astype(float), [0] * len(self.positions), s=100
        )

        for name, x in self.positions.items():
            ax.text(x, 0.05, str(name), ha="center", va="bottom", rotation=90)

        ax.set_ylim(-0.1, 0.3)
        ax.set_yticks([])
        ax.set_xlabel("Candy axis (left = chocolate … right = hard)")
        ax.set_title("Kid-style 1-D candy layout")
        ax.spines[["left", "right", "top"]].set_visible(False)

        fig.tight_layout()
        plt.show()


@dataclass
class CandyDemoFeatures:
    features: pd.DataFrame = field(
        default_factory=lambda: pd.DataFrame(
            {
                "name": [
                    "Snickers",
                    "MilkyWay",
                    "M&M",
                    "SourPatch",
                    "Skittles",
                    "JollyRancher",
                    "Jawbreaker",
                    "HotTamales",
                    "RedVines",
                    "BigLeagueChew",
                    "HubbaBubba",
                    "ReesesCups",
                    "HersheysBar",
                    "Nerds",
                    "TootsiePop",
                ],
                "chocolate": [
                    1.0,
                    1.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    1.0,
                    0.0,
                    0.3,
                ],
                "sour": [
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    0.2,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.1,
                    0.0,
                    0.0,
                    0.9,
                    0.3,
                ],
                "hard": [
                    0.2,
                    0.2,
                    0.2,
                    0.3,
                    0.4,
                    1.0,
                    1.0,
                    0.3,
                    0.2,
                    0.1,
                    0.1,
                    0.2,
                    0.1,
                    0.6,
                    0.8,
                ],
                "gum": [
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                ],
                "nutty": [
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                ],
            }
        ).set_index("name")
    )

    def plot_heatmap(self) -> None:
        fig = px.imshow(
            self.features,
            labels=dict(x="Feature", y="Candy", color="Intensity"),
            x=self.features.columns,
            y=self.features.index,
            color_continuous_scale="Blues",
            aspect="auto",
        )
        fig.update_layout(title="Candy Feature Heatmap")
        fig.show()

    def __get_scaled_qualitative(self) -> pd.DataFrame:
        def to_qualitative(x: float) -> str:
            if x < 0.33:
                return "Low"
            elif x < 0.66:
                return "Medium"
            else:
                return "High"

        label_to_score = {"Low": 0, "Medium": 0.5, "High": 1}

        qualitative = self.features.map(to_qualitative)
        scaled = qualitative.apply(lambda col: col.map(label_to_score))
        return scaled

    def plot_qualitative(self) -> None:
        candies_scaled = self.__get_scaled_qualitative()
        fig = px.imshow(
            candies_scaled,
            labels=dict(x="Feature", y="Candy", color="Level"),
            x=candies_scaled.columns,
            y=candies_scaled.index,
            color_continuous_scale="Blues",
            aspect="auto",
        )
        fig.update_layout(title="Candy Feature Levels (Qualitative)")
        fig.show()

    def plot_1d(self, feature: str) -> None:
        return plot_1d(self.features, feature=feature)

    def plot_2d(self, x_axis: str = "chocolate", y_axis: str = "sour") -> None:
        """
        Plot a fixed 2D scatter plot with specified axes.
        """
        scatter_2d(self.features, x_axis=x_axis, y_axis=y_axis)

    def plot_2d_interactive(self) -> None:
        # TODO: this prints 3 plots in Jupyter, not sure why
        interact(
            scatter_2d_with_df(df=self.features),
            x_axis=Dropdown(
                options=self.features.columns, value="chocolate", description="X-axis"
            ),
            y_axis=Dropdown(
                options=self.features.columns, value="sour", description="Y-axis"
            ),
        )

    def plot_projection(self) -> None:
        tsne = TSNE(
            n_components=2,
            perplexity=5,
            init="random",
            learning_rate="auto",
            random_state=42,
        )
        projection = tsne.fit_transform(self.features.to_numpy())

        df = pd.DataFrame(projection, columns=["x", "y"])
        df["name"] = self.features.index

        # Optional: categorize for coloring
        def infer_type(name: str) -> str:
            if name in {"Snickers", "MilkyWay", "M&M", "ReesesCups", "HersheysBar"}:
                return "Chocolate"
            elif name in {"SourPatch", "Skittles", "Nerds"}:
                return "Fruity/Sour"
            elif name in {"Jawbreaker", "JollyRancher", "TootsiePop"}:
                return "Hard"
            elif name in {"BigLeagueChew", "HubbaBubba"}:
                return "Gum"
            elif name == "HotTamales":
                return "Spicy"
            else:
                return "Other"

        df["type"] = df["name"].map(infer_type)

        fig = px.scatter(
            df,
            x="x",
            y="y",
            hover_name="name",
            color="type",
            title="t-SNE Projection of Candy Features",
        )
        fig.update_traces(marker=dict(size=12, opacity=0.8))
        fig.show()
