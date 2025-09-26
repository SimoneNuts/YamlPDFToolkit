# OpenAPI YAML → PDF Toolkit
Convert any OpenAPI **YAML/JSON** into pretty **PDFs** via **ReDoc** → HTML → **Chrome headless**/**wkhtmltopdf**. Cross‑platform, Windows‑friendly, and Dockerable.


## ✨ Features
- ✅ Batch convert a folder of **.yaml/.yml/.json** (use `--recursive` for subfolders)
- ✅ Uses **npx redoc-cli** when present, or globally installed `redoc-cli`
- ✅ Falls back to **wkhtmltopdf** if Chrome/Edge headless fails
- ✅ Options: orientation, margins, keep HTML, custom ReDoc flags
- ✅ Clear preflight checks and Windows‑friendly paths
- ✅ Works on **Windows / macOS / Linux** or inside **Docker**


## 🚀 Quickstart
### Windows (PowerShell)
```pwsh
winget install -e --id Google.Chrome
winget install -e --id OpenJS.NodeJS.LTS # includes npx
winget install -e --id wkhtmltopdf.wkhtmltopdf # optional fallback
python .\openapi_to_pdf.py --src .\examples --out .\pdf --keep-html
```

### macOS / Linux
```pwsh
brew install --cask google-chrome || true
brew install node wkhtmltopdf || true
python ./openapi_to_pdf.py --src ./examples --out ./pdf --keep-html
```

### Docker (no local installs)
```pwsh
docker build -t openapi2pdf .
docker run --rm -v "$PWD:/work" openapi2pdf \
python /tool/openapi_to_pdf.py --src /work/examples --out /work/pdf --keep-html
```

### 🧠 CLI Usage
```pwsh
usage: openapi_to_pdf.py --src SRC [--out OUT] [--landscape]
[--margin MARGIN] [--recursive]
[--keep-html] [--chrome-path PATH]
[--wkhtml-path PATH] [--redoc-args "..."]

options:
--src Folder with .yaml/.yml/.json specs
--out Output folder for PDFs (default: ./pdf)
--landscape Horizontal page layout
--margin wkhtmltopdf margins (default: 12mm)
--recursive Recurse into subfolders
--keep-html Keep generated HTML next to PDFs
--chrome-path Explicit Chrome/Edge/Chromium path
--wkhtml-path Explicit wkhtmltopdf path
--redoc-args Extra args for redoc-cli bundle (e.g. "--disableGoogleFont")
```

### 🧪 Try it
```pwsh
python ./openapi_to_pdf.py --src ./examples --out ./pdf --keep-html
```

### ❓ FAQ

- **Chrome is required?** No. Will try **Edge/Chromium**; if none, uses **wkhtmltopdf**.
- **Pass ReDoc options?** Yes: `--redoc-args "--disableGoogleFont"`.
- **Subfolders?** Yes: `--recursive`.