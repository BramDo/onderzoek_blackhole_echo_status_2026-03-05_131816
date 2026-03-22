# Paper Draft

Files:

- `main.tex`
- `references.bib`

Compile from this directory with:

```powershell
./build-paper.ps1
```

Equivalent manual sequence:

```powershell
pdflatex -interaction=nonstopmode -output-directory=build main.tex
bibtex build/main
pdflatex -interaction=nonstopmode -output-directory=build main.tex
pdflatex -interaction=nonstopmode -output-directory=build main.tex
```

The verified PDF path is:

- `build/main.pdf`

The main figure is stored locally in this directory as:

- `signal_above_noise_scale_plot_2026-03-21.png`
- `signal_above_noise_scale_plot_2026-03-21.pdf`

This draft is intentionally claim-disciplined:

- strong subset-proxy continuity through q80
- exploratory full-register q80 bonus wording
- no full-q80 OLE closure claim
