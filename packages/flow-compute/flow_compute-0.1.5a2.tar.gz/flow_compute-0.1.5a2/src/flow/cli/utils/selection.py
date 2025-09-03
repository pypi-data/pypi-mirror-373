"""Selection parser and model (core).

Parses index sets like ``1``, ``1-3``, ``1-3,5,7``. Also accepts the
legacy leading-colon form (e.g., ``:1``, ``:1-3``) for backward
compatibility.
"""

from __future__ import annotations

from dataclasses import dataclass


class SelectionParseError(Exception):
    pass


@dataclass
class Selection:
    indices: list[int]

    @staticmethod
    def parse(text: str) -> Selection:
        """Parse a selection expression into indices.

        Supports both bare-number and legacy leading-colon forms. Examples:

        - "1" -> [1]
        - "1-3,5" -> [1,2,3,5]
        - ":1-3,5" -> [1,2,3,5]  # legacy
        - "2,3,7," -> [2,3,7]  (trailing commas ignored)
        """
        s = text.strip()
        # Allow optional leading ':'
        body = s[1:] if s.startswith(":") else s
        if not body:
            raise SelectionParseError("Empty selection")
        parts = [p.strip() for p in body.split(",") if p.strip()]
        indices: list[int] = []
        for p in parts:
            if "-" in p:
                a, b = p.split("-", 1)
                if not (a.isdigit() and b.isdigit()):
                    raise SelectionParseError(f"Invalid range: {p}")
                start = int(a)
                end = int(b)
                if end < start:
                    raise SelectionParseError(f"Invalid range: {p}")
                indices.extend(range(start, end + 1))
            else:
                if not p.isdigit():
                    raise SelectionParseError(f"Invalid index: {p}")
                indices.append(int(p))
        # De-duplicate while preserving order
        seen = set()
        uniq: list[int] = []
        for i in indices:
            if i not in seen:
                seen.add(i)
                uniq.append(i)
        return Selection(indices=uniq)

    def to_task_ids(self, index_to_task_id: dict[str, str]) -> tuple[list[str], list[str]]:
        """Map parsed indices to task IDs using a provided index map.

        Args:
            index_to_task_id: Mapping of 1-based index (as string) to task_id,
                typically produced by TaskIndexCache.get_indices_map().

        Returns:
            A tuple of (task_ids, errors). If any index is out of range, an
            explanatory error string will be included in the errors list.
        """
        task_ids: list[str] = []
        errors: list[str] = []

        if not index_to_task_id:
            return task_ids, ["No recent task list. Run 'flow status' to refresh indices"]

        # Determine max index for helpful error messages
        try:
            available_indices = [int(k) for k in index_to_task_id if str(k).isdigit()]
            max_index = max(available_indices) if available_indices else 0
        except Exception:
            max_index = 0

        for index in self.indices:
            task_id = index_to_task_id.get(str(index))
            if task_id:
                task_ids.append(task_id)
            else:
                if max_index > 0:
                    errors.append(f"Index {index} out of range (1-{max_index})")
                else:
                    errors.append(f"Unknown index: {index}")

        return task_ids, errors
