from sentence_transformers import SentenceTransformer
import os

MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2"
)

model = SentenceTransformer(MODEL_NAME)

def embed(text: str):
    
    return model.encode(text).tolist()
