from __future__ import annotations

from typing import List, Tuple


def rank_commands(commands: List[Tuple[str, str, str]], query: str, limit: int = 200) -> List[Tuple[str, str, str]]:
	"""Rank and filter (id, name, desc) by fuzzy subsequence score.

	Scoring favors name-startswith, contains, and subsequence hits across name+desc.
	Only items that are a subsequence match are returned, limited to `limit`.
	"""
	q = (query or "").strip().lower()
	if not q:
		return commands

	def score(item: Tuple[str, str, str]) -> int:
		_, name, desc = item
		text = (name + " " + (desc or "")).lower()
		# Subsequence match score
		i = 0
		hits = 0
		for ch in text:
			if i < len(q) and ch == q[i]:
				i += 1
				hits += 1
		starts = 10 if name.lower().startswith(q) else 0
		contains = 5 if q in text else 0
		return starts + contains + hits

	def is_subseq(item: Tuple[str, str, str]) -> bool:
		_, name, desc = item
		text = (name + " " + (desc or "")).lower()
		i = 0
		for ch in text:
			if i < len(q) and ch == q[i]:
				i += 1
		return i == len(q)

	ranked = sorted(commands, key=score, reverse=True)
	return [c for c in ranked if is_subseq(c)][:limit]


