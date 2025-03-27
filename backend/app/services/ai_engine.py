import os
import git
import re
import gc
import traceback
from typing import Tuple
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI  # ✅ 改成新版匯入

# ✅ Load API key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ OpenAI API Key 未找到，請確認 .env 設定正確！")

# ✅ Constants
GITLAB_REPO_URL = "https://gitlab.com/chen88088/mlops_dag_template.git"
LOCAL_DAG_FOLDER = "gitlab_dags"
VECTOR_DB_FOLDER = "dag_vector_db"

# ✅ Global cache
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
faiss_index = None

# ✅ 建立 OpenAI 客戶端
client = OpenAI(api_key=OPENAI_API_KEY)

# ✅ Clone or update Git repo
def sync_gitlab_repo():
    if os.path.exists(LOCAL_DAG_FOLDER):
        print("✅ GitLab Repo 已存在，正在更新...")
        repo = git.Repo(LOCAL_DAG_FOLDER)
        repo.remotes.origin.pull()
    else:
        print("✅ 正在從 GitLab Clone Repo...")
        git.Repo.clone_from(GITLAB_REPO_URL, LOCAL_DAG_FOLDER)
    print("✅ DAG 模板已同步完成！")

# ✅ 建立 FAISS 向量庫
def build_faiss_index():
    global faiss_index
    dag_texts = []
    for filename in os.listdir(LOCAL_DAG_FOLDER):
        if filename.endswith(".py"):
            with open(os.path.join(LOCAL_DAG_FOLDER, filename), "r", encoding="utf-8") as f:
                dag_texts.append(f.read())
    faiss_index = FAISS.from_texts(dag_texts, embeddings)
    faiss_index.save_local(VECTOR_DB_FOLDER)
    print(f"✅ 建立 FAISS 成功，載入了 {len(dag_texts)} 個模板")

# ✅ 載入 FAISS（只做一次）
def load_faiss():
    global faiss_index
    if not faiss_index:
        faiss_index = FAISS.load_local(VECTOR_DB_FOLDER, embeddings, allow_dangerous_deserialization=True)
        print("✅ FAISS Index 載入完成")

# ✅ 核心主流程：查詢 + AI 回應
def run_ai_assist(question: str, dag_code: str = "") -> Tuple[str, str]:
    try:
        load_faiss()
        docs = faiss_index.similarity_search(question, k=1)
        best_dag = docs[0].page_content

        user_dag = f"使用者目前的 DAG 程式碼：\n{dag_code}" if dag_code.strip() else ""

        prompt = (
            "你是一位專精於 Airflow 的工程師。請根據下列兩段資訊，整合出一個符合提問需求的完整 DAG：\n\n"
            f"- GitLab 中最相似的 DAG 範例：\n{best_dag}\n\n"
            f"{user_dag}\n"
            f"請你：\n"
            f"1. 根據需求 '{question}' 增加必要任務。\n"
            "2. 修改 owner 為 'jerryChen'。\n"
            "3. 加上 email 通知 'chen88088@gmail.com'。\n"
            "4. 若有原始 DAG 程式碼，請保留其任務結構與相依順序，並整合建議。\n"
            "5. 請直接輸出完整 Python 程式碼，不要附加說明，不要省略任何任務與內容，請完整保留每一行程式碼。"
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一位專精於 Airflow 的工程師。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=3000
        )

        answer = response.choices[0].message.content.strip()

        if "```python" in answer:
            code_match = re.search(r"```python\n(.*?)```", answer, re.DOTALL)
            code = code_match.group(1).strip() if code_match else answer
        else:
            code = answer

        return answer, code

    except Exception as e:
        print("❌ AI 助理發生錯誤：", e)
        traceback.print_exc()
        return "⚠️ AI 助理出錯了，請稍後再試。", ""

    finally:
        gc.collect()

# ✅ 初始建構（只做一次）
if __name__ == "__main__":
    sync_gitlab_repo()
    build_faiss_index()
    full, code = run_ai_assist("加入 Slack 通知", "")
    print("\n💬 Response:\n", full)
    print("\n🧾 DAG code:\n", code)
