from __future__ import annotations

import sys
import json
from typing import Any


def emit_json(data: Any) -> None:
	"""Write pretty-printed JSON to stdout without any styling or extra text.

	This bypasses Rich to avoid markup or color codes contaminating machine output.
	"""
	try:
		text = json.dumps(data, indent=2, ensure_ascii=False)
	except Exception:
		# As a last resort, stringify the object
		text = json.dumps(str(data))
	sys.stdout.write(text + "\n")
	sys.stdout.flush()


