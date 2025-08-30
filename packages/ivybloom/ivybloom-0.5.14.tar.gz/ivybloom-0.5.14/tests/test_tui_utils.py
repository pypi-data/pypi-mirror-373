from __future__ import annotations

from ivybloom_cli.tui.search import rank_commands
from ivybloom_cli.tui.structure_service import StructureService
from ivybloom_cli.tui.commands import artifacts_cmds, jobs_cmds


def test_rank_commands_basic():
	commands = [
		("refresh", "Refresh", "Reload jobs"),
		("open_external", "Open Artifact", "Open best artifact in browser"),
		("jobs_list", "Jobs: List", "List jobs with optional filters"),
	]
	res = rank_commands(commands, "jo li")
	assert res and res[0][0] == "jobs_list"
	# Empty query returns original list
	assert rank_commands(commands, "") == commands


def test_structure_frame_advances():
	service = StructureService()
	# Minimal two points to render something deterministic-ish
	points = [(0.0, 0.0, 0.0), (0.2, 0.2, 0.2)]
	art1, a1 = service.render_frame_advance(points, 0.0, rows=10, cols=20, delta=0.5)
	art2, a2 = service.render_frame_advance(points, a1, rows=10, cols=20, delta=0.5)
	assert a2 > a1
	assert isinstance(art1, str) and isinstance(art2, str)


class DummyRunner:
    def __init__(self, json_map=None, text_map=None):
        self.json_map = json_map or {}
        self.text_map = text_map or {}

    def run_cli_json(self, args, timeout=30, env_overrides=None):
        key = tuple(args)
        return self.json_map.get(key)

    def run_cli_text(self, args, timeout=60, input_text=None, env_overrides=None):
        key = tuple(args)
        return self.text_map.get(key, "")

    def run_cli_stream(self, args, input_text=None, env_overrides=None):
        # Simple deterministic stream
        for line in ["line1", "line2", "line3"]:
            yield line


def test_artifacts_best_and_primary_selection():
    job_id = "job_1"
    data = {
        "artifacts": [
            {"artifact_type": "csv", "url": "http://example/csv"},
            {"artifact_type": "pdb", "presigned_url": "http://example/pdb"},
            {"artifact_type": "zip", "url": "http://example/zip"},
        ]
    }
    jr = DummyRunner(json_map={
        ("jobs", "download", job_id, "--list-only", "--format", "json"): data
    })
    assert artifacts_cmds.pdb_url_for_job(jr, job_id) == "http://example/pdb"
    assert artifacts_cmds.primary_artifact_url(jr, job_id) == "http://example/pdb"
    assert artifacts_cmds.best_artifact_url(jr, job_id) == "http://example/pdb"


def test_jobs_status_streaming_and_text():
    job_id = "job_2"
    jr = DummyRunner(text_map={
        ("jobs", "status", job_id, "--format", "table"): "ok"
    })
    # non-follow
    res = jobs_cmds.status(jr, job_id, extra_flags=None)
    assert res == "ok"
    # follow
    lines = []
    res2 = jobs_cmds.status(jr, job_id, extra_flags="--follow", on_line=lambda s: lines.append(s))
    assert res2 is None
    assert lines == ["line1", "line2", "line3"]

