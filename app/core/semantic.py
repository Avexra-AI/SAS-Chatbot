# app/core/semantic.py

import json
from pathlib import Path
from typing import Dict


class SemanticLayer:
    def __init__(self, semantic_path: Path | None = None):
        self.semantic_path = semantic_path or self._default_path()
        self.layer = self._load_layer()

    def _default_path(self) -> Path:
        return Path(
            "/home/deepak/AVEXRA-AI/Project First SAS/sas_semantic_layer.mdl.json"
        )

    def _load_layer(self) -> Dict:
        if not self.semantic_path.exists():
            raise FileNotFoundError(
                f"Semantic layer file not found at {self.semantic_path}"
            )
        with open(self.semantic_path, "r") as f:
            return json.load(f)

    # ---------- Guardrail helpers ----------

    def allowed_tables_text(self) -> str:
        return "\n".join(
            f"- {m['name']} ({', '.join(c['name'] for c in m['columns'])})"
            for m in self.layer["models"]
        )

    def allowed_joins_text(self) -> str:
        return "\n".join(
            f"- {r['condition']}"
            for r in self.layer.get("relationships", [])
        )

    def forbidden_concepts_text(self) -> str:
        return (
            "Profit, margin, tax, GST, discount, cost price "
            "are NOT available unless explicitly defined."
        )
