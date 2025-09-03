from __future__ import annotations

from typing import Optional

from ..cli_runner import CLIRunner


def list_only_json(runner: CLIRunner, job_id: str) -> dict | None:
    return runner.run_cli_json(["jobs", "download", job_id, "--list-only", "--format", "json"]) or {}


def _extract_urls_from_data(data: dict) -> list[str]:
    urls: list[str] = []
    if not isinstance(data, dict):
        return urls
    artifacts = data.get("artifacts") or []
    for art in artifacts:
        if not isinstance(art, dict):
            continue
        url = art.get("presigned_url") or art.get("url")
        if isinstance(url, str) and url.startswith("http"):
            urls.append(url)
    # Fallback: scan other string fields
    for val in data.values():
        if isinstance(val, str) and val.startswith("http"):
            urls.append(val)
        elif isinstance(val, list):
            urls.extend([v for v in val if isinstance(v, str) and v.startswith("http")])
    return urls


def best_artifact_url(runner: CLIRunner, job_id: str) -> Optional[str]:
    data = list_only_json(runner, job_id) or {}
    if not isinstance(data, dict):
        return None
    artifacts = data.get("artifacts") or []
    # Prefer pdb, sdf, primary, json, zip (include JSON so BLAST/ValidationMonitor open works)
    preferred_types = ("pdb", "sdf", "primary", "json", "zip")
    for pref in preferred_types:
        for a in artifacts or []:
            if not isinstance(a, dict):
                continue
            aType = str(a.get("artifact_type") or a.get("type") or "").lower()
            if pref in aType:
                url = a.get("presigned_url") or a.get("url")
                if isinstance(url, str) and url.startswith("http"):
                    return url
    # Fallback: any URL
    urls = _extract_urls_from_data(data)
    return urls[0] if urls else None


def primary_artifact_url(runner: CLIRunner, job_id: str) -> Optional[str]:
    data = list_only_json(runner, job_id) or {}
    if not isinstance(data, dict):
        return None
    artifacts = data.get("artifacts") or []
    if isinstance(artifacts, list):
        chosen = next((a for a in artifacts if isinstance(a, dict) and a.get("primary")), None)
        if chosen:
            url = chosen.get("presigned_url") or chosen.get("url")
            if isinstance(url, str) and url.startswith("http"):
                return url
    # Fallback: reuse best selection
    return best_artifact_url(runner, job_id)


def pdb_url_for_job(runner: CLIRunner, job_id: str) -> Optional[str]:
    data = list_only_json(runner, job_id) or {}
    if not isinstance(data, dict):
        return None
    arts = data.get("artifacts") if isinstance(data, dict) else []
    if isinstance(arts, list):
        for art in arts:
            if not isinstance(art, dict):
                continue
            aType = str(art.get("artifact_type") or art.get("type") or "").lower()
            if aType == "pdb" and (art.get("presigned_url") or art.get("url")):
                url = art.get("presigned_url") or art.get("url")
                if isinstance(url, str) and url.startswith("http"):
                    return url
    return None


