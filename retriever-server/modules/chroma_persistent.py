from chromadb import PersistentClient
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import re

class ChromaPersistent:
    def __init__(self, persist_directory="./chroma", embedding_model="intfloat/multilingual-e5-large"):
        self.client = PersistentClient(path=persist_directory, settings=Settings(allow_reset=True))
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )
        self.collections = {}

    def get_collection_names(self):
        '''컬렉션 이름 목록 반환'''
        return [col.name for col in self.client.list_collections()]

    def create_collection(self, name: str):
        '''새로운 컬렉션 생성'''
        if not self.validate_collection_name(name):
            raise ValueError(f"[{name}]: 유효하지 않은 컬렉션 이름")
    
        if name in self.get_collection_names():
            print(f"[{name}]: 이미 존재하는 컬렉션")
        else:
            self.collections[name] = self.client.create_collection(
                name=name,
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"[{name}]: 컬렉션 생성 완료")
            
    def delete_all_collections(self):
        '''컬렉션 초기화'''
        try:
            self.client.reset()
            print("모든 컬렉션 삭제 완료")
        except Exception as e:
            print(f"컬렉션 삭제 실패: {str(e)}")

    def validate_collection_name(self, name: str) -> bool:
        '''컬렉션 이름 유효성 검사 (영문, 숫자, 언더스코어)'''
        return bool(re.fullmatch(r"[a-zA-Z0-9_]+", name))
    
    def validate_collection_schema(self, document: dict):
        '''컬렉션 구조 검사'''
        return True

    def connect(self, name: str):
        '''컬렉션 접속'''
        if not self.validate_collection_name(name):
            raise ValueError(f"[{name}]: 유효하지 않은 컬렉션 이름")
        
        if name not in self.get_collection_names():
            print(f"[{name}]: 존재하지 않는 컬렉션")
        else:
            self.collections[name] = self.client.get_collection(name=name)
        return self.collections[name]

    def index(self, collection_name: str, document):
        '''문서 인덱싱 (create)'''
        collection = self.connect(collection_name)

        if isinstance(document, dict):
            document = [document]

        documents = [doc["content"] for doc in document]
        metadatas = [doc["metadata"] for doc in document]
        ids = [f"{collection_name}_{i}" for i in range(len(document))]

        collection.add(documents=documents, metadatas=metadatas, ids=ids)
        print(f"[{collection_name}]: 인덱싱 완료")

    def query(self, collection_name: str, query_text: str, k: int = 3):
        '''질의 (read)'''
        collection = self.connect(collection_name)
        results = collection.query(query_texts=[query_text], n_results=k, include=["documents", "metadatas", "distances"])

        return [
            {
                "metadata": results["metadatas"][0][i],
                "content": results["documents"][0][i],
                "distance": results["distances"][0][i]
            }
            for i in range(len(results["documents"][0]))
        ]
        
    def update(self, keyword: str):
        '''문서 수정 (update)'''
        print("not yet")
        return True
    
    def delete(self, collection_name: str, keyword: str):
        '''문서 삭제 (delete)'''
        print("not yet")
        return True
