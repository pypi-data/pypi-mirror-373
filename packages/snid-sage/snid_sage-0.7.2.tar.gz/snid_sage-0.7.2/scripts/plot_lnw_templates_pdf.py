"""
plot_lnw_templates_pdf.py – create a multi-page PDF that visualises
all *.lnw* template spectra.

Each page corresponds to one template (i.e. one *.lnw file).  Within the
page every epoch is drawn on the common rebinned wavelength grid and
vertically offset so they do not overlap.  A legend lists the age (if
known) of each epoch.

Example usage (PowerShell):

    python scripts/plot_lnw_templates_pdf.py -i templates -o plots/lnw_templates_preview.pdf
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Tuple

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import cm

from snid_sage.snid.io import read_template

__all__ = ["main"]


def _prepare_epoch_data(t: dict) -> List[Tuple[float, np.ndarray]]:
    """Return list of (age, flux) pairs for each epoch in template dict."""
    flux_matrix = t.get("flux_matrix")
    if flux_matrix is None:
        flux_matrix = np.expand_dims(t["flux"], axis=0)
    ages = t.get("ages", [np.nan] * flux_matrix.shape[0])
    return [(float(ages[i]) if i < len(ages) else np.nan, flux_matrix[i]) for i in range(flux_matrix.shape[0])]


def _plot_template(fig_ax, wave: np.ndarray, epoch_data: List[Tuple[float, np.ndarray]]):
    """Draw epochs with vertical offsets on provided Axes."""
    ax = fig_ax
    epoch_data.sort(key=lambda tup: (np.isnan(tup[0]), tup[0]))
    n_epochs = len(epoch_data)

    # vertical spacing
    ptp = np.ptp(epoch_data[0][1]) if n_epochs else 1.0
    spacing = ptp * 1.4 if ptp > 0 else 1.0

    cmap = cm.get_cmap("viridis", n_epochs or 1)
    for idx, (age, flux) in enumerate(epoch_data):
        offset = idx * spacing
        label = f"age = {age:.1f}" if not np.isnan(age) else f"epoch {idx}"
        ax.plot(wave, flux + offset, lw=0.8, color=cmap(idx), label=label)

    ax.set_xlabel("Wavelength (Å)")
    ax.set_ylabel("Flux + offset")
    ax.legend(fontsize="small", ncol=2)


def generate_pdf(in_dir: Path, output_pdf: Path, max_templates: int | None = None):
    lnw_files = sorted(list(in_dir.glob("*.lnw")))
    if not lnw_files:
        print(f"No .lnw files found in {in_dir}")
        return

    print(f"Creating {output_pdf} with {len(lnw_files)} pages …")
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    with PdfPages(output_pdf) as pdf:
        for idx, path in enumerate(lnw_files):
            if max_templates is not None and idx >= max_templates:
                break
            try:
                t = read_template(str(path))
            except Exception as exc:
                print(f"⚠️  Skip {path.name}: {exc}")
                continue

            wave = t["wave"]  # linear Å values
            epoch_data = _prepare_epoch_data(t)

            fig, ax = plt.subplots(figsize=(11, 6))
            _plot_template(ax, wave, epoch_data)
            ax.set_title(f"{t['name']} – {path.name}")
            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

    print(f"✅ PDF written to {output_pdf}")


def main():
    parser = argparse.ArgumentParser(description="Multi-page PDF preview of *.lnw* templates")
    parser.add_argument("-i", "--input_dir", type=str, default="templates", help="Folder with *.lnw files")
    parser.add_argument("-o", "--output_pdf", type=str, default="lnw_templates_preview.pdf", help="Path to output PDF")
    parser.add_argument("--max_templates", type=int, default=None, help="Limit number of templates (for testing)")

    args = parser.parse_args()
    in_dir = Path(args.input_dir).expanduser().resolve()
    out_pdf = Path(args.output_pdf).expanduser().resolve()

    generate_pdf(in_dir, out_pdf, args.max_templates)


if __name__ == "__main__":
    main() 