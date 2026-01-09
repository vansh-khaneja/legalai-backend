from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

class EmbeddingService:
    def __init__(self):
        self.client = OpenAI()

    def get_text_embedding(self, text: str) -> list[float]:
        # Generate an embedding vector for the given text using OpenAI's text-embedding-3-small model.
        response = self.client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding

    def embed(self, texts: list[str]) -> list[list[float]]:
        # Generate embeddings for a list of texts
        embeddings = []
        for text in texts:
            embedding = self.get_text_embedding(text)
            embeddings.append(embedding)
        return embeddings

