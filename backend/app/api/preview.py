from fastapi import APIRouter
from pydantic import BaseModel
import ast
from typing import List, Dict

router = APIRouter()

class PreviewRequest(BaseModel):
    dag_code: str

@router.post("/preview-dag")
def preview_dag(request: PreviewRequest):
    dag_code = request.dag_code
    try:
        tree = ast.parse(dag_code)
        tasks = {}
        edges = []

        class DAGVisitor(ast.NodeVisitor):
            def visit_Assign(self, node):
                # 掃描 PythonOperator 宣告
                if isinstance(node.value, ast.Call):
                    func = node.value.func
                    if isinstance(func, ast.Name) and func.id == 'PythonOperator':
                        task_id = None
                        for kw in node.value.keywords:
                            if kw.arg == 'task_id' and isinstance(kw.value, ast.Constant):
                                task_id = kw.value.value
                        if task_id and isinstance(node.targets[0], ast.Name):
                            tasks[node.targets[0].id] = task_id
                self.generic_visit(node)

            def visit_Expr(self, node):
                # 處理任務依賴關係：A >> B >> C
                if isinstance(node.value, ast.BinOp):
                    self.handle_dependency(node.value)
                self.generic_visit(node)

            def handle_dependency(self, binop):
                if isinstance(binop.op, ast.RShift):
                    left = self.extract_chain(binop.left)
                    right = self.extract_chain(binop.right)
                    for src in left:
                        for tgt in right:
                            edges.append((src, tgt))

            def extract_chain(self, node):
                if isinstance(node, ast.Name):
                    return [node.id]
                elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.RShift):
                    return self.extract_chain(node.left) + self.extract_chain(node.right)
                return []

        DAGVisitor().visit(tree)

        # ✅ nodes 用 task_id 命名，edges 用 Python 變數名稱連接
        node_list = [{"id": v} for v in tasks.values()]
        edge_list = [
            {"from": tasks.get(src, src), "to": tasks.get(dst, dst)} for src, dst in edges
        ]

        return {"nodes": node_list, "edges": edge_list}

    except Exception as e:
        return {"error": f"解析 DAG 時發生錯誤: {str(e)}"}
