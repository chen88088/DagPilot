import * as React from "react"
import { useState } from "react"
import MonacoEditor from "./components/MonacoEditor"
import DagPreview from "./components/DagPreview"
import axios from "axios"

type DagNode = { id: string }
type DagEdge = { from: string; to: string }

const App: React.FC = () => {
  const [code, setCode] = useState(`# Example DAG\nfrom airflow import DAG`)
  const [question, setQuestion] = useState("")
  const [aiResponse, setAiResponse] = useState("")
  const [suggestedCode, setSuggestedCode] = useState("")
  const [loading, setLoading] = useState(false)
  const [dagPreview, setDagPreview] = useState<{ nodes: DagNode[]; edges: DagEdge[] } | null>(null)
  const [showPreview, setShowPreview] = useState(false)

  const askAI = async () => {
    if (!question.trim()) return
    setLoading(true)
    try {
      const res = await axios.post("http://localhost:8000/ai-assist", {
        dag_code: code,
        question: question,
      })
      setAiResponse(res.data.answer || "")
      setSuggestedCode(res.data.suggested_code || "")
    } catch (err) {
      console.error("AI 助理錯誤", err)
      setAiResponse("⚠️ AI 助理出錯了，請稍後再試。")
      setSuggestedCode("")
    } finally {
      setLoading(false)
    }
  }

  const insertSuggestion = () => {
    if (suggestedCode.trim()) {
      setCode((prev) => `${prev}\n\n# 🔽 AI 建議程式碼 🔽\n${suggestedCode}`)
    }
  }

  const previewDag = async () => {
    try {
      const res = await axios.post("http://localhost:8000/preview-dag", {
        dag_code: code,
      })
      setDagPreview(res.data)
      setShowPreview(true)
    } catch (err) {
      console.error("預覽 DAG 失敗", err)
      alert("⚠️ DAG 預覽失敗，請確認程式碼正確")
      setDagPreview(null)
      setShowPreview(false)
    }
  }

  return (
    <div className="p-6 space-y-6 w-full max-w-full">
      <h1 className="text-2xl font-bold">🚀 DagPilot DAG 編輯器 + AI 助理</h1>

      {/* ▶️ 程式碼編輯器 + 按鈕區 */}
      <div className="relative w-full space-y-4">
        <MonacoEditor code={code} onChange={(v) => setCode(v || "")} />

        {/* ✅ 獨立的按鈕區塊，緊貼編輯區下方 */}
        <div className="relative w-full mt-2">
          <button
            className="absolute left-0 bg-purple-600 text-white px-4 py-2 rounded"
            onClick={previewDag}
          >
            預覽 DAG 流程圖
          </button>

          <button
            className="absolute right-0 bg-emerald-600 text-white px-4 py-2 rounded"
            onClick={() => alert("🚀 準備部署 DAG！")}
          >
            部署
          </button>
        </div>
      </div>

      {/* ▶️ DAG 預覽圖區塊（可收合） */}
      {showPreview && dagPreview && (
        <div className="border border-gray-300 rounded p-4 relative max-h-[260px] overflow-auto">
          <h2 className="text-lg font-bold mb-2 flex items-center gap-2">
            <span>📊 DAG 預覽圖</span>
            <button
              onClick={() => setShowPreview(false)}
              className="ml-auto text-sm bg-gray-300 px-2 py-1 rounded hover:bg-gray-400"
            >
              收合
            </button>
          </h2>
          <DagPreview nodes={dagPreview.nodes} edges={dagPreview.edges} />
        </div>
      )}

      {/* ▶️ AI 助理提問區 */}
      <div className="mt-6">
        <h2 className="text-lg font-semibold mb-1">💬 提問 AI 助理</h2>
        <textarea
          className="w-full border rounded p-2"
          rows={3}
          placeholder="請輸入問題，例如：幫我加入 Slack 通知"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded mt-2 mr-2"
          onClick={askAI}
          disabled={loading}
        >
          {loading ? "請稍候..." : "發問"}
        </button>

        {suggestedCode && (
          <button
            className="bg-green-600 text-white px-4 py-2 rounded mt-2"
            onClick={insertSuggestion}
          >
            插入 AI 建議程式碼
          </button>
        )}
      </div>

      {/* ▶️ AI 回覆顯示區 */}
      {aiResponse && (
        <div className="bg-gray-100 p-4 rounded max-h-[400px] overflow-auto">
          <h3 className="font-semibold mb-2">🧠 AI 回覆：</h3>
          <pre className="whitespace-pre-wrap text-sm font-mono text-black">
            {aiResponse}
          </pre>
        </div>
      )}
    </div>
  )
}

export default App
