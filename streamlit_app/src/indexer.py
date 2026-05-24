import os
import json
from typing import List
from unstructured.chunking.title import chunk_by_title
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2", 
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True} 
)

DB_PATH = "./chroma_db"

def seperate_content_types(chunk):
    content_data = {
        'text': chunk.text,
        'tables': [],
        'images': [],
        'types': ['text']
    }
    if hasattr(chunk, 'metadata') and hasattr(chunk.metadata, 'orig_elements'):
        for element in chunk.metadata.orig_elements:
            element_type = type(element).__name__
            if element_type == 'Table':
                if 'table' not in content_data['types']:
                    content_data['types'].append('table')
                table_html = getattr(element.metadata, 'text_as_html', element.text) 
                content_data['tables'].append(table_html)
    return content_data

def create_ai_enhanced_summary(text: str, tables: List[str]):
    print('Enhancing table content before embedding...')
    llm = ChatGoogleGenerativeAI(
        model='gemini-2.5-flash', 
        google_api_key=os.getenv('GEMINI_API_KEY'),
        temperature=0.1
    )
    table_content = "\\n\\n".join([f'Table (html):{t}' for t in tables])
    prompt_text = f"""
    You are an analyst. Summarize this document for research purposes.
    REQUIREMENT: Extract data from the table.
    TEXT: {text}
    {table_content}
    """
    message = HumanMessage(content=prompt_text)
    response = llm.invoke([message])
    return response.content

def index_contract(elements, filename="uploaded_contract.pdf"):
    print("Chunking documents by title...")
    chunks = chunk_by_title(
        elements=elements,
        combine_text_under_n_chars=250,      
        max_characters=1500,                
        new_after_n_chars=1000,                
        overlap=150                          
    )
    
    langchain_documents = []
    total_chunks = len(chunks)
    
    # STATEFUL TRACKING: Giữ tiêu đề ở ngoài vòng lặp
    current_title = "General Clause"
    
    for i, chunk in enumerate(chunks):
        print(f"-> Processing chunk {i + 1}/{total_chunks}")
        content_data = seperate_content_types(chunk)
        
        # Lấy Tên Điều Khoản
        if hasattr(chunk, 'metadata') and hasattr(chunk.metadata, 'orig_elements'):
            for el in chunk.metadata.orig_elements:
                if type(el).__name__ == 'Title':
                    current_title = el.text
                    break
        
        clause_name = current_title
                    
        enhanced_content = content_data['text']
        if content_data['tables']:
            try:
                enhanced_content = create_ai_enhanced_summary(
                    content_data['text'],
                    content_data['tables']
                )
            except Exception as e:
                print(f"Failed to enhance table: {e}")
                
        doc = Document(
            page_content=enhanced_content,
            metadata={
                'source': filename,
                'clause': clause_name,
                'page': chunk.metadata.page_number if hasattr(chunk.metadata, 'page_number') else 1
            }
        )
        langchain_documents.append(doc)
        
    print(f"Finished processing {len(langchain_documents)} chunks. Saving to ChromaDB...")
    vector_db = Chroma.from_documents(documents=langchain_documents, embedding=embeddings, persist_directory=DB_PATH)
    return vector_db

def get_retriever():
    if os.path.exists(DB_PATH):
        vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
        return vector_db.as_retriever(search_kwargs={"k": 3})
    return None
