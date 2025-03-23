import os
import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.utils import setup_logger
import numpy as np
from lightrag.utils import EmbeddingFunc
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from dotenv import load_dotenv

load_dotenv()

setup_logger("lightrag", level="INFO")

async def llm_model_func(
    prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs
) -> str:
    return await openai_complete_if_cache(
        "qwen2.5-7b-instruct-1m",
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        api_key="none",
        base_url="http://192.168.31.58:1234/v1",
        **kwargs
    )

async def embedding_func(texts: list[str]) -> np.ndarray:
    return await openai_embed(
        texts,
        model="text-embedding-bge-m3",
        api_key="none",
        base_url="http://192.168.31.58:1234/v1",
    )


# Setup logger for LightRAG
setup_logger("lightrag", level="INFO")

async def initialize_rag():
    rag = LightRAG(
        working_dir="extracted",
        embedding_func=EmbeddingFunc(
            embedding_dim=1024,
            max_token_size=8194,
            func=embedding_func,
        ),
        llm_model_func=llm_model_func,
        graph_storage="Neo4JStorage", #<-----------override KG default
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag

def main():
    # Initialize RAG instance
    rag = asyncio.run(initialize_rag())
    # Insert text
    import textract

    base_path = "/Users/harrychen/Projects/ChatSeia/output"
    file_paths = os.listdir(base_path)
    documents = [textract.process(os.path.join(base_path, file_path)).decode('utf-8') for file_path in file_paths]

    # Insert documents with file paths
    rag.insert(documents, file_paths=file_paths)
    print("Documents inserted successfully.")

    # Perform naive search
    mode="naive"
    # Perform local search
    mode="local"
    # Perform global search
    mode="global"
    # Perform hybrid search
    mode="hybrid"
    # Mix mode Integrates knowledge graph and vector retrieval.
    mode="mix"

    rag.query(
        "What are the top themes in this story?",
        param=QueryParam(mode=mode)
    )

if __name__ == "__main__":
    main()