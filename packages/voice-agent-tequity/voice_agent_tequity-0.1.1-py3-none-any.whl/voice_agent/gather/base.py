import os
from dotenv import load_dotenv
from voice_agent.gather.vector_read import VectoRead

load_dotenv()

class BaseVectorHandler:
    def __init__(self, train=False, folder_path="./data_folder", email="ravi@example.com"):
        """
        Base class for handling vector DB operations.

        Args:
            train (bool): If True, upserts all TXT files for chunking.
            folder_path (str): Path to the folder containing TXT files.
            email (str): User email to namespace vector entries.
        """
        self.train = train
        self.folder_path = folder_path
        self.email = email

        # Initialize VectoRead instance
        self.vectoread = VectoRead(
            pinecone_api_key=os.getenv("PINECONE_API_KEY"),
            index_name=os.getenv("PINECONE_INDEX_NAME"),
            folder_path=self.folder_path
        )

        if self.train:
            self.train_vector_db()

    def train_vector_db(self):
        """Upsert all files from the folder to the vector DB."""
        print("[INFO] Training vector DB with files from:", self.folder_path)
        self.vectoread.upsert_folder_to_vectordb(email=self.email)
        print("[INFO] Training completed.")

    def query(self, query_text):
        """Fetch relevant chunks from the vector DB."""
        print("[INFO] Querying vector DB for:", query_text)
        chunks = self.vectoread.get_relevant_chunks(query_text, email=self.email)
        return chunks


