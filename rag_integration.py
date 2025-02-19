import json
import os
import requests
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from logging_utils import log_message, ConsoleColor

A1 = {
  "questions": [
    "What is the central theme of the book, and how is it developed throughout the narrative?",
    "Who are the key characters, and what are their motivations, conflicts, and arcs?",
    "What literary techniques (symbolism, metaphor, foreshadowing) are used, and how do they enhance the story?",
    "What crucial information or insights can be derived from this book?",
    "How does the book reflect its historical, cultural, or social context?",
    "What is the author's intent or message, and how is it conveyed through the text?",
    "What narrative structure is employed, and how does it affect the reader's experience?",
    "How do the setting and atmosphere contribute to the mood and themes of the book?",
    "What are the major conflicts and resolutions, and what do they reveal about the characters or themes?",
    "How does the book compare to other works in the same genre or by the same author?",
    "What are the notable quotes or passages, and why are they significant?",
    "How do literary devices like irony, allegory, and satire function within the text?",
    "What philosophical or moral questions are raised by the book, and how are they explored?",
    "How does the book's pacing and tone influence the reader's engagement?",
    "What critical interpretations or academic analyses exist for this book?",
  ]
}

def query_ollama(prompt: str, api_key: str) -> str:
    url = "http://ollama:11434/v1/generate"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "input": prompt,
        "model": "llama2"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()["response"]
    else:
        raise ValueError(f"Error with Ollama API: {response.text}")

def run_rag_system(
    api_key: str,
    persist_dir: str,
    data_dir: str,
) -> str:
    try:
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        index = load_index_from_storage(storage_context)
        log_message("✅ Index loaded from disk.", color=ConsoleColor.GREEN)
    except FileNotFoundError:
        if not os.path.isdir(data_dir) or not os.listdir(data_dir):
            raise ValueError(f"🚨 No documents found in '{data_dir}'. Please add files to index.")
        documents = SimpleDirectoryReader(data_dir).load_data()
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=persist_dir)
        log_message("✅ Index created and persisted to disk.", color=ConsoleColor.GREEN)

    summary_query = ("Provide a concise summary of the key themes and content of this book. "
                     "Consider foundational assumptions, core elements, evident patterns, long-term implications, "
                     "and key stakeholders from the provided data: "
                     f"{json.dumps(A1)}")
    
    try:
        book_summary = query_ollama(summary_query, api_key)
        log_message("✅ RAG system completed. Returning final improved response.", color=ConsoleColor.GREEN)
    except ValueError as e:
        log_message(f"❌ Error in querying Ollama: {str(e)}", color=ConsoleColor.RED)
        return str(e)
    
    return book_summary
