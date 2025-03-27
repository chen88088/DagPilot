import * as React from "react"
import DagPreview from "./components/DagPreview"

const PreviewPage: React.FC = () => {
  const data = localStorage.getItem("dagPreview")
  const parsed = data ? JSON.parse(data) : { nodes: [], edges: [] }

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-bold">📊 DAG 預覽圖</h1>
      <DagPreview nodes={parsed.nodes} edges={parsed.edges} />
    </div>
  )
}

export default PreviewPage
