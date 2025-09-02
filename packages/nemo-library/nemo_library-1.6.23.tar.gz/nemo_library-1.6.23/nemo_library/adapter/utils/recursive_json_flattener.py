import uuid
from typing import Any


class RecursiveJsonFlattener:
    """
    Recursively flattens JSON structures into fully contextualized rows.
    - All scalars and dicts are first resolved into a base context.
    - Lists of dicts create new rows, inheriting the full parent context.
    - Metadata includes __depth__, __path__, __parent_id__, __count__, row_id.
    """

    def __init__(self):
        self.rows: list[dict] = []

    def flatten(self, data: list[dict]) -> list[dict]:
        """Entry point for flattening."""
        self.rows = []
        for entry in data:
            self._flatten_node(
                entry, parent_context={}, depth=0, path="root", parent_id=None
            )
        return self.rows

    def _flatten_node(
        self,
        obj: dict,
        parent_context: dict[str, Any],
        depth: int,
        path: str,
        parent_id: str | None,
    ) -> None:
        """Flattens a single JSON object by first resolving context, then descending into lists."""
        row_id = str(uuid.uuid4())
        context = dict(parent_context)
        context["__depth__"] = depth
        context["__path__"] = path
        context["__parent_id__"] = parent_id
        context["row_id"] = row_id

        # Step 1: resolve scalars and dicts into the context
        for key, value in obj.items():
            full_key = f"{key}" if path == "root" else f"{path}.{key}"

            if isinstance(value, dict):
                flattened = self._flatten_dict(value, prefix=full_key)
                context.update(flattened)
            elif not isinstance(value, list):
                context[full_key] = value

        # Step 2: find expandable lists of dicts
        expanded = False
        for key, value in obj.items():
            if isinstance(value, list) and all(isinstance(i, dict) for i in value):
                full_key = f"{key}" if path == "root" else f"{path}.{key}"
                context[f"__count__.{full_key}"] = len(value)
                for child in value:
                    self._flatten_node(
                        obj=child,
                        parent_context=context,
                        depth=depth + 1,
                        path=full_key,
                        parent_id=row_id,
                    )
                expanded = True

        # Step 3: emit current context as a row only if nothing was expanded
        if not expanded:
            self.rows.append(context)

    def _flatten_dict(self, d: dict, prefix: str) -> dict:
        """Flattens nested dicts using dot-notation."""
        result = {}
        for k, v in d.items():
            key = f"{prefix}.{k}"
            if isinstance(v, dict):
                result.update(self._flatten_dict(v, prefix=key))
            else:
                result[key] = v
        return result
