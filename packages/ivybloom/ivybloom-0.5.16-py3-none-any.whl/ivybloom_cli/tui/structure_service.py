from __future__ import annotations

from typing import List, Tuple
import math


class StructureService:
	"""ASCII protein structure projection/animation utils."""

	def parse_pdb_ca(self, pdb_text: str) -> List[Tuple[float, float, float]]:
		points: List[Tuple[float, float, float]] = []
		for line in pdb_text.splitlines():
			if not line.startswith("ATOM"):
				continue
			name = line[12:16].strip()
			if name != 'CA':
				continue
			try:
				x = float(line[30:38].strip())
				y = float(line[38:46].strip())
				z = float(line[46:54].strip())
				points.append((x, y, z))
			except Exception:
				continue
		if not points:
			return []
		cx = sum(p[0] for p in points) / len(points)
		cy = sum(p[1] for p in points) / len(points)
		cz = sum(p[2] for p in points) / len(points)
		centered = [(p[0]-cx, p[1]-cy, p[2]-cz) for p in points]
		max_r = max(math.sqrt(px*px+py*py+pz*pz) for px,py,pz in centered) or 1.0
		scale = 1.0 / max_r
		return [(px*scale, py*scale, pz*scale) for px,py,pz in centered]

	def render_ascii(self, points: List[Tuple[float, float, float]], angle: float, rows: int = 30, cols: int = 80) -> str:
		if not points:
			return "No structure loaded"
		ca = math.cos(angle)
		sa = math.sin(angle)
		cb = math.cos(angle*0.5)
		sb = math.sin(angle*0.5)
		grid = [[" "]*cols for _ in range(rows)]
		charset = ".:*oO#@"
		step = max(1, len(points)//1500 or 1)
		for x,y,z in points[::step]:
			x1 = ca*x + sa*z
			z1 = -sa*x + ca*z
			y1 = cb*y - sb*z1
			z2 = sb*y + cb*z1
			u = int((x1*0.5 + 0.5) * (cols-1))
			v = int((y1*0.5 + 0.5) * (rows-1))
			if 0 <= v < rows and 0 <= u < cols:
				depth = (z2*0.5 + 0.5)
				ch = charset[min(len(charset)-1, max(0, int(depth*len(charset))))]
				grid[v][u] = ch
		return "\n".join("".join(r) for r in grid)

	def render_frame_advance(self, points: List[Tuple[float, float, float]], prev_angle: float, rows: int = 30, cols: int = 80, delta: float = 0.12) -> Tuple[str, float]:
		"""Render a frame and advance angle; returns (ascii_art, new_angle)."""
		art = self.render_ascii(points, prev_angle, rows=rows, cols=cols)
		return art, prev_angle + delta


