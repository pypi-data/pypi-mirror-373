from __future__ import annotations

from typing import TypedDict, Optional, Any, Dict


class Job(TypedDict, total=False):
	job_id: str
	id: str
	tool_name: str
	job_type: str
	status: str
	job_title: str
	title: str
	project_id: str
	parameters: Dict[str, Any]
	request_params: Dict[str, Any]


class Artifact(TypedDict, total=False):
	artifact_type: str
	type: str
	filename: str
	file_size: str
	url: str
	presigned_url: str
	primary: bool

