from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from sentence_transformers import SentenceTransformer
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


class VecStorage:
    def __init__(self, url="localhost", server_port=6333):
        self.client = QdrantClient(url, port=server_port)
        # Загружаем модель для генерации эмбеддингов (BERT-based)
        self.sentence_model = SentenceTransformer(
            "paraphrase-multilingual-mpnet-base-v2"
        )
        self.collection_name = "vec_db_semantic_search"
        # Проверяем, существует ли коллекция
        collections = self.client.get_collections()
        if not (self.collection_name in [col.name for col in collections.collections]):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE),
            )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=100
        )

    def get_best_results(self, query, count=5):
        query_vector = self.sentence_model.encode(query).tolist()

        # Ищем в коллекции
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=count,
        )
        return search_results

    def add_text_file(self, path):
        print("Старт загрузки...")
        with open(path, encoding="utf8") as f:
            text = f.read()
            split_texts = self.text_splitter.split_text(text)
            vectors = self.sentence_model.encode(split_texts).tolist()
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(id=i, vector=vector, payload={"text": split_texts[i]})
                    for i, vector in enumerate(vectors)
                ],
            )
            f.close()
        print("Данные были успешно загружены!")
