from dataclasses import dataclass

import pandas as pd
from langchain_core.documents import Document
from plotly import express as px  # type: ignore
from sklearn.manifold import TSNE  # type: ignore


@dataclass
class ArticleEmbeddingProjector:
    projection_df: pd.DataFrame

    def plot(self, show_feeds: bool = False) -> None:
        scatter_kwargs = {
            "x": "x",
            "y": "y",
            "hover_name": "title",
            "custom_data": ["url"],
            "title": "t-SNE projection of article embeddings",
        }
        if show_feeds:
            scatter_kwargs["color"] = "feed"
        fig = px.scatter(self.projection_df, **scatter_kwargs)

        fig.update_traces(
            marker=dict(size=10, opacity=0.8),
            # HTML anchor tag makes the link clickable
            hovertemplate=(
                "<b>%{hovertext}</b><br>"
                "<a href='%{customdata[0]}' target='_blank'>open article ↗</a>"
                "<extra></extra>"
            ),
        )

        fig.show()

    @staticmethod
    def fit_transform(
        embeddings_df: pd.DataFrame, all_articles: list[Document]
    ) -> "ArticleEmbeddingProjector":
        embeddings_matrix = embeddings_df.to_numpy()
        tsne = TSNE(
            n_components=2,
            perplexity=8,
            init="random",
            learning_rate="auto",
            random_state=42,
        )
        projection_2d = tsne.fit_transform(embeddings_matrix)

        points_df = pd.DataFrame(projection_2d, columns=["x", "y"])
        points_df["id"] = embeddings_df.index
        points_df["title"] = [
            article.metadata.get("title", "") for article in all_articles
        ]
        points_df["url"] = [article.metadata.get("url", "") for article in all_articles]
        points_df["feed"] = [
            article.metadata.get("feed", "/").split("/")[-1] for article in all_articles
        ]
        return ArticleEmbeddingProjector(points_df)
