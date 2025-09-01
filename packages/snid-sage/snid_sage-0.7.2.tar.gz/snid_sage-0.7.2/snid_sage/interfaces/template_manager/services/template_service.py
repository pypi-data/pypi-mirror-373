"""
Template Service (HDF5-only)
============================

Centralized service for HDF5-only template storage and index management.

Responsibilities:
- Manage a user-writable template library under `snid_sage/templates/User_templates/`
- Append templates to per-type HDF5 files (rebinned to the standard grid)
- Maintain a user index (`template_index.user.json`) and merge with built-in index
- Provide a small API for the GUI (creator, browser, manager)

Notes:
- Legacy .lnw support is intentionally removed. All new templates are written
  directly to HDF5 and indexed.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import json
import threading
from importlib import resources

import numpy as np
import h5py


def _compute_builtin_dir() -> Path:
    """Resolve the packaged templates directory robustly (installed or dev)."""
    # Prefer importlib.resources traversal of the installed package
    try:
        with resources.as_file(resources.files('snid_sage') / 'templates') as tpl_dir:
            if tpl_dir.exists():
                return tpl_dir
    except Exception:
        pass
    # Fallback: use the repo-relative path for editable installs
    try:
        return Path(__file__).resolve().parents[3] / "templates"
    except Exception:
        return Path("snid_sage/templates").resolve()


_BUILTIN_DIR = _compute_builtin_dir()

# Determine a writable user templates directory. Prefer app config dir.
def _compute_user_dir() -> Path:
    # Try configuration manager location
    try:
        from snid_sage.shared.utils.config.configuration_manager import ConfigurationManager
        cfg = ConfigurationManager()
        user_dir = Path(cfg.config_dir) / "templates" / "User_templates"
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    except Exception:
        pass
    # Fallback to a subdir next to built-ins (may be read-only, so try/except)
    fallback = _BUILTIN_DIR / "User_templates"
    try:
        fallback.mkdir(parents=True, exist_ok=True)
    except Exception:
        # As a last resort, use home directory
        fallback = Path.home() / ".snid_sage" / "User_templates"
        fallback.mkdir(parents=True, exist_ok=True)
    return fallback


_USER_DIR = _compute_user_dir()
_USER_INDEX = _USER_DIR / "template_index.user.json"
_BUILTIN_INDEX = _BUILTIN_DIR / "template_index.json"


@dataclass
class StandardGrid:
    num_points: int = 1024
    min_wave: float = 2500.0
    max_wave: float = 10000.0

    @property
    def dlog(self) -> float:
        return float(np.log(self.max_wave / self.min_wave) / self.num_points)

    def wavelength(self) -> np.ndarray:
        # Same construction used by TemplateFFTStorage
        idx = np.arange(self.num_points) + 0.5
        return self.min_wave * np.exp(idx * self.dlog)


class TemplateService:
    """
    HDF5-only template service.

    Thread-safe for write operations via an internal lock.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        _USER_DIR.mkdir(parents=True, exist_ok=True)
        # Lazy cache
        self._standard_grid = StandardGrid()
        self._standard_wave = self._standard_grid.wavelength()

    # ---- Public API ----
    def get_merged_index(self) -> Dict[str, Any]:
        """Return the merged built-in + user index for the GUI browser."""
        builtin = self._read_json(_BUILTIN_INDEX) or {
            "templates": {},
            "by_type": {},
            "template_count": 0,
        }
        user = self._read_json(_USER_INDEX) or {
            "templates": {},
            "by_type": {},
            "template_count": 0,
        }

        merged_templates: Dict[str, Any] = {}
        merged_templates.update(builtin.get("templates", {}))
        merged_templates.update(user.get("templates", {}))

        # Recompute by_type from merged templates
        by_type: Dict[str, Any] = {}
        for name, meta in merged_templates.items():
            ttype = meta.get("type", "Unknown")
            bucket = by_type.setdefault(ttype, {"count": 0, "storage_file": meta.get("storage_file", ""), "template_names": []})
            bucket["count"] += 1
            bucket["template_names"].append(name)
            # Prefer an existing storage_file reference; do not overwrite with empty
            if not bucket.get("storage_file") and meta.get("storage_file"):
                bucket["storage_file"] = meta["storage_file"]

        return {
            "version": user.get("version") or builtin.get("version") or "2.0",
            "template_count": len(merged_templates),
            "templates": merged_templates,
            "by_type": by_type,
        }

    def add_template_from_arrays(
        self,
        *,
        name: str,
        ttype: str,
        subtype: str,
        age: float,
        redshift: float,
        phase: str,
        wave: np.ndarray,
        flux: np.ndarray,
    ) -> bool:
        """
        Append a template to the per-type user HDF5 and update the user index.
        Data are rebinned to the standard grid and FFT is precomputed.
        """
        if not isinstance(wave, np.ndarray) or not isinstance(flux, np.ndarray):
            return False
        if wave.size == 0 or flux.size == 0:
            return False
        try:
            with self._lock:
                h5_rel_path = self._ensure_user_h5_for_type(ttype)
                h5_abs_path = _BUILTIN_DIR / h5_rel_path

                # Rebin to the standard grid
                rebinned_flux = self._rebin_to_standard_grid(wave, flux)
                fft = np.fft.fft(rebinned_flux)

                # Write (append or create) to HDF5
                self._append_to_h5(
                    h5_abs_path,
                    name,
                    ttype,
                    subtype,
                    age,
                    redshift,
                    phase,
                    rebinned_flux,
                    fft,
                )

                # Update user index
                index = self._read_json(_USER_INDEX) or {
                    "version": "2.0",
                    "templates": {},
                    "by_type": {},
                    "template_count": 0,
                }
                index_templates = index.setdefault("templates", {})
                index_templates[name] = {
                    "type": ttype,
                    "subtype": subtype,
                    "age": float(age),
                    "redshift": float(redshift),
                    "phase": phase,
                    "epochs": 1,
                    "file_path": "",  # No LNW provenance
                    "storage_file": str(h5_rel_path).replace("\\", "/"),
                    "rebinned": True,
                }

                # Recompute by_type summary
                index["by_type"] = self._compute_by_type(index_templates)
                index["template_count"] = len(index_templates)

                self._write_json_atomic(_USER_INDEX, index)
            return True
        except Exception:
            return False

    def update_metadata(self, name: str, changes: Dict[str, Any]) -> bool:
        """Update metadata attributes for a user template and its index entry."""
        try:
            with self._lock:
                index = self._read_json(_USER_INDEX) or {}
                tmpl = (index.get("templates") or {}).get(name)
                if not tmpl:
                    return False  # only user templates can be edited
                storage_rel = Path(tmpl["storage_file"]) if tmpl.get("storage_file") else None
                if not storage_rel:
                    return False
                storage_abs = (_BUILTIN_DIR / storage_rel).resolve()
                if not storage_abs.exists():
                    return False
                # Update HDF5 attrs
                with h5py.File(storage_abs, "a") as f:
                    g = f["templates"].get(name)
                    if g is None:
                        return False
                    for k, v in changes.items():
                        if k in {"type", "subtype", "phase"} and isinstance(v, str):
                            g.attrs[k] = v
                        elif k in {"age", "redshift"}:
                            try:
                                g.attrs[k] = float(v)
                            except Exception:
                                pass
                # Update index entry
                for k in ["type", "subtype", "phase", "age", "redshift"]:
                    if k in changes:
                        tmpl[k] = changes[k]
                # Write back
                index["by_type"] = self._compute_by_type(index.get("templates", {}))
                self._write_json_atomic(_USER_INDEX, index)
            return True
        except Exception:
            return False

    def delete(self, name: str) -> bool:
        """Delete a user template group and its index entry."""
        try:
            with self._lock:
                index = self._read_json(_USER_INDEX) or {}
                templates = index.get("templates") or {}
                meta = templates.get(name)
                if not meta:
                    return False
                storage_rel = Path(meta.get("storage_file", ""))
                storage_abs = (_BUILTIN_DIR / storage_rel).resolve()
                if not storage_abs.exists():
                    return False
                with h5py.File(storage_abs, "a") as f:
                    tgroup = f["templates"]
                    if name in tgroup:
                        del tgroup[name]
                        try:
                            m = f["metadata"]
                            m.attrs["template_count"] = max(0, int(m.attrs.get("template_count", 1)) - 1)
                        except Exception:
                            pass
                # Remove from index
                templates.pop(name, None)
                index["by_type"] = self._compute_by_type(templates)
                index["template_count"] = len(templates)
                self._write_json_atomic(_USER_INDEX, index)
            return True
        except Exception:
            return False

    def rename(self, old_name: str, new_name: str) -> bool:
        """Rename a template. Built-in templates are copied into user HDF5 under the new name."""
        if not new_name or new_name == old_name:
            return False
        try:
            with self._lock:
                merged = self.get_merged_index()
                entry = (merged.get("templates") or {}).get(old_name)
                if not entry:
                    return False
                src_rel = Path(entry.get("storage_file", ""))
                src_abs = (_BUILTIN_DIR / src_rel).resolve()
                if not src_abs.exists():
                    return False
                # Read source datasets
                with h5py.File(src_abs, "r") as sf:
                    sg = sf["templates"].get(old_name)
                    if sg is None:
                        return False
                    flux = sg["flux"][:]
                    fft = (sg["fft_real"][:] + 1j * sg["fft_imag"][:])
                    attrs = dict(sg.attrs)
                # Write into user HDF5 (append)
                h5_rel = self._ensure_user_h5_for_type(attrs.get("type", "Unknown"))
                self._append_to_h5(_BUILTIN_DIR / h5_rel, new_name,
                                   attrs.get("type", "Unknown"), attrs.get("subtype", "Unknown"),
                                   float(attrs.get("age", 0.0)), float(attrs.get("redshift", 0.0)),
                                   attrs.get("phase", "Unknown"), flux, fft)
                # Update user index (add new entry, optionally delete old if it was user-owned)
                user_idx = self._read_json(_USER_INDEX) or {"version": "2.0", "templates": {}, "by_type": {}, "template_count": 0}
                user_idx["templates"][new_name] = {
                    "type": attrs.get("type", "Unknown"),
                    "subtype": attrs.get("subtype", "Unknown"),
                    "age": float(attrs.get("age", 0.0)),
                    "redshift": float(attrs.get("redshift", 0.0)),
                    "phase": attrs.get("phase", "Unknown"),
                    "epochs": int(attrs.get("epochs", 1)),
                    "file_path": "",
                    "storage_file": str(h5_rel).replace("\\", "/"),
                    "rebinned": True,
                }
                # If old was user-owned, remove its index entry and group
                old_user = (self._read_json(_USER_INDEX) or {}).get("templates", {}).get(old_name)
                if old_user and Path(old_user.get("storage_file", "")).exists():
                    try:
                        self.delete(old_name)
                    except Exception:
                        pass
                user_idx["by_type"] = self._compute_by_type(user_idx.get("templates", {}))
                user_idx["template_count"] = len(user_idx.get("templates", {}))
                self._write_json_atomic(_USER_INDEX, user_idx)
            return True
        except Exception:
            return False

    def duplicate(self, name: str, new_name: str) -> bool:
        """Duplicate a template to user HDF5 under a new name."""
        return self.rename(name, new_name)

    def rebuild_user_index(self) -> bool:
        """Re-scan user HDF5 files and rebuild the user index from scratch."""
        try:
            templates: Dict[str, Any] = {}
            for h5_path in (_USER_DIR.glob("templates_*.user.hdf5")):
                rel = h5_path.relative_to(_BUILTIN_DIR)
                with h5py.File(h5_path, "r") as f:
                    if "templates" not in f:
                        continue
                    tg = f["templates"]
                    for name in tg.keys():
                        g = tg[name]
                        attrs = dict(g.attrs)
                        templates[name] = {
                            "type": attrs.get("type", "Unknown"),
                            "subtype": attrs.get("subtype", "Unknown"),
                            "age": float(attrs.get("age", 0.0)),
                            "redshift": float(attrs.get("redshift", 0.0)),
                            "phase": attrs.get("phase", "Unknown"),
                            "epochs": int(attrs.get("epochs", 1)),
                            "file_path": "",
                            "storage_file": str(rel).replace("\\", "/"),
                            "rebinned": True,
                        }
            index = {
                "version": "2.0",
                "templates": templates,
                "by_type": self._compute_by_type(templates),
                "template_count": len(templates),
            }
            with self._lock:
                self._write_json_atomic(_USER_INDEX, index)
            return True
        except Exception:
            return False

    # ---- Internals ----
    def _rebin_to_standard_grid(self, wave: np.ndarray, flux: np.ndarray) -> np.ndarray:
        """Rebin flux onto the standard logarithmic grid by interpolation in log space."""
        # Guard inputs
        wave = np.asarray(wave, dtype=float)
        flux = np.asarray(flux, dtype=float)
        # Enforce strictly positive wavelengths
        mask = np.isfinite(wave) & np.isfinite(flux) & (wave > 0)
        wave, flux = wave[mask], flux[mask]
        if wave.size < 2:
            # Not enough data to interpolate; pad with median
            out = np.full(self._standard_wave.shape, np.median(flux) if flux.size else 0.0, dtype=float)
            return out
        # Interpolate flux in log-lambda domain
        logw = np.log(wave)
        target_logw = np.log(self._standard_wave)
        # Use linear interpolation in log space; out-of-bounds filled with nearest value
        rebinned = np.interp(target_logw, logw, flux, left=float(flux[0]), right=float(flux[-1]))
        # Normalize by median to emulate flattened spectra expectation
        med = float(np.median(rebinned)) if rebinned.size else 1.0
        if med != 0.0 and np.isfinite(med):
            rebinned = rebinned / med
        return rebinned.astype(float, copy=False)

    def _ensure_user_h5_for_type(self, ttype: str) -> Path:
        """Ensure the per-type user HDF5 exists; return path relative to built-in dir."""
        safe_type = ttype.replace("/", "_").replace("-", "_").replace(" ", "_")
        rel = Path("User_templates") / f"templates_{safe_type}.user.hdf5"
        abs_path = _BUILTIN_DIR / rel
        if not abs_path.exists():
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            with h5py.File(abs_path, "w") as f:
                meta = f.create_group("metadata")
                grid = self._standard_grid
                meta.attrs["version"] = "2.0"
                meta.attrs["created_date"] = float(np.floor(np.datetime64("now").astype("datetime64[s]").astype(int)))
                meta.attrs["template_count"] = 0
                meta.attrs["supernova_type"] = ttype
                meta.attrs["grid_rebinned"] = True
                meta.attrs["NW"] = grid.num_points
                meta.attrs["W0"] = grid.min_wave
                meta.attrs["W1"] = grid.max_wave
                meta.attrs["DWLOG"] = grid.dlog
                meta.create_dataset("standard_wavelength", data=self._standard_wave)
                f.create_group("templates")

            # NEW: Seed user library with all built-in templates for this type (one-time),
            # so that per-type override keeps the full set by default.
            try:
                builtin_h5 = _BUILTIN_DIR / f"templates_{safe_type}.hdf5"
                if builtin_h5.exists():
                    with h5py.File(builtin_h5, "r") as src, h5py.File(abs_path, "a") as dst:
                        if "templates" in src and "templates" in dst:
                            src_templates = src["templates"]
                            dst_templates = dst["templates"]
                            copied = 0
                            for name in src_templates.keys():
                                if name in dst_templates:
                                    continue
                                sg = src_templates[name]
                                dg = dst_templates.create_group(name)
                                # Copy datasets
                                dg.create_dataset("flux", data=sg["flux"][:])
                                dg.create_dataset("fft_real", data=sg["fft_real"][:])
                                dg.create_dataset("fft_imag", data=sg["fft_imag"][:])
                                # Copy attributes
                                for k, v in dict(sg.attrs).items():
                                    try:
                                        dg.attrs[k] = v
                                    except Exception:
                                        pass
                                # Ensure flags
                                dg.attrs["rebinned"] = True
                                if "epochs" not in dg.attrs:
                                    dg.attrs["epochs"] = 1
                                copied += 1
                            # Update count
                            try:
                                meta = dst["metadata"]
                                meta.attrs["template_count"] = int(meta.attrs.get("template_count", 0)) + int(copied)
                            except Exception:
                                pass

                    # Update user index with copied entries
                    index = self._read_json(_USER_INDEX) or {
                        "version": "2.0",
                        "templates": {},
                        "by_type": {},
                        "template_count": 0,
                    }
                    templates_idx = index.setdefault("templates", {})
                    # Read back from the destination to ensure attributes
                    with h5py.File(abs_path, "r") as f:
                        tg = f["templates"]
                        for name in tg.keys():
                            if name in templates_idx:
                                continue
                            g = tg[name]
                            attrs = dict(g.attrs)
                            templates_idx[name] = {
                                "type": attrs.get("type", ttype),
                                "subtype": attrs.get("subtype", "Unknown"),
                                "age": float(attrs.get("age", 0.0)),
                                "redshift": float(attrs.get("redshift", 0.0)),
                                "phase": attrs.get("phase", "Unknown"),
                                "epochs": int(attrs.get("epochs", 1)),
                                "file_path": "",
                                "storage_file": str(rel).replace("\\", "/"),
                                "rebinned": True,
                            }
                    index["by_type"] = self._compute_by_type(templates_idx)
                    index["template_count"] = len(templates_idx)
                    self._write_json_atomic(_USER_INDEX, index)
            except Exception:
                # Seeding is best-effort; ignore failures
                pass
        return rel

    def _append_to_h5(
        self,
        h5_path: Path,
        name: str,
        ttype: str,
        subtype: str,
        age: float,
        redshift: float,
        phase: str,
        flux: np.ndarray,
        fft: np.ndarray,
    ) -> None:
        # Handle name collision by suffixing
        final_name = name
        with h5py.File(h5_path, "a") as f:
            templates_group = f["templates"]
            suffix = 1
            while final_name in templates_group:
                final_name = f"{name}_{suffix}"
                suffix += 1
            g = templates_group.create_group(final_name)
            g.create_dataset("flux", data=flux)
            g.create_dataset("fft_real", data=np.asarray(fft.real))
            g.create_dataset("fft_imag", data=np.asarray(fft.imag))
            g.attrs["type"] = ttype
            g.attrs["subtype"] = subtype
            g.attrs["age"] = float(age)
            g.attrs["redshift"] = float(redshift)
            g.attrs["phase"] = phase
            g.attrs["epochs"] = 1
            g.attrs["file_path"] = ""  # no provenance .lnw
            g.attrs["rebinned"] = True
            # bump count
            meta = f["metadata"]
            try:
                meta.attrs["template_count"] = int(meta.attrs.get("template_count", 0)) + 1
            except Exception:
                meta.attrs["template_count"] = 1

    def _compute_by_type(self, templates: Dict[str, Any]) -> Dict[str, Any]:
        by_type: Dict[str, Any] = {}
        for name, meta in templates.items():
            ttype = meta.get("type", "Unknown")
            bucket = by_type.setdefault(ttype, {"count": 0, "storage_file": meta.get("storage_file", ""), "template_names": []})
            bucket["count"] += 1
            bucket["template_names"].append(name)
            if not bucket.get("storage_file") and meta.get("storage_file"):
                bucket["storage_file"] = meta["storage_file"]
        return by_type

    @staticmethod
    def _read_json(path: Path) -> Optional[Dict[str, Any]]:
        try:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            return None
        return None

    @staticmethod
    def _write_json_atomic(path: Path, data: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        tmp.replace(path)


# Global singleton
_template_service: Optional[TemplateService] = None


def get_template_service() -> TemplateService:
    global _template_service
    if _template_service is None:
        _template_service = TemplateService()
    return _template_service


