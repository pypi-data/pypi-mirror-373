from __future__ import annotations

from textual.widgets import DataTable, Static

from ivybloom_cli.tui.views import JobsView, DetailsView


class FakeJobsService:
	def __init__(self):
		self.calls = []

	def list_jobs(self, project_id, limit, offset):
		self.calls.append((project_id, limit, offset))
		# return predictable rows
		base = offset
		return [
			{"job_id": f"job-{base+1}", "tool_name": "esmfold", "status": "completed", "job_title": "t1"},
			{"job_id": f"job-{base+2}", "tool_name": "diffdock", "status": "running", "job_title": "t2"},
		]


class FakeArtifactsService:
	def list_artifacts_table(self, job_id: str):
		return f"ARTS:{job_id}"


def test_jobs_view_paging_and_selection():
	service = FakeJobsService()
	table = DataTable()
	view = JobsView(table, service)  # type: ignore[arg-type]
	view.limit = 2
	jobs = view.load_initial("proj-1")
	assert len(jobs) == 2 and jobs[0]["job_id"] == "job-1"
	more = view.load_more("proj-1")
	assert len(more) == 2 and more[0]["job_id"] == "job-3"
	# selection maps to internal list
	assert view.get_selected_job(1)["job_id"] == "job-2"


def test_details_view_renders():
	summary = Static()
	params = Static()
	arts = Static()
	arts_service = FakeArtifactsService()
	view = DetailsView(summary, params, arts, arts_service)
	job = {"job_id": "job-1", "tool_name": "esmfold", "status": "completed", "parameters": {"a": 1}}
	view.render_summary(job)
	assert "Job ID" in summary.renderable
	view.render_params(job)
	assert "\n" in params.renderable or "{" in params.renderable
	view.render_artifacts(job)
	assert "ARTS:job-1" in str(arts.renderable)

