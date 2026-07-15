from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    Service responsible for generating embeddings.
    """

    def __init__(self):
        self.model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
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
        )

        return embedding.tolist()