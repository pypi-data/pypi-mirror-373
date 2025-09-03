from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, List

from .protein_visualizer import ProteinVisualizer
from .artifact_visualizer import visualize_json, visualize_txt
from .accelerated_text import braille_minimap, chunked_update
from .smiles_visualizer import render_smiles_unicode, summarize_smiles


class DetailsController:
    """Own rendering of details panes and optimized visualization paths."""

    def __init__(self, app: Any) -> None:
        self.app = app
        self._last_viz_kind: Optional[str] = None
        self._last_viz_payload: Optional[Dict[str, Any]] = None

    def render_all(self, job: Dict[str, Any]) -> None:
        self.app._details_view.render_summary(job)
        self._render_manifest_fast(job)
        self.app._details_view.render_visualization_placeholder(job)
        self.app._details_view.render_artifacts(job)
        # Capture current job SMILES for later visualization
        try:
            self._current_job_smiles = None
            smiles_arr = None
            if isinstance(job.get('smiles'), list):
                smiles_arr = job.get('smiles')
            elif isinstance(job.get('input_smiles'), list):
                smiles_arr = job.get('input_smiles')
            if smiles_arr and len(smiles_arr) > 0:
                self._current_job_smiles = smiles_arr[0]
            else:
                self._current_job_smiles = job.get('smiles') or job.get('input_smiles')
        except Exception:
            self._current_job_smiles = None
        # Pre-visualization preview (image or ASCII summary) above tabs
        try:
            job_id = str(job.get('job_id') or job.get('id') or '').strip()
            panel = getattr(self.app.right_column, 'preview', None) if getattr(self.app, 'right_column', None) else None
            if not job_id or panel is None:
                raise RuntimeError("no job or preview panel")
            # Prefer image-like artifacts for preview
            art = self.app._artifacts.choose_artifact_by_ext(job_id, [".png", ".jpg", ".jpeg", ".svg"]) or \
                  self.app._artifacts.choose_artifact_by_ext(job_id, [".json"]) or \
                  self.app._artifacts.choose_artifact(job_id, selector=None)
            if not art or not isinstance(art, dict):
                # If job has smiles, show a small braille depiction preview
                try:
                    smiles = job.get('smiles') or job.get('input_smiles')
                    if smiles:
                        mini = render_smiles_unicode(str(smiles), width=40, height=6)
                        panel.update(mini)
                    else:
                        panel.update("")
                except Exception:
                    panel.update("")
                raise RuntimeError("no artifact for preview")
            url = str(art.get('presigned_url') or art.get('url') or '')
            fname = str(art.get('filename') or '')
            if not url:
                panel.update(f"{fname}")
                raise RuntimeError("no url")
            # Fetch small preview bytes with short timeout
            try:
                content = self.app._artifacts.fetch_bytes(url, timeout=6)
            except Exception:
                panel.update(f"{fname}")
                raise
            # For images: kitty inline if kitty/wezterm and small enough, else show tag
            caps = getattr(self.app, "_accel_caps", {}) or {}
            is_image = fname.lower().endswith((".png", ".jpg", ".jpeg"))
            if is_image and (caps.get("kitty") or caps.get("wezterm")) and len(content) < 300_000:
                # Kitty graphics protocol escape sequence
                import base64
                b64 = base64.b64encode(content).decode('ascii')
                # Place an inline marker and a very small note; many terminals render images out of band
                panel.update("[dim]image preview (inline)[/dim]")
                print(f"\033_Gf=100,t=f,a=T;{b64}\033\\", end="")
            else:
                # For JSON or text-like, render snippet with braille off; small inline summary only
                if fname.lower().endswith(".json"):
                    snippet = content.decode('utf-8', errors='ignore')[:1000]
                    panel.update(snippet + ("\n[dim](truncated)[/dim]" if len(content) > 1000 else ""))
                else:
                    panel.update(f"{fname}")
        except Exception:
            pass
        try:
            tabbed_content = self.app.query_one("TabbedContent")
            if tabbed_content:
                tabbed_content.active = "manifest"
        except Exception:
            pass

    def try_render_protein(self, pdb_text: str, filename: str) -> None:
        try:
            pv = ProteinVisualizer()
            vw, vh = self.app._compute_visualization_size()
            # Accelerated path selection
            caps = getattr(self.app, "_accel_caps", {}) or {}
            use_fast = bool(caps.get("unicode_heavy", True))
            use_truecolor = bool(caps.get("truecolor", False))
            if use_fast:
                ascii_art = pv.render_pdb_fast_unicode(pdb_text, width=vw, height=vh, filename_hint=filename, use_truecolor=use_truecolor)
                # Fallback if fast renderer failed
                if not ascii_art or ascii_art.startswith("Fast render failed"):
                    ascii_art = pv.render_pdb_as_text(pdb_text, width=vw, height=vh, filename_hint=filename)
            else:
                ascii_art = pv.render_pdb_as_text(pdb_text, width=vw, height=vh, filename_hint=filename)
            # Append SMILES summary if present for multimodal jobs
            try:
                smiles = getattr(self, "_current_job_smiles", None)
                if not smiles and hasattr(self.app, "selected_job") and isinstance(self.app.selected_job, dict):
                    smiles = self.app.selected_job.get("smiles") or self.app.selected_job.get("input_smiles")
                if smiles:
                    ascii_art = ascii_art + "\n\n" + summarize_smiles(str(smiles))
            except Exception:
                pass
            if self.app.details_visualization:
                legend = []
                try:
                    pairs = pv.chain_legend(pdb_text)
                    if pairs:
                        legend_lines = ["[dim]Chains:[/dim]"]
                        for cid, color in pairs[:10]:
                            legend_lines.append(f"[{color}]■[/] {cid}")
                        legend = ["", "\n".join(legend_lines)]
                except Exception:
                    pass
                self.app.details_visualization.update(f"[green]Protein Structure (ASCII)[/green]\n\n{ascii_art}" + ("\n\n" + legend[1] if legend else ""))
            self._last_viz_kind = "protein"
            self._last_viz_payload = {"pdb_text": pdb_text, "filename": filename}
        except Exception as e:
            if self.app.details_visualization:
                self.app.details_visualization.update(f"[red]Visualization failed:[/red]\n{self.app._format_error(e)}")

    def rerender_on_resize(self) -> None:
        try:
            if self._last_viz_kind == "protein" and self._last_viz_payload:
                pdb_text = self._last_viz_payload.get("pdb_text", "")
                filename = self._last_viz_payload.get("filename", "protein.pdb")
                if pdb_text and self.app.details_visualization:
                    pv = ProteinVisualizer()
                    vw, vh = self.app._compute_visualization_size()
                    caps = getattr(self.app, "_accel_caps", {}) or {}
                    use_fast = bool(caps.get("unicode_heavy", True))
                    use_truecolor = bool(caps.get("truecolor", False))
                    if use_fast:
                        ascii_art = pv.render_pdb_fast_unicode(pdb_text, width=vw, height=vh, filename_hint=filename, use_truecolor=use_truecolor)
                        if not ascii_art or ascii_art.startswith("Fast render failed"):
                            ascii_art = pv.render_pdb_as_text(pdb_text, width=vw, height=vh, filename_hint=filename)
                    else:
                        ascii_art = pv.render_pdb_as_text(pdb_text, width=vw, height=vh, filename_hint=filename)
                    self.app.details_visualization.update(f"[green]Protein Structure (ASCII)[/green]\n\n{ascii_art}")
        except Exception:
            pass

    # -------- Fast manifest rendering using chunked update and braille minimap --------
    def _render_manifest_fast(self, job: Dict[str, Any]) -> None:
        try:
            if not self.app.details_manifest:
                return
            # Build the same manifest text as before but without JSON pretty at the bottom if huge
            lines: List[str] = []
            job_id = job.get('job_id') or job.get('id')
            lines.append(f"[b]Job ID:[/b] {job_id}")
            lines.append(f"[b]Tool:[/b] {job.get('tool_name') or job.get('job_type')}")
            lines.append(f"[b]Status:[/b] {job.get('status')}")
            title = job.get('job_title') or job.get('title')
            if title:
                lines.append(f"[b]Title:[/b] {title}")
            project = job.get('project_id')
            if project:
                lines.append(f"[b]Project:[/b] {project}")
            created = job.get('created_at')
            if created:
                lines.append(f"[b]Created:[/b] {created}")
            completed = job.get('completed_at')
            if completed:
                lines.append(f"[b]Completed:[/b] {completed}")
            progress = job.get('progress_percent') or job.get('progress_percentage')
            if progress is not None:
                lines.append(f"[b]Progress:[/b] {progress}%")
            lines.append("")
            lines.append("[b]Complete Job Data (preview):[/b]")
            import json as _json
            try:
                job_json = _json.dumps(job, indent=2)
            except Exception:
                job_json = str(job)
            # Minimap first row to give a quick sense of size
            try:
                bw = 40
                bh = 3
                mini = braille_minimap(job_json, bw, bh)
                lines.append("[dim]Minimap:[/dim]")
                lines.append(mini)
                lines.append("")
            except Exception:
                pass
            header = "\n".join(lines) + "\n"
            # Chunk the heavy JSON append for speed
            content = header + job_json
            chunked_update(self.app, self.app.details_manifest, content, chunk_bytes=15000)
        except Exception:
            # Fallback to original renderer
            try:
                self.app._details_view.render_manifest(job)
            except Exception:
                pass


