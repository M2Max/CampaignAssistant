from langchain_core.tools.retriever import create_retriever_tool
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from pathlib import Path
import os


class CampaignHistory:
    def __init__(self, txt_directory: str = None, persist_directory: str = None):
        self.txt_directory = txt_directory
        self.persist_directory = persist_directory
        self.doc_splits = []
        self.vectorstore = None
        self.retriever = None
        self.retriever_tool = None
        
        if persist_directory is None:
            self.persist_directory = os.path.join(os.path.dirname(__file__), "ChromaDB")

        if txt_directory:
            self.load_documents_from_directory()
    
    def load_documents_from_directory(self):
        docs = []
        txt_files = Path(self.txt_directory).glob("*.txt")
        
        for txt_file in txt_files:
            loader = TextLoader(str(txt_file))
            docs.extend(loader.load())
        
        append = not Path(self.persist_directory).exists()
        self.process_documents(docs, append=append)
    
    def add_documents(self, documents: list[Document]):
        self.process_documents(documents, append=True)
    
    def _build_embeddings(self):
        embeddings = None
        try:
            embeddings = OpenAIEmbeddings(
                check_embedding_ctx_length=False,
                openai_api_key="sk-1234",
                base_url="http://localhost:1234/v1",
                model="text-embedding-embeddinggemma-300m",
            )
            embeddings.embed_query("test")
            print("Using LM Studio EmbeddingGemma with Chroma")
        except Exception:
            try:
                embeddings = OllamaEmbeddings(model="embeddinggemma:latest")
                embeddings.embed_query("test")
                print("Using Ollama EmbeddingGemma with Chroma")
            except Exception as e:
                print(f"Ollama EmbeddingGemma not available: {str(e)}")
                raise RuntimeError("No embedding backend available for CampaignHistory") from e
        return embeddings
    
    def process_documents(self, docs: list[Document], append: bool):
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=100, chunk_overlap=50
        )
        self.doc_splits = text_splitter.split_documents(docs)
        if not self.doc_splits:
            return
        
        persist_path = Path(self.persist_directory)
        if self.vectorstore is None:
            embeddings = self._build_embeddings()
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=embeddings,
            )
            # ensure we do not duplicate data if existing store already populated
            should_add = not persist_path.exists() or append
        else:
            should_add = append
        
        if should_add:
            self.vectorstore.add_documents(documents=self.doc_splits)
            if hasattr(self.vectorstore, "persist") and callable(getattr(self.vectorstore, "persist")):
                try:
                    self.vectorstore.persist()
                except Exception as exc:
                    print(f"Warning: unable to persist updated vectorstore: {exc}")

        # self.vectorstore = InMemoryVectorStore.from_documents(
        #     documents=self.doc_splits, embedding=embeddings
        # )
        self.retriever = self.vectorstore.as_retriever()
        
        self.retriever_tool = create_retriever_tool(
            self.retriever,
            "retrieve_campaign_results",
            "Search and return information about marketing campaigns history.",
        )
    
    def get_retriever_tool(self):
        return self.retriever_tool
    
    def get_retriever(self):
        return self.retriever