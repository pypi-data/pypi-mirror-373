from __future__ import annotations

from typing import Callable, Dict, Optional
import json
import csv
import io
from rich.table import Table


class ArtifactPreviewRegistry:
    """Simple registry mapping content-types or extensions to preview functions.

    preview_fn signature: (content: bytes, filename: str) -> str | rich.Table
    """

    def __init__(self) -> None:
        self._by_ext: Dict[str, Callable[[bytes, str], object]] = {}
        self._by_mime: Dict[str, Callable[[bytes, str], object]] = {}

    def register_extension(self, ext: str, fn: Callable[[bytes, str], object]) -> None:
        self._by_ext[ext.lower().lstrip('.')] = fn

    def register_mime(self, mime: str, fn: Callable[[bytes, str], object]) -> None:
        self._by_mime[mime.lower()] = fn

    def preview(self, content: bytes, filename: str, content_type: Optional[str] = None) -> Optional[object]:
        if content_type:
            fn = self._by_mime.get(content_type.lower())
            if fn:
                return fn(content, filename)
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        fn = self._by_ext.get(ext)
        if fn:
            return fn(content, filename)
        return None


# -------- Default previewers and helpers --------

def _preview_json_basic(content: bytes, filename: str) -> str | Table:
    text = content.decode('utf-8', errors='ignore')
    data_obj = json.loads(text or "")
    if isinstance(data_obj, list) and data_obj and isinstance(data_obj[0], dict):
        cols = list(data_obj[0].keys())[:20]
        table = Table(title=f"JSON Preview: {filename}")
        for c in cols:
            table.add_column(str(c))
        for row in data_obj[:100]:
            table.add_row(*[str(row.get(c, ""))[:120] for c in cols])
        return table
    return json.dumps(data_obj, indent=2)


def _preview_csv_basic(content: bytes, filename: str) -> str | Table:
    text = content.decode('utf-8', errors='ignore')
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample)
    except Exception:
        dialect = csv.excel
    reader = csv.reader(io.StringIO(text), dialect)
    rows = list(reader)
    if not rows:
        return "Empty CSV"
    table = Table(title=f"CSV Preview: {filename}")
    header = rows[0]
    for h in header[:20]:
        table.add_column(str(h))
    for r in rows[1:101]:
        table.add_row(*[str(x)[:120] for x in r[:20]])
    return table


def _preview_blast_json(content: bytes, filename: str) -> Optional[Table]:
    # Heuristic BLAST JSON (common fields vary). Try alignments-like summary.
    try:
        data = json.loads(content.decode('utf-8', errors='ignore') or "{}")
    except Exception:
        return None
    # Detect by filename or keys
    lower_name = filename.lower()
    if 'blast' not in lower_name and not any(k in data for k in ("BlastOutput", "alignments", "BlastOutput2")):
        return None
    # Extract best-effort alignments
    rows = []
    if isinstance(data, dict):
        # Try standard-ish structure
        aligns = data.get('alignments') or []
        if isinstance(aligns, list):
            for a in aligns[:100]:
                if not isinstance(a, dict):
                    continue
                rows.append(
                    [
                        str(a.get('target') or a.get('id') or a.get('accession') or ''),
                        str(a.get('e_value') or a.get('evalue') or ''),
                        str(a.get('bit_score') or a.get('bitscore') or ''),
                        str(a.get('identity') or a.get('identity_pct') or ''),
                    ]
                )
        # Try NCBI BlastOutput2 structure
        if not rows and isinstance(data.get('BlastOutput2'), list):
            try:
                for report in data['BlastOutput2'][:5]:
                    it = report.get('report', {}).get('results', {}).get('search', {}).get('hits', [])
                    for h in it[:100]:
                        hsps = h.get('hsps') or []
                        top = hsps[0] if hsps else {}
                        rows.append([
                            str(h.get('description', [{}])[0].get('id', '')),
                            str(top.get('evalue', '')),
                            str(top.get('bit_score', '')),
                            str(top.get('identity', '')),
                        ])
            except Exception:
                pass
    if not rows:
        return None
    table = Table(title=f"BLAST Summary: {filename}")
    for c in ("Target", "E-value", "BitScore", "Identity"):
        table.add_column(c)
    for r in rows:
        table.add_row(*[str(x)[:120] for x in r])
    return table


def _preview_validation_json(content: bytes, filename: str) -> Optional[Table]:
    # Heuristic validation monitor summary
    try:
        data = json.loads(content.decode('utf-8', errors='ignore') or "{}")
    except Exception:
        return None
    lower_name = filename.lower()
    if not any(x in lower_name for x in ("validation", "monitor")) and not any(
        k in data for k in ("validation", "status", "metrics")
    ):
        return None
    # Collect simple key-value metrics from top-level dicts
    items = []
    if isinstance(data, dict):
        for k, v in list(data.items())[:50]:
            if isinstance(v, (str, int, float)):
                items.append((k, v))
        metrics = data.get('metrics')
        if isinstance(metrics, dict):
            for k, v in list(metrics.items())[:50]:
                if isinstance(v, (str, int, float)):
                    items.append((k, v))
    if not items:
        return None
    table = Table(title=f"Validation Summary: {filename}")
    table.add_column("Metric")
    table.add_column("Value")
    for k, v in items[:100]:
        table.add_row(str(k), str(v))
    return table


def register_default_previewers(registry: ArtifactPreviewRegistry) -> ArtifactPreviewRegistry:
    # JSON: prefer specialized then basic
    def json_wrapper(content: bytes, filename: str) -> object:
        for fn in (_preview_blast_json, _preview_validation_json):
            try:
                table = fn(content, filename)
                if table is not None:
                    return table
            except Exception:
                pass
        return _preview_json_basic(content, filename)

    # CSV
    def csv_wrapper(content: bytes, filename: str) -> object:
        return _preview_csv_basic(content, filename)

    registry.register_extension('json', json_wrapper)
    registry.register_mime('application/json', json_wrapper)
    registry.register_extension('csv', csv_wrapper)
    registry.register_mime('text/csv', csv_wrapper)
    return registry


