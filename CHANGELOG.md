# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Core Modular Architecture**: Reorganized into `core` and `gui` packages to prepare for future Web App deployments.
- **Smart PDF Mapping**: Evaluator directly uses Option IDs natively embedded within the PDF text instead of forcing external Answer Key normalization.
- **Native PDF Annotations**: Evaluated outputs are saved natively as `_evaluated.pdf`.
- **Scorecard Drawer**: Added an overall performance scorecard annotated onto the top right corner of the first PDF page.
- **Question Markers**: Added visual `✅ Correct` / `❌ Incorrect` markers drawn 20 pixels directly above every Question ID in the evaluated PDF.
- **HTML Answer Key Support**: Direct ingestion of NTA portal Answer Keys saved as `.html`, including automatic layout stripping and generation of backup `.csv`s.

### Changed
- **Lightning Fast Extraction**: Replaced PyTesseract and pdf2image with `PyMuPDF`, increasing parsing speed by >100x and eliminating local dependencies like Poppler and Tesseract.
- **Separated Entry Points**: Dedicated `main.py` for CLI execution and `run_gui.py` for UI execution.
- **README Redux**: Refactored README instructions to reflect the vastly simplified installation process.

### Removed
- **Tesseract & Image Libraries**: Removed `pytesseract`, `pdf2image`, `opencv-python`, and `pillow` from dependencies.
- **Scraping Artifacts**: Removed throwaway normalization scripts and test files.
- **OCR Logic**: Extracted all legacy RegEx dependent on OCR inaccuracies.
