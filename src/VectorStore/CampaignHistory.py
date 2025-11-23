from langchain_core.tools.retriever import create_retriever_tool
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from pathlib import Path
import os
import tempfile
from typing import Union, List, Any

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

        # Initialize embedding model
        self.embeddings = self._initialize_embeddings()

        if txt_directory:
            self.load_documents_from_directory()
    
    def _initialize_embeddings(self):
        try:
            embeddings = OpenAIEmbeddings(check_embedding_ctx_length=False,  openai_api_key="sk-1234", base_url="http://localhost:1234/v1",model="text-embedding-embeddinggemma-300m")
            embeddings.embed_query("test")
            print("Using LM Studio EmbeddingGemma with Chroma")
            return embeddings
        except Exception as e:
            try:
                embeddings = OllamaEmbeddings(model="embeddinggemma:latest")
                embeddings.embed_query("test")
                print("Using Ollama EmbeddingGemma with Chroma")
                return embeddings
            except Exception as e:
                print(f"Ollama EmbeddingGemma not available: {str(e)}")
                return None

    def add_documents(self, documents: List[Any]):
        """
        1. Generic add_documents method which receives a list of documents.
        Can receive file paths (str, Path), Streamlit UploadedFiles, or existing Document objects.
        """
        all_parsed_documents = []
        
        for doc in documents:
            # 2. For each one, it understands if it has a processor for it and uses it to parse it
            parsed_docs = self._parse_document(doc)
            if parsed_docs:
                all_parsed_documents.extend(parsed_docs)
        
        # 3. After that each parsed document passes through the same kind of post processor
        if all_parsed_documents:
            self._post_process_documents(all_parsed_documents)

    def _parse_document(self, doc_input: Any) -> List[Document]:
        """
        Identifies the input type and delegates to the correct processor.
        """
        # Case 1: It's already a LangChain Document
        if isinstance(doc_input, Document):
            return [doc_input]
            
        # Case 2: It's a Streamlit UploadedFile (has read/name/getvalue)
        if hasattr(doc_input, 'read') and hasattr(doc_input, 'name'):
            return self._process_uploaded_file(doc_input)
            
        # Case 3: It's a file path (str or Path)
        if isinstance(doc_input, (str, Path)):
            path = Path(doc_input)
            if path.exists():
                return self._process_file_path(path)
            else:
                print(f"Warning: File not found: {path}")
                return []
                
        print(f"Warning: Unsupported document type: {type(doc_input)}")
        return []

    def _process_uploaded_file(self, uploaded_file) -> List[Document]:
        """
        Processor for Streamlit UploadedFile objects.
        Saves to a temp file and then delegates to file path processor.
        """
        file_extension = Path(uploaded_file.name).suffix.lower()
        
        # Get content
        if hasattr(uploaded_file, 'getvalue'):
            content = uploaded_file.getvalue()
        else:
            content = uploaded_file.read()
            if hasattr(uploaded_file, 'seek'):
                uploaded_file.seek(0)
                
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name
            
        try:
            # Delegate to file path processor
            return self._process_file_path(Path(tmp_path))
        finally:
            # Clean up
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def _process_file_path(self, file_path: Path) -> List[Document]:
        """
        Processor for file paths. Selects specific loader based on extension.
        """
        suffix = file_path.suffix.lower()
        
        try:
            if suffix == '.pdf':
                loader = PyMuPDFLoader(str(file_path))
                return loader.load()
            elif suffix in ['.txt', '.md']:
                loader = TextLoader(str(file_path))
                return loader.load()
            else:
                print(f"Warning: No processor for file extension {suffix}")
                return []
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return []

    def _post_process_documents(self, docs: List[Document]):
        """
        3. Post processor which chunks and then embeds it
        """
        # 3a. Chunking
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=100, chunk_overlap=50
        )
        new_splits = text_splitter.split_documents(docs)
        self.doc_splits.extend(new_splits)

        # 3b. Embedding (Adding to VectorStore)
        persist_path = Path(self.persist_directory)
        
        if self.vectorstore is None:
             # Try to load existing or create new
            if persist_path.exists():
                try:
                    self.vectorstore = Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)
                    # Check if we need to add the new docs (if we just loaded it)
                    # Note: Chroma persists automatically, so if we loaded it, we just add new docs
                    self.vectorstore.add_documents(documents=new_splits)
                except Exception as e:
                    print(f"Could not load existing Chroma store, creating new: {str(e)[:80]}")
                    self._create_new_vectorstore(new_splits)
            else:
                self._create_new_vectorstore(new_splits)
        else:
            # Vectorstore already loaded in memory, just add docs
            self.vectorstore.add_documents(documents=new_splits)
            
        # Update retriever
        self.retriever = self.vectorstore.as_retriever()
        self._update_retriever_tool()

    def _create_new_vectorstore(self, splits):
        print("Creating new Chroma vector store")
        self.vectorstore = Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)
        self.vectorstore.add_documents(documents=splits)
        print(f"Added {len(splits)} chunks. Done.")

    def _update_retriever_tool(self):
        self.retriever_tool = create_retriever_tool(
            self.retriever,
            "retrieve_campaign_results",
            "Search and return information about marketing campaigns history.",
        )

    def load_documents_from_directory(self):
        """
        Legacy support: Loads all supported files from the configured directory.
        """
        if not self.txt_directory:
            return
            
        directory_path = Path(self.txt_directory)
        files_to_process = []
        
        # Gather all supported files
        for pattern in ["*.txt", "*.md", "*.pdf"]:
            files_to_process.extend(list(directory_path.glob(pattern)))
            
        # Use the generic add_documents method
        if files_to_process:
            self.add_documents(files_to_process)

    def get_retriever_tool(self):
        if self.retriever_tool is None:
            # Initialize empty if not ready
            pass 
        return self.retriever_tool
    
    def get_retriever(self):
        return self.retriever
