import os
import gc
from dotenv import load_dotenv
from typing import Tuple
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from autogen import AssistantAgent, UserProxyAgent

# ✅ 載入環境變數
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ OpenAI API Key 未找到，請確認 .env 設定正確！")

# ✅ 向量庫與 Embeddings 初始化
VECTOR_DB_FOLDER = "dag_vector_db"
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
faiss_index = FAISS.load_local(VECTOR_DB_FOLDER, embeddings, allow_dangerous_deserialization=True)

# ✅ 初始化 AutoGen Agents
dag_creator = AssistantAgent(
    name="DAG_Creator",
    llm_config={
        "model": "gpt-3.5-turbo",
        "api_key": OPENAI_API_KEY,
    }
)
user = UserProxyAgent(name="user")

# ✅ 主流程：查詢 + 自動對話整合 DAG

def run_ai_assist_autogen(question: str, dag_code: str = "") -> Tuple[str, str]:
    try:
        # 查詢最相似 DAG 範本
        retrieved_docs = faiss_index.similarity_search(question, k=1)
        best_dag = retrieved_docs[0].page_content

        user_dag = f"使用者目前的 DAG 程式碼：\n{dag_code}" if dag_code.strip() else ""

        # 建立完整提示詞
        message = f"""
你是一位專精於 Airflow 的工程師。請根據下列兩段資訊，整合出一個符合提問需求的完整 DAG：

- GitLab 中最相似的 DAG 範例：
{best_dag}

{user_dag}
請你：
1. 根據需求 '{question}' 增加必要任務。
2. 修改 owner 為 'jerryChen'。
3. 加上 email 通知 'chen88088@gmail.com'。
4. 若有原始 DAG 程式碼，請保留其任務結構與相依順序，並整合建議。
5. 請直接輸出完整 Python 程式碼，不要附加說明，不要省略任何任務與內容，請完整保留每一行程式碼。
        """

        # 啟動對話
        response = user.initiate_chat(
            dag_creator,
            message=message,
            summary_method="last_msg",
            clear_history=True
        )

        response_text = str(response)

        # ✅ 萃取程式碼部分
        if "```python" in response_text:
            start_idx = response_text.find("```python") + len("```python\n")
            end_idx = response_text.find("```", start_idx)
            dag_code = response_text[start_idx:end_idx].strip()
        else:
            dag_code = response_text.strip()

        return response_text, dag_code

    except Exception as e:
        print("❌ AutoGen 模式出錯：", e)
        return "⚠️ AI 助理出錯了，請稍後再試。", ""

    finally:
        gc.collect()
