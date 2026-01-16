import json

class SemanticLayer:
    def __init__(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)

        self.metrics = self.schema["metrics"]
        self.dimensions = self.schema["dimensions"]
        self.models = self.schema["models"]
        self.relationships = self.schema["relationships"]

    # ----------------------
    # INTENT VALIDATION
    # ----------------------
    def validate(self, intent: dict) -> dict:
        metric = intent.get("metric")
        dimensions = intent.get("dimensions", [])

        if metric not in self.metrics:
            raise ValueError(f"Metric '{metric}' not allowed")

        for dim in dimensions:
            if dim not in self.dimensions:
                raise ValueError(f"Dimension '{dim}' not allowed")

        self._validate_relationships(metric, dimensions)
        return intent

    # ----------------------
    # RELATIONSHIP GOVERNANCE
    # ----------------------
    def _validate_relationships(self, metric: str, dimensions: list):
        base_model = self.metrics[metric]["base_model"]

        for dim in dimensions:
            dim_model = self.dimensions[dim]["model"]

            if base_model == dim_model:
                continue

            allowed = any(
                (
                    r["from"] == base_model and r["to"] == dim_model
                ) or (
                    r["from"] == dim_model and r["to"] == base_model
                )
                for r in self.relationships
            )

            if not allowed:
                raise ValueError(
                    f"No approved relationship between '{base_model}' and '{dim_model}'"
                )

    # ----------------------
    # HELPERS
    # ----------------------
    def get_metric(self, metric: str):
        return self.metrics[metric]

    def get_dimension(self, dim: str):
        return self.dimensions[dim]

    def get_model(self, model: str):
        return self.models[model]

    # ✅ THIS METHOD WAS MISSING
    def get_relationship(self, from_model: str, to_model: str):
        for r in self.relationships:
            if (
                r["from"] == from_model and r["to"] == to_model
            ) or (
                r["from"] == to_model and r["to"] == from_model
            ):
                return r
        return None
