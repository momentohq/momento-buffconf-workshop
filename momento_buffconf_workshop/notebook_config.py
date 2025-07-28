# workshop_utils/notebook_config.py
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, cast

from dotenv import load_dotenv

DEFAULT_SNAPSHOT_TIMESTAMP = "2025-07-25-14-48-36"
"""Default timestamp for cached data files."""
ENV_SNAPSHOT_TIMESTAMP_KEY = "WORKSHOP_SNAPSHOT_TIMESTAMP"
"""Environment variable key for the snapshot timestamp."""
ENV_OPENAI_API_KEY = "OPENAI_API_KEY"
"""Environment variable key for the OpenAI API key."""
ENV_TURBOPUFFER_API_KEY = "TURBOPUFFER_API_KEY"
"""Environment variable key for the Turbopuffer API key."""
ENV_TURBOPUFFER_NAMESPACE_KEY = "TURBOPUFFER_NAMESPACE"
"""Environment variable key for the Turbopuffer namespace."""
ENV_TURBOPUFFER_REGION_KEY = "TURBOPUFFER_REGION"
"""Environment variable key for the Turbopuffer region."""
ENV_MOMENTO_API_KEY = "MOMENTO_API_KEY"
"""Environment variable key for the Momento API key."""

DEFAULT_TURBOPUFFER_REGION = "gcp-us-central1"
"""Default region for Turbopuffer if not specified."""

load_dotenv()


@dataclass
class AssetDirectories:
    """Directories to initialize for the workshop."""

    content_data_directory: Path
    raw_article_directory: Path
    normalized_article_directory: Path
    embeddings_directory: Path
    wasm_directory: Path


@dataclass
class NotebookConfiguration:
    """Configuration for a notebook stage in the workshop."""

    notebook_name: str
    """Name of the notebook stage (e.g., '02-data-scraping')."""
    run_demos_live: bool
    """Whether to run the demos live or use cached data."""
    snapshot_timestamp: str
    """Timestamp for the snapshot to use (if not using live data)."""

    content_data_directory: Path
    """Directory for all content data files."""
    raw_article_directory: Path
    """Directory for raw article files."""
    normalized_article_directory: Path
    """Directory for normalized article files."""
    embeddings_directory: Path
    """Directory for embeddings files."""
    wasm_directory: Path
    """Directory for WASM files used in the workshop."""

    # file paths (always defined by _make_base)
    raw_article_path: Path
    """Path to the raw article file."""
    normalized_article_path: Path
    """Path to the normalized article file."""
    embeddings_path: Path
    """Path to the embeddings file."""
    index_articles_function_wasm_path: Path
    """Path to the Turbopuffer index function WASM file."""
    recommend_articles_function_wasm_path: Path
    """Path to the Turbopuffer recommend function WASM file."""

    _turbopuffer_api_key: Optional[str] = None
    """API key for Turbopuffer, if required."""
    _turbopuffer_namespace: Optional[str] = None
    """Namespace for Turbopuffer, if required."""
    _turbopuffer_region: Optional[str] = None
    """Region for Turbopuffer, if required."""

    required_files: tuple[Path, ...] = field(default_factory=lambda: ())
    """Paths to all required files for this notebook stage."""
    required_environment_variables: tuple[str, ...] = field(default_factory=lambda: ())
    """Environment variables required for this notebook stage."""

    momento_cache_name: str = "my-functions-cache"
    """Cache name for Momento functions, defaulting to 'my-functions-cache' for the workshop."""

    def __post_init__(self) -> None:
        """Post-initialization to set up Turbopuffer configuration."""
        self._turbopuffer_api_key = os.getenv(ENV_TURBOPUFFER_API_KEY)
        self._turbopuffer_namespace = os.getenv(ENV_TURBOPUFFER_NAMESPACE_KEY)
        self._turbopuffer_region = os.getenv(
            ENV_TURBOPUFFER_REGION_KEY, DEFAULT_TURBOPUFFER_REGION
        )

    @property
    def turbopuffer_api_key(self) -> str:
        if not self._turbopuffer_api_key:
            raise ValueError(
                "❌ TURBOPUFFER_API_KEY is missing. "
                "Set it in the environment or your '.env' file."
            )
        return self._turbopuffer_api_key

    @property
    def turbopuffer_namespace(self) -> str:
        if not self._turbopuffer_namespace:
            raise ValueError(
                "❌ TURBOPUFFER_NAMESPACE is missing. "
                "Set it in the environment or pass explicit_namespace=..."
            )
        return self._turbopuffer_namespace

    @property
    def turbopuffer_region(self) -> str:
        if not self._turbopuffer_region:
            return DEFAULT_TURBOPUFFER_REGION
        return self._turbopuffer_region

    def validate_requirements(self) -> None:
        self.__validate_required_files_exist()
        self.__validate_required_environment_variables_exist()

    def __validate_required_files_exist(self) -> None:
        """Raise a helpful error if any expected cached file is missing."""
        missing_files: list[str] = [
            str(file_path)
            for file_path in self.required_files
            if not file_path.exists()
        ]

        if missing_files:
            joined = "\n".join(missing_files)
            raise FileNotFoundError(
                f"🔴 The following required file(s) are missing:\n{joined}\n"
                "Run the prerequisite notebook with `run_demos_live=True`, "
                "or copy the cached files into place."
            )

    def __validate_required_environment_variables_exist(self) -> None:
        """Ensure all env vars we need for this stage are set."""
        missing_vars = [
            key for key in self.required_environment_variables if key not in os.environ
        ]
        if missing_vars:
            joined = ", ".join(missing_vars)
            raise EnvironmentError(
                f"🔴 Missing required environment variable(s): {joined}\n"
                "Create a '.env' file or export them in your shell, then restart the notebook.\n"
                "Example .env template:\n"
                "OPENAI_API_KEY=sk-...\n"
                "TURBOPUFFER_API_KEY=tp-...\n"
            )

    @staticmethod
    def _infer_latest_snapshot() -> str | None:
        """Return newest timestamp based on filenames or None if none exist."""
        asset_directories = NotebookConfiguration._initialize_directories()
        matches = sorted(
            asset_directories.normalized_article_directory.glob(
                "cbssports-articles-*.json"
            )
        )
        if not matches:
            return None
        # filenames sort lexicographically == chrono with yyyy-mm-dd-hh-mm-ss
        return matches[-1].stem.replace("cbssports-articles-", "")

    @classmethod
    def _choose_snapshot_timestamp(
        cls,
        *,
        explicit: str | None,
        is_producer_live: bool,
        allow_infer_latest: bool,
    ) -> str:
        """
        Return a snapshot timestamp following priority:
        1. explicit arg (if provided)
        2. environment variable (if set)
        3. is producer live? (if so, use current time)
        4. latest snapshot on disk   (if allowed and available)
        """
        if explicit:
            return explicit

        if ENV_SNAPSHOT_TIMESTAMP_KEY in os.environ:
            return os.environ[ENV_SNAPSHOT_TIMESTAMP_KEY]

        if is_producer_live:
            return time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())

        latest = cls._infer_latest_snapshot() if allow_infer_latest else None
        if latest:
            return latest

        # ---- final fallback ----
        print(
            f"🛈 No snapshot found; falling back to bundled demo "
            f"{DEFAULT_SNAPSHOT_TIMESTAMP}"
        )
        return DEFAULT_SNAPSHOT_TIMESTAMP

    @classmethod
    def _initialize_directories(cls) -> AssetDirectories:
        content_data_directory = Path("../data/content")
        raw_article_directory = content_data_directory / "raw"
        normalized_article_directory = content_data_directory / "normalized"
        embeddings_directory = Path("../data/embeddings")
        wasm_directory = Path("../data/wasm")

        for directory in (
            content_data_directory,
            raw_article_directory,
            normalized_article_directory,
            embeddings_directory,
            wasm_directory,
        ):
            directory.mkdir(parents=True, exist_ok=True)

        return AssetDirectories(
            content_data_directory=content_data_directory,
            raw_article_directory=raw_article_directory,
            normalized_article_directory=normalized_article_directory,
            embeddings_directory=embeddings_directory,
            wasm_directory=wasm_directory,
        )

    @classmethod
    def _make_base(
        cls,
        *,
        notebook_name: str,
        snapshot_timestamp: str,
        run_demos_live: bool = False,
    ) -> "NotebookConfiguration":
        """Base configuration for all notebooks."""
        asset_directories = cls._initialize_directories()

        filename = f"cbssports-articles-{snapshot_timestamp}.json"

        raw_article_path = asset_directories.raw_article_directory / filename
        normalized_article_path = (
            asset_directories.normalized_article_directory / filename
        )
        embeddings_path = (
            asset_directories.embeddings_directory
            / f"{normalized_article_path.stem}.parquet"
        )
        index_articles_function_wasm_path = (
            asset_directories.wasm_directory / "turbopuffer_index_articles.wasm"
        )
        recommend_articles_function_wasm_path = (
            asset_directories.wasm_directory / "turbopuffer_recommend_articles.wasm"
        )

        return cls(
            notebook_name=notebook_name,
            run_demos_live=run_demos_live,
            snapshot_timestamp=snapshot_timestamp,
            content_data_directory=asset_directories.content_data_directory,
            raw_article_directory=asset_directories.raw_article_directory,
            normalized_article_directory=asset_directories.normalized_article_directory,
            embeddings_directory=asset_directories.embeddings_directory,
            wasm_directory=asset_directories.wasm_directory,
            raw_article_path=raw_article_path,
            normalized_article_path=normalized_article_path,
            embeddings_path=embeddings_path,
            index_articles_function_wasm_path=index_articles_function_wasm_path,
            recommend_articles_function_wasm_path=recommend_articles_function_wasm_path,
        )

    @classmethod
    def for_scraping(
        cls, *, run_demos_live: bool = False, snapshot_timestamp: str | None = None
    ) -> "NotebookConfiguration":
        """Configuration for *02-data-scraping* notebook."""
        snapshot_timestamp = cls._choose_snapshot_timestamp(
            explicit=snapshot_timestamp,
            is_producer_live=run_demos_live,
            allow_infer_latest=not run_demos_live,
        )

        config = cls._make_base(
            notebook_name="02-data-scraping",
            run_demos_live=run_demos_live,
            snapshot_timestamp=snapshot_timestamp,
        )

        required_files: list[Path] = []
        if not run_demos_live:
            required_files.extend(
                [config.raw_article_path, config.normalized_article_path]
            )

        config.required_files = tuple(required_files)
        config.validate_requirements()
        return config

    @classmethod
    def for_embedding(
        cls, *, run_demos_live: bool = False, snapshot_timestamp: str | None = None
    ) -> "NotebookConfiguration":
        """Configuration for *03-embed-content* notebook."""
        snapshot_timestamp = cls._choose_snapshot_timestamp(
            explicit=snapshot_timestamp,
            is_producer_live=False,
            allow_infer_latest=True,
        )

        config = cls._make_base(
            notebook_name="03-embed-content",
            run_demos_live=run_demos_live,
            snapshot_timestamp=snapshot_timestamp,
        )

        required_files = [config.normalized_article_path]
        required_environment_variables = []
        if run_demos_live:
            required_environment_variables.append(ENV_OPENAI_API_KEY)
        else:
            required_files.append(config.embeddings_path)
        config.required_files = tuple(required_files)
        config.required_environment_variables = tuple(required_environment_variables)
        config.validate_requirements()
        return config

    @classmethod
    def for_indexing(
        cls, *, snapshot_timestamp: Optional[str] = None
    ) -> "NotebookConfiguration":
        """Configuration for *04-index-content* notebook."""
        snapshot_timestamp = cls._choose_snapshot_timestamp(
            explicit=snapshot_timestamp,
            is_producer_live=False,
            allow_infer_latest=True,
        )

        config = cls._make_base(
            notebook_name="04-index-content",
            run_demos_live=True,
            snapshot_timestamp=snapshot_timestamp,
        )
        config.required_files = (
            config.normalized_article_path,
            config.embeddings_path,
        )
        config.required_environment_variables = (
            ENV_TURBOPUFFER_API_KEY,
            ENV_TURBOPUFFER_NAMESPACE_KEY,
            ENV_TURBOPUFFER_REGION_KEY,
        )
        config.validate_requirements()
        return config

    @classmethod
    def for_querying(
        cls, *, snapshot_timestamp: Optional[str] = None
    ) -> "NotebookConfiguration":
        """Configuration for *05-query-and-recommend-content* notebook."""
        snapshot_timestamp = cls._choose_snapshot_timestamp(
            explicit=snapshot_timestamp,
            is_producer_live=False,
            allow_infer_latest=True,
        )

        config = cls._make_base(
            notebook_name="05-query-and-recommend-content",
            run_demos_live=True,
            snapshot_timestamp=snapshot_timestamp,
        )

        # The notebook is not runnable without these.
        config.required_files = (
            config.normalized_article_path,
            config.embeddings_path,
        )
        config.required_environment_variables = (
            ENV_OPENAI_API_KEY,
            ENV_TURBOPUFFER_API_KEY,
            ENV_TURBOPUFFER_NAMESPACE_KEY,
            ENV_TURBOPUFFER_REGION_KEY,
        )
        config.validate_requirements()

        return config

    @classmethod
    def for_functions(
        cls, *, snapshot_timestamp: Optional[str] = None
    ) -> "NotebookConfiguration":
        """Configuration for *06-functions* notebook."""
        snapshot_timestamp = cls._choose_snapshot_timestamp(
            explicit=snapshot_timestamp,
            is_producer_live=False,
            allow_infer_latest=True,
        )

        config = cls._make_base(
            notebook_name="06-deploy-with-momento-functions",
            run_demos_live=True,
            snapshot_timestamp=snapshot_timestamp,
        )

        # The notebook is not runnable without these.
        config.required_files = (
            config.normalized_article_path,
            config.index_articles_function_wasm_path,
            config.recommend_articles_function_wasm_path,
        )
        config.required_environment_variables = (
            ENV_OPENAI_API_KEY,
            ENV_TURBOPUFFER_API_KEY,
            ENV_TURBOPUFFER_NAMESPACE_KEY,
            ENV_TURBOPUFFER_REGION_KEY,
            ENV_MOMENTO_API_KEY,
        )
        config.validate_requirements()

        return cast(NotebookConfiguration, config)

    def print_status_banner(self) -> None:
        """Terminal-style banner announcing whether we’re live or cached."""
        snapshot_origin = (
            "explicit" if ENV_SNAPSHOT_TIMESTAMP_KEY in os.environ else "auto"
        )
        snapshot_string = f"📦 snapshot {self.snapshot_timestamp} ({snapshot_origin})"

        if self.run_demos_live:
            print(
                f"🟢 LIVE DEMO — {self.notebook_name} will generate fresh outputs "
                f"({snapshot_string})"
            )
        else:
            print(
                f"🟡 USING CACHED DATA — {self.notebook_name} relies on cached data "
                f"({snapshot_string})"
            )
