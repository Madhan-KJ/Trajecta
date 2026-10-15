$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][scriptblock]$Command
    )

    Write-Host "`n==> $Name"
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE"
    }
}

Invoke-Step "Install requirements" { python -m pip install -r requirements.txt }
Invoke-Step "Recreate synthetic experiments" { python recreate.py }
Invoke-Step "Download public benchmarks" { python download_benchmarks.py }
Invoke-Step "Run public benchmark experiments" { python run_benchmarks.py }
Invoke-Step "Generate figures and tables" { python generate_artifacts.py }

Write-Host "`nPipeline completed. See results/figures and results/tables."
