import Editor from "@monaco-editor/react"
import * as React from "react"

type MonacoEditorProps = {
  code: string
  onChange: (value: string | undefined) => void
}

const MonacoEditor: React.FC<MonacoEditorProps> = ({ code, onChange }) => {
  return (
    <Editor
      height="400px"
      defaultLanguage="python"
      value={code}
      onChange={onChange}
      theme="vs-dark"
    />
  )
}

export default MonacoEditor
