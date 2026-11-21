HPV vaccine acceptance thesis (LaTeX)
Build: pdflatex main && bibtex main && pdflatex main && pdflatex main
Edit: config.tex (name, ID, supervisor, month). Set \showconfirm to 0 in config.tex to hide red [confirm: ...] flags.
Place university logo at figures/logo.png.
Regenerate: python3 scripts/build_tables.py ; python3 scripts/make_figures.py (needs the xlsx path in scripts/prep.py)
Ethics approval: appendices.tex (Appendix B placeholder).
