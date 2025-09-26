param(
[string]$Src = "./examples",
[string]$Out = "./pdf"
)
python ./openapi_to_pdf.py --src $Src --out $Out --keep-html