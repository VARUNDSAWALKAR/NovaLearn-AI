# Run from any working directory: project paths are anchored to this script.
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    Write-Host 'Creating Python 3.11 virtual environment...'
    py -3.11 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.11 is required. Check py -0p.' }
}
$py = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
& $py -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
& $py -m streamlit run app.py
