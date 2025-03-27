import * as React from "react"

type DagPreviewProps = {
  nodes: { id: string }[]
  edges: { from: string; to: string }[]
}

const DagPreview: React.FC<DagPreviewProps> = ({ nodes, edges }) => {
  const spacingX = 40
  const baseY = 80
  const nodePadding = 20
  const fontWidth = 8
  const minBoxWidth = 100

  const nodePositions: { [key: string]: { x: number; y: number } } = {}
  const nodeWidths: { [key: string]: number } = {}

  // 計算每個節點寬度
  nodes.forEach((node) => {
    const width = Math.max(minBoxWidth, node.id.length * fontWidth + nodePadding)
    nodeWidths[node.id] = width
  })

  // 計算每個節點位置（依據前面總長度 + spacing）
  let currentX = 100
  nodes.forEach((node) => {
    nodePositions[node.id] = { x: currentX, y: baseY }
    currentX += nodeWidths[node.id] + spacingX
  })

  return (
    <svg
      width="100%"
      height="300"
      viewBox="0 0 2000 300"
      className="bg-white border rounded shadow"
    >
      <defs>
        {/* 🔁 每條線都可共用這個箭頭 */}
        <marker
          id="arrow"
          markerWidth="10"
          markerHeight="10"
          refX="8"
          refY="5"
          orient="auto"
        >
          <path d="M0,0 L10,5 L0,10 Z" fill="#333" />
        </marker>
      </defs>

      {/* 畫線（每條邊） */}
      {edges.map((edge, i) => {
        const from = nodePositions[edge.from]
        const to = nodePositions[edge.to]
        const fromWidth = nodeWidths[edge.from] || minBoxWidth
        if (!from || !to) return null
        return (
          <line
            key={i}
            x1={from.x + fromWidth}
            y1={from.y + 20}
            x2={to.x}
            y2={to.y + 20}
            stroke="#000"
            strokeWidth={1.5}
            // markerEnd="url(#arrow)"
          />
        )
      })}

      {/* 畫節點 */}
      {nodes.map((node) => {
        const pos = nodePositions[node.id]
        const width = nodeWidths[node.id]
        return (
          <g key={node.id}>
            <rect
              x={pos.x}
              y={pos.y}
              width={width}
              height={40}
              fill="#facc15"
              rx={8}
            />
            <text
              x={pos.x + width / 2}
              y={pos.y + 25}
              textAnchor="middle"
              fill="#000"
              fontSize="12"
              fontFamily="monospace"
            >
              {node.id}
            </text>
          </g>
        )
      })}
    </svg>
  )
}

export default DagPreview
