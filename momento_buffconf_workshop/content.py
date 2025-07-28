from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from langchain_core.documents import Document
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ArticleContent(BaseModel):
    articles: dict[str, list[Document]] = Field(
        ..., description="A dictionary of articles categorized by their type."
    )

    @property
    def all_articles(self) -> list[Document]:
        """
        Get all articles from the dictionary.
        """
        # exclude duplicates by article.id
        seen = set()
        all_docs = []
        for docs in self.articles.values():
            for doc in docs:
                if doc.id not in seen:
                    seen.add(doc.id)
                    all_docs.append(doc)
        return all_docs

    def create_index_with_embeddings(self, embeddings_df: pd.DataFrame) -> ArticleIndex:
        """
        Create an index of articles with their embeddings.
        """
        return ArticleIndex(self, embeddings_df)

    def save_json(self, fp: str | Path) -> None:
        """
        Save the articles to a JSON file.
        """
        with open(fp, "w") as f:
            json.dump(self.model_dump(), f, default=str, indent=2)

    @staticmethod
    def load_json(fp: str | Path) -> ArticleContent:
        """
        Load the articles from a JSON file.
        """
        with open(fp, "r") as f:
            data = json.load(f)
            return ArticleContent.model_validate(data)  # type: ignore[call-arg]


class ArticleIndex:
    """A simple index to map article IDs and links to articles."""

    def __init__(self, articles: ArticleContent, embeddings_df: pd.DataFrame):
        self.articles = articles
        self.embeddings_df = embeddings_df
        self.article_index = {article.id: article for article in articles.all_articles}
        self.link_index = {
            article.metadata.get("link"): article.id
            for article in articles.all_articles
        }

    def get_embedding(self, article_id: str) -> Optional[np.ndarray]:
        """Get the embedding for an article by its ID."""
        if article_id in self.embeddings_df.index:
            return np.array(self.embeddings_df.loc[article_id].embedding.tolist())
        return None

    def find_article_by_id(self, article_id: str) -> Optional[Document]:
        """Find an article by its ID."""
        return self.article_index.get(article_id, None)

    def find_article_by_link(self, link: str) -> Optional[Document]:
        """Find an article by its link."""
        article_id = self.link_index.get(link, None)
        if article_id:
            return self.article_index.get(article_id, None)
        return None

    def __len__(self) -> int:
        """Return the number of articles in the index."""
        return len(self.articles.all_articles)

    def __repr__(self):
        return f"ArticleIndex with {len(self.articles.all_articles)} articles and {len(self.embeddings_df)} embeddings."
