import * as React from "react"
import ReactDOM from "react-dom/client"
import App from "./App"
import { BrowserRouter, Routes, Route } from "react-router-dom"
import PreviewPage from "./PreviewPage"


ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/preview" element={<PreviewPage />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
)
