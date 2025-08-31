from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
import os
from glob import glob

class VectoRead:
    def __init__(self, 
                 pinecone_api_key: str, 
                 index_name: str, 
                 pinecone_region: str = "us-east-1",
                 folder_path: str = None,
                 model_name: str = "all-MiniLM-L6-v2",
                 chunk_size: int = 500):
        """
        Initialize VectoRead
        """
        self.pc = Pinecone(api_key=pinecone_api_key)
        self.index_name = index_name
        self.region = pinecone_region
        self.folder_path = folder_path
        self.model = SentenceTransformer(model_name)
        self.chunk_size = chunk_size
        
        # Create index if not exists
        if index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=index_name,
                dimension=self.model.get_sentence_embedding_dimension(),
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=self.region
                )
            )
            print("✅ Index created:", index_name)
        else:
            print("✅ Using existing index:", index_name)
            
        self.index = self.pc.Index(index_name)

    def _read_files(self):
        """
        Read all TXT files from the folder and return a list of their content
        """
        if not self.folder_path:
            raise ValueError("Folder path not provided.")
            
        txt_files = glob(os.path.join(self.folder_path, "*.txt"))
        all_texts = []
        for file in txt_files:
            with open(file, "r", encoding="utf-8") as f:
                all_texts.append(f.read())
        return all_texts

    def _split_text(self, text):
        """
        Split text into chunks
        """
        chunks = []
        for i in range(0, len(text), self.chunk_size):
            chunks.append(text[i:i+self.chunk_size])
        return chunks

    def upsert_folder_to_vectordb(self, email: str):
        """
        Read folder, split into chunks, generate embeddings and upsert into Pinecone
        """
        all_texts = self._read_files()
        upsert_data = []

        for text in all_texts:
            chunks = self._split_text(text)
            for i, chunk in enumerate(chunks):
                embedding = self.model.encode([chunk])[0].tolist()
                upsert_data.append({
                    "id": f"{email}_{i}",
                    "values": embedding,
                    "metadata": {
                        "email": email,
                        "chunk_index": i,
                        "chunk_text": chunk
                    }
                })

        # Upsert all data
        self.index.upsert(vectors=upsert_data)
        print(f"✅ Upserted {len(upsert_data)} chunks to Pinecone.")

    def get_relevant_chunks(self, query: str, email: str, top_k: int = 12):
        """
        Retrieve top_k relevant chunks for the given query and email
        """
        query_embedding = self.model.encode(query).tolist()
        result = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter={"email": {"$eq": email}}
        )
        matches = result.get("matches", [])
        return [match["metadata"]["chunk_text"] for match in matches] if matches else []

