# Changelog

All notable changes to SNID SAGE will be documented in this file.

## [0.7.0] - 2025-08-30

- New preprocessing: added Step 0 to automatically detect and correct obvious cosmic-ray hits before standard preprocessing.
- Batch mode plotting: fixed inconsistencies when only weak matches are found; summary lines and generated plots now reflect weak-match status consistently.

## [0.6.1] - 2025-01-27

- Bug fixes and improvements:
  - Improved error handling for template loading failures in .csv
  - Fixed ejecta shifting

## [0.6.0] - 2025-08-19

- BREAKING: CLI renamed `snid` → `sage`; GUI utilities → `snid-sage-lines` / `snid-sage-templates`. Docs and entry points updated. Migration: replace `snid` with `sage`; main `snid-sage` unchanged.

- Analysis and messaging improvements:
  - Distinguish “weak match” vs “no matches” in GUI/CLI; cluster “no valid clusters” logs downgraded to INFO.
  - GUI: clearer status and dialogs for weak/no-match; added suggestion to reduce overlap threshold (`lapmin`).
  - CLI: “No good matches” suggestions now include lowering `lapmin`.
  - Batch CLI: adds “(weak)” marker in per-spectrum lines and suppresses cluster warnings.

- Clustering/logging:
  - More precise INFO messages for “no matches above RLAP-CCC” and “no types for clustering”.
