from __future__ import annotations

from app.core.constants import EMBEDDING_MODEL
from app.core.logger import logger

from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    Service responsible for generating embeddings.
    """

    def __init__(self) -> None:

        logger.info(
            "Loading embedding model: %s",
            EMBEDDING_MODEL,
        )

        self.model = SentenceTransformer(
            EMBEDDING_MODEL,
        )

        logger.info(
            "Embedding model loaded successfully."
        )

    async def get_embedding(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate normalized embedding.
        """

        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        return embedding.tolist()