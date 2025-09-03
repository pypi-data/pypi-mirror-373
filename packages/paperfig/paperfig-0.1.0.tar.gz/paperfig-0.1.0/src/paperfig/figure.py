"""Generic figure orchestrator that reads a JSON spec and renders PDFs.

This module provides the Fig class, which:
- Loads a JSON file describing figures to produce.
- Delegates per-figure rendering to user-provided functions via a type map.
- Collects individual PDFs and concatenates them into a single figures.pdf.
- Supports composite "multi" figures arranged in a grid.

It does not implement model fitting or plotting details; instead it connects
JSON inputs to rendering callables supplied by the caller.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import importlib
import importlib.metadata

from pdfgridcat import concat_pdf_pages


Renderer = Callable[[str, Dict[str, Any], Any], Any]


class FigError(Exception):
    """Domain-specific errors for figure orchestration."""


class Fig:
    """Container and runner for figure creation based on a JSON specification."""

    def __init__(self, json_filename: str | Path):
        self._json_filename: Path = Path(json_filename).expanduser()
        self.pdf_filename: str = "figures.pdf"
        self.verbose: int = 1
        self._fig_dir: Path = Path(".")
        self.function: Dict[str, Renderer] = {}
        self.result: Dict[str, Any] = {}
        self._logger = self._make_logger()
        self._entry_point_renderers: Optional[Dict[str, Renderer]] = None
        self.load_json()

    @property
    def fig_dir(self) -> Path:
        return self._fig_dir

    @fig_dir.setter
    def fig_dir(self, value: Any) -> None:
        if isinstance(value, Path):
            self._fig_dir = value.expanduser()
        else:
            self._fig_dir = Path(str(value)).expanduser()

    @property
    def json_filename(self) -> Path:
        return self._json_filename

    def _make_logger(self) -> logging.Logger:
        logger = logging.getLogger(f"{__name__}.Fig")
        if not logger.handlers:
            handler = logging.StreamHandler()
            fmt = logging.Formatter("[%(levelname)s] %(message)s")
            handler.setFormatter(fmt)
            logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def _apply_verbose(self) -> None:
        if self.verbose <= 0:
            level = logging.WARNING
        elif self.verbose == 1:
            level = logging.INFO
        else:
            level = logging.DEBUG
        self._logger.setLevel(level)

    def load_json(self) -> None:
        if not self.json_filename.exists():
            raise FigError(f"JSON file does not exist: {self.json_filename}")
        try:
            with self.json_filename.open(encoding="utf-8") as f:
                self.list: Dict[str, Dict[str, Any]] = json.load(f)
        except json.JSONDecodeError as e:
            raise FigError(f"Failed to parse JSON: {self.json_filename}: {e}") from e
        self._validate_json()

    def save_json(self) -> None:
        try:
            with self.json_filename.open("w", encoding="utf-8") as f:
                json.dump(self.list, f, indent=2, ensure_ascii=False)
        except OSError as e:
            raise FigError(f"Failed to write JSON: {self.json_filename}: {e}") from e

    def _validate_json(self) -> None:
        if not isinstance(self.list, dict):
            raise FigError("Root of JSON must be an object mapping id -> figure spec.")
        for idx, node in self.list.items():
            if not isinstance(idx, str):
                raise FigError(f"Figure id must be a string, got: {idx!r}")
            if not isinstance(node, dict):
                raise FigError(f"Figure '{idx}' spec must be an object.")
            t = node.get("type")
            if not isinstance(t, str):
                raise FigError(f"Figure '{idx}' must have a string 'type' field.")
            if t == "multi":
                figs = node.get("figures")
                if not isinstance(figs, dict):
                    raise FigError(f"Figure '{idx}': multi requires 'figures' object.")
                for k, sub in figs.items():
                    if not isinstance(sub, dict):
                        raise FigError(f"Figure '{idx}': sub-figure '{k}' must be object.")
                    st = sub.get("type")
                    if not isinstance(st, str):
                        raise FigError(
                            f"Figure '{idx}': sub-figure '{k}' must have string 'type'."
                        )
                for key in ("row", "column"):
                    if key not in node:
                        raise FigError(f"Figure '{idx}': multi requires '{key}'.")

    def register(self, type_name: str, renderer: Renderer) -> None:
        self.function[type_name] = renderer

    def _load_entry_point_renderers(self) -> Dict[str, Renderer]:
        if self._entry_point_renderers is not None:
            return self._entry_point_renderers
        eps: Dict[str, Renderer] = {}
        try:
            for ep in importlib.metadata.entry_points(group="paperfig.renderers"):
                try:
                    func = ep.load()
                    if callable(func):
                        eps[ep.name] = func
                except Exception:
                    continue
        except Exception:
            pass
        self._entry_point_renderers = eps
        return eps

    def _resolve_renderer(self, type_name: str) -> Optional[Renderer]:
        if type_name in self.function:
            return self.function[type_name]
        eps = self._load_entry_point_renderers()
        if type_name in eps:
            return eps[type_name]
        if ":" in type_name:
            mod_name, func_name = type_name.split(":", 1)
            try:
                mod = importlib.import_module(mod_name)
                func = getattr(mod, func_name)
                if callable(func):
                    return func
            except Exception as e:
                raise FigError(f"Failed to import renderer '{type_name}': {e}") from e
        return None

    def create_pdf(self) -> None:
        self._apply_verbose()
        self.fig_dir = self.fig_dir  # normalize
        try:
            self.fig_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise FigError(f"Cannot create output directory: {self.fig_dir}: {e}") from e

        self.result = {}
        fig_files: list[Path] = []

        for index, data in self.list.items():
            t = data.get("type")
            if not isinstance(t, str):
                raise FigError(f"Figure '{index}' has invalid 'type': {t!r}")
            if t == "multi":
                result_multi = self.multi(index, data)
                for k, v in result_multi.items():
                    self.result[k] = v
                parent_pdf = self.fig_dir / f"fig{index}.pdf"
                if not parent_pdf.exists():
                    raise FigError(
                        f"Composite PDF not produced for '{index}': {parent_pdf}"
                    )
                fig_files.append(parent_pdf)
                continue

            renderer = self._resolve_renderer(t)
            if renderer is None:
                raise FigError(f"type '{t}' not defined/resolvable for figure '{index}'")

            self._logger.info(f"Rendering {index} (type={t})")
            try:
                self.result[index] = renderer(index, data, verbose=self.verbose)
            except TypeError:
                raise

            expected = self.fig_dir / f"fig{index}.pdf"
            if not expected.exists():
                raise FigError(
                    f"Renderer completed but expected file not found: {expected}"
                )
            fig_files.append(expected)

        if not fig_files:
            raise FigError("No figures were produced; nothing to concatenate.")

        out_file = self.fig_dir / self.pdf_filename
        self._logger.info(f"Concatenating {len(fig_files)} pages -> {out_file}")
        try:
            concat_pdf_pages(
                input_files=[str(p) for p in fig_files],
                output_file=str(out_file),
                col=1,
                row=1,
            )
        except Exception as e:
            raise FigError(f"Concatenation failed: {e}") from e

        if self.verbose > 0:
            self._logger.info(f"Finished creating {out_file}")

    def multi(self, parent_index: str, fig: Dict[str, Any]) -> Dict[str, Any]:
        figs = fig.get("figures")
        if not isinstance(figs, dict):
            raise FigError(f"Figure '{parent_index}': multi requires 'figures' object.")
        row = fig.get("row")
        col = fig.get("column")
        if not isinstance(row, int) or not isinstance(col, int):
            raise FigError(f"Figure '{parent_index}': 'row' and 'column' must be integers.")

        result: Dict[str, Any] = {}
        fig_files: list[Path] = []

        for index, data in figs.items():
            t = data.get("type")
            if not isinstance(t, str):
                raise FigError(f"Figure '{parent_index}': sub-figure '{index}' has invalid 'type'.")
            renderer = self._resolve_renderer(t)
            if renderer is None:
                raise FigError(f"type '{t}' not defined in multi() for '{index}'")
            self._logger.info(f"Rendering sub-figure {index} (type={t}) of {parent_index}")
            res = renderer(index, data, verbose=self.verbose)
            result[index] = res

            expected = self.fig_dir / f"fig{index}.pdf"
            if not expected.exists():
                raise FigError(
                    f"Sub-figure renderer completed but expected file not found: {expected}"
                )
            fig_files.append(expected)

        output_file = self.fig_dir / f"fig{parent_index}.pdf"
        try:
            concat_pdf_pages(
                input_files=[str(p) for p in fig_files],
                output_file=str(output_file),
                col=col,
                row=row,
            )
        except Exception as e:
            raise FigError(f"Concatenation for multi '{parent_index}' failed: {e}") from e

        return result
