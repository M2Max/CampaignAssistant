from langchain_classic.tools.retriever import create_retriever_tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pathlib import Path


class CampaignHistory:
    def __init__(self, txt_directory: str = None):
        self.txt_directory = txt_directory
        self.doc_splits = []
        self.vectorstore = None
        self.retriever = None
        self.retriever_tool = None
        
        if txt_directory:
            self._load_documents_from_directory()
    
    def _load_documents_from_directory(self):
        docs = []
        txt_files = Path(self.txt_directory).glob("*.txt")
        
        for txt_file in txt_files:
            loader = TextLoader(str(txt_file))
            docs.extend(loader.load())
        
        self._process_documents(docs)
    
    def add_documents(self, documents: list[Document]):
        self._process_documents(documents)
    
    def _process_documents(self, docs: list[Document]):
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=100, chunk_overlap=50
        )
        self.doc_splits = text_splitter.split_documents(docs)
        
        self.vectorstore = InMemoryVectorStore.from_documents(
            documents=self.doc_splits, embedding=OpenAIEmbeddings()
        )
        self.retriever = self.vectorstore.as_retriever()
        
        self.retriever_tool = create_retriever_tool(
            self.retriever,
            "retrieve_campaign_posts",
            "Search and return information about campaign history.",
        )
    
    def get_retriever_tool(self):
        return self.retriever_tool
    
    def get_retriever(self):
        return self.retriever