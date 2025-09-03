# Changelog

All notable changes to SNID SAGE will be documented in this file.

## [0.7.3] - 2025-09-01

- Template corrections:
  - Fixed incorrect subtype classifications for several Type Ia templates:
    - `sn2005hk`: corrected from `Ia-pec` to `Ia-02cx`
    - `sn2008A`: corrected from `Ia-pec` to `Ia-02cx`
    - `sn2013gr`: corrected from `Ia-pec` to `Ia-02cx`
    - `sn2016ado`: corrected from `Ia-pec` to `Ia-02cx`
    - `sn2008ae`: corrected from `Ia-pec` to `Ia-02cx`
    - `ASASSN-15ga`: corrected from `Ia-pec` to `Ia-91bg`
    - `ASASSN-15hy`: corrected from `Ia-pec` to `Ia-03fg`


## [0.7.2] - 2025-09-01

- Bug fixes:
  - Fixed subtype display in CLI summary output when clustering fails and only 1-2 matches survive (weak match cases)

## [0.7.1] - 2025-09-01

- Bug fixes:
  - Fixed autoscaling issue in plot display within the advanced preprocessing interface
  - Fixed subtype fetching in batch summary when only a single match survives

## [0.7.0] - 2025-08-30

- New preprocessing: added Step 0 to automatically detect and correct obvious cosmic-ray hits before standard preprocessing.
- Batch mode plotting: fixed inconsistencies when only weak matches are found; summary lines and generated plots now reflect weak-match status consistently.

## [0.6.1] - 2025-08-20

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
