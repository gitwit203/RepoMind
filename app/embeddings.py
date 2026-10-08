from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid

MODEL_NAME = "all-MiniLM-L6-v2"  # small, fast, good enough for code+text
COLLECTION_NAME = "repo_chunks"

_model = None
_client = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def get_client():
    global _client
    if _client is None:
        _client = QdrantClient(":memory:")
    return _client


def index_chunks(chunks: list):
    """Embeds all chunks and stores them in Qdrant. Returns nothing."""
    model = get_model()
    client = get_client()

    # recreate collection fresh each time you index a new repo
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
    )

    texts = [chunk["code"] for chunk in chunks]
    vectors = model.encode(texts, show_progress_bar=False)

    points = []
    for chunk, vector in zip(chunks, vectors):
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=vector.tolist(),
            payload=chunk,  # store name, type, file_path, code, lines — all of it
        ))

    client.upsert(collection_name=COLLECTION_NAME, points=points)


def search_chunks(query: str, top_k: int = 5):
    """Embeds the query and returns the top_k most similar chunks."""
    model = get_model()
    client = get_client()

    query_vector = model.encode(query).tolist()
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k,
    )

    return [hit.payload for hit in results]