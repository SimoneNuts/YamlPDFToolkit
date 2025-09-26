#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Converti tutti gli OpenAPI YAML/JSON in PDF (Windows-friendly).
Pipeline: YAML/JSON --(ReDoc via redoc-cli)--> HTML --(Chrome/Edge headless o wkhtmltopdf)--> PDF
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ------------------------- utils ------------------------- #

def which_many(candidates):
    for c in candidates:
        p = shutil.which(c)
        if p:
            return p
    return None


def find_chrome(explicit: str | None = None) -> str | None:
    if explicit and Path(explicit).exists():
        return explicit
    bins = [
        r"chrome.exe", r"msedge.exe",
        r"google-chrome", r"chromium", r"chromium-browser", r"msedge",
    ]
    p = which_many(bins)
    if p:
        return p
    if os.name == "nt":
        guesses = [
            r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            r"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
            r"C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
        ]
        for g in guesses:
            if Path(g).is_file():
                return g
    return None


def find_wkhtml(explicit: str | None = None) -> str | None:
    if explicit and Path(explicit).exists():
        return explicit
    return which_many(["wkhtmltopdf.exe", "wkhtmltopdf"]) 


def find_npx_and_redoc():
    npx_bin = which_many(["npx.cmd", "npx"])    
    redoc_bin = which_many(["redoc-cli.cmd", "redoc-cli"]) 
    if os.name == "nt":
        appdata = os.environ.get("AppData", r"C:\\Users\\%USERNAME%\\AppData\\Roaming")
        guesses = [
            rf"{appdata}\\npm\\npx.cmd",
            rf"{appdata}\\npm\\redoc-cli.cmd",
        ]
        for g in guesses:
            if Path(g).is_file():
                if g.endswith("npx.cmd") and not npx_bin:
                    npx_bin = g
                if g.endswith("redoc-cli.cmd") and not redoc_bin:
                    redoc_bin = g
    return npx_bin, redoc_bin


def run(cmd, cwd=None):
    try:
        subprocess.run(cmd, cwd=cwd, check=True)
    except FileNotFoundError:
        print(f"❌ Eseguibile non trovato: {cmd[0]}", file=sys.stderr)
        sys.exit(127)
    except subprocess.CalledProcessError as e:
        print(f"❌ Comando fallito: {' '.join(map(str, cmd))}", file=sys.stderr)
        sys.exit(e.returncode)


# ------------------------- converters ------------------------- #

def build_html_with_redoc(spec_path: Path, out_html: Path, npx_path: str | None, redoc_path: str | None, redoc_args: list[str] | None):
    args = redoc_args or []
    if npx_path:
        cmd = [npx_path, "--yes", "redoc-cli", "bundle", str(spec_path), "-o", str(out_html), *args]
        run(cmd)
        return
    if redoc_path:
        cmd = [redoc_path, "bundle", str(spec_path), "-o", str(out_html), *args]
        run(cmd)
        return
    print("❌ Né 'npx' né 'redoc-cli' trovati. Installa Node LTS (include npx) oppure `npm i -g redoc-cli`.", file=sys.stderr)
    sys.exit(1)


def chrome_to_pdf(chrome_bin, in_html: Path, out_pdf: Path, landscape=False):
    cmd = [
        chrome_bin, "--headless=new", "--disable-gpu",
        f"--print-to-pdf={out_pdf}",
        "--print-to-pdf-no-header",
        "--virtual-time-budget=20000",
        str(in_html.resolve().as_uri()),
    ]
    if landscape:
        cmd.append("--landscape")
    run(cmd)


def wkhtml_to_pdf(wk_bin, in_html: Path, out_pdf: Path, landscape=False, margin="12mm"):
    cmd = [
        wk_bin, "--print-media-type", "--enable-local-file-access",
        "--margin-top", margin, "--margin-right", margin,
        "--margin-bottom", margin, "--margin-left", margin,
        str(in_html), str(out_pdf)
    ]
    if landscape:
        cmd[1:1] = ["--orientation", "Landscape"]
    run(cmd)


# ------------------------- main ------------------------- #

def main():
    p = argparse.ArgumentParser(description="Converti OpenAPI YAML/JSON in PDF (batch)")
    p.add_argument("--src", required=True, help="Cartella sorgente con .yaml/.yml/.json")
    p.add_argument("--out", default="./pdf", help="Cartella output PDF (default: ./pdf)")
    p.add_argument("--landscape", action="store_true", help="PDF orizzontale")
    p.add_argument("--margin", default="12mm", help="Margini (solo wkhtmltopdf) default: 12mm")
    p.add_argument("--recursive", action="store_true", help="Cerca ricorsivamente nelle sottocartelle")
    p.add_argument("--keep-html", action="store_true", help="Mantieni gli HTML generati accanto ai PDF")
    p.add_argument("--chrome-path", default=None, help="Percorso esplicito di Chrome/Edge/Chromium")
    p.add_argument("--wkhtml-path", default=None, help="Percorso esplicito di wkhtmltopdf")
    p.add_argument("--redoc-args", default=None, help="Argomenti extra da passare a redoc-cli (stringa intera)")
    args = p.parse_args()

    src_dir = Path(args.src).resolve()
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    npx_bin, redoc_bin = find_npx_and_redoc()
    chrome_bin = find_chrome(args.chrome_path)
    wkhtml_bin = find_wkhtml(args.wkhtml_path)

    if not chrome_bin and not wkhtml_bin:
        print("⚠️  Né Chrome/Chromium (headless) né wkhtmltopdf trovati. Installane uno per proseguire.", file=sys.stderr)
        if os.name == "nt":
            print("   - Consigliato: winget install -e --id Google.Chrome", file=sys.stderr)
        print("   - In alternativa: winget/brew/apt install wkhtmltopdf", file=sys.stderr)
        sys.exit(1)

    patterns = ["*.yaml", "*.yml", "*.json"]
    if args.recursive:
        specs = []
        for pat in patterns:
            specs += list(src_dir.rglob(pat))
    else:
        specs = []
        for pat in patterns:
            specs += list(src_dir.glob(pat))
    specs = sorted({p.resolve() for p in specs})

    if not specs:
        print(f"❌ Nessun .yaml/.yml/.json trovato in: {src_dir}", file=sys.stderr)
        sys.exit(1)

    redoc_extra = args.redoc_args.split() if args.redoc_args else None

    with tempfile.TemporaryDirectory(prefix="redoc_html_") as tmpdir:
        tmpdir = Path(tmpdir)
        for spec in specs:
            name = spec.stem
            html_tmp = tmpdir / f"{name}.html"
            pdf_path = out_dir / f"{name}.pdf"
            html_out = (out_dir / f"{name}.html") if args.keep_html else html_tmp

            print(f"\n📦 [{name}] Bundling con ReDoc…")
            build_html_with_redoc(spec, html_tmp, npx_bin, redoc_bin, redoc_extra)

            if args.keep_html and html_tmp != html_out:
                try:
                    html_out.write_bytes(html_tmp.read_bytes())
                except Exception as e:
                    print(f"⚠️  Impossibile salvare HTML per {name}: {e}")

            print(f"🖨️  [{name}] HTML → PDF …")
            if chrome_bin:
                try:
                    chrome_to_pdf(chrome_bin, html_tmp, pdf_path, landscape=args.landscape)
                except subprocess.CalledProcessError:
                    if wkhtml_bin:
                        print(f"⚠️  Chrome headless non riuscito. Provo wkhtmltopdf per {name}…")
                        wkhtml_to_pdf(wkhtml_bin, html_tmp, pdf_path, landscape=args.landscape, margin=args.margin)
                    else:
                        raise
            else:
                wkhtml_to_pdf(wkhtml_bin, html_tmp, pdf_path, landscape=args.landscape, margin=args.margin)

            print(f"✅  [{name}] creato: {pdf_path}")

    print(f"\n🎉 Completato! PDF disponibili in: {out_dir}")

if __name__ == "__main__":
    main()