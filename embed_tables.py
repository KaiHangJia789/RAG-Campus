# embed_tables.py
import os
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import DashScopeEmbeddings  # 如果用阿里云的 text-embedding-v4
from config_data import (
    CHROMA_PERSIST_DIR, 
    QWEN_API_KEY, 
    QWEN_EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    SEPARATORS,
    PDF_PATH
)
from extract_table import extract_tables_to_text

def embed_table_descriptions():
    # 1. 抽取表格描述
    table_texts = extract_tables_to_text(PDF_PATH)
    if not table_texts:
        print("未找到表格数据，无需嵌入。")
        return

    # 2. 初始化嵌入模型（使用 DashScope 的 text-embedding-v4）
    embeddings = DashScopeEmbeddings(
        model=QWEN_EMBEDDING_MODEL,
        dashscope_api_key=QWEN_API_KEY
    )

    # 3. 加载已有向量库
    vectorstore = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embeddings,
        collection_name="chroma_db" 
    )

    # 4. 将表格描述包装成 Document，简单处理（可不用再切分，因为表格描述通常很短）
    docs = []
    for text in table_texts:
        docs.append(Document(page_content=text, metadata={"source": "表格数据"}))

    # 如果表格描述很长的话，可在这里用 TextSplitter 再切分，但通常一句就够
    # from langchain.text_splitter import RecursiveCharacterTextSplitter
    # splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, separators=SEPARATORS)
    # docs = splitter.split_documents(docs)

    # 5. 添加到向量库
    vectorstore.add_documents(docs)
    vectorstore.persist()
    print(f"已成功将 {len(docs)} 条表格描述存入 Chroma。")

if __name__ == "__main__":
    embed_table_descriptions()