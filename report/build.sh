#!/usr/bin/env bash
# Build report/report.pdf from report.md (needs pandoc + a LaTeX engine); check it is <= 8 pages.
cd "$(dirname "$0")" && pandoc report.md -o report.pdf --pdf-engine=xelatex -V mainfont="DejaVu Serif" -V monofont="DejaVu Sans Mono" && pdfinfo report.pdf | grep Pages
