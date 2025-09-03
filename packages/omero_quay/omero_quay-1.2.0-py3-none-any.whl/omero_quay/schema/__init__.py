from __future__ import annotations

from pathlib import Path

from linkml_runtime.utils.schemaview import SchemaView

SCHEMA = (Path(__file__).parent / "manifest-schema.yml").resolve()
view = SchemaView(SCHEMA)
