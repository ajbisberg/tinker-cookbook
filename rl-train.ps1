Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-UsablePython {
  param([string]$RepoRoot)

  $directCandidates = @(
    (Join-Path $RepoRoot ".venv\Scripts\python.exe"),
    "python"
  )

  $errors = @()

  foreach ($candidate in $directCandidates) {
    if (($candidate -ne "python") -and -not (Test-Path $candidate)) {
      continue
    }

    try {
      & $candidate -c "import sys; assert sys.version_info >= (3, 11), f'Python 3.11+ required, found {sys.version.split()[0]}'; import chz; import torch"
      if ($LASTEXITCODE -eq 0) {
        return [PSCustomObject]@{ Mode = "direct"; Command = $candidate }
      }
      $errors += "${candidate}: python preflight failed with exit code $LASTEXITCODE"
    }
    catch {
      $errors += "${candidate}: $($_.Exception.Message)"
    }
  }

  $condaCmd = Get-Command conda -ErrorAction SilentlyContinue
  if ($null -ne $condaCmd) {
    $condaEnv = if ($Env:TINKER_CONDA_ENV) { $Env:TINKER_CONDA_ENV } else { "tinker-cb" }
    & conda --no-plugins run -n $condaEnv python -c "import sys; assert sys.version_info >= (3, 11), f'Python 3.11+ required, found {sys.version.split()[0]}'; import chz; import torch"
    if ($LASTEXITCODE -eq 0) {
      return [PSCustomObject]@{ Mode = "conda"; EnvName = $condaEnv }
    }
    $errors += "conda env '${condaEnv}': python preflight failed with exit code $LASTEXITCODE"
  }

  throw "No usable Python interpreter found. Use Python 3.11+ and install dependencies with pip install -e . Set TINKER_CONDA_ENV to your env name if needed.`n$($errors -join "`n")"
}

Push-Location $PSScriptRoot
try {
  if (-not (Test-Path "api-key.txt")) {
    throw "Missing api-key.txt in $PSScriptRoot"
  }

  $pythonSpec = Get-UsablePython -RepoRoot $PSScriptRoot

  $Env:TINKER_API_KEY = (Get-Content -Raw "api-key.txt").Trim()
  $Env:KMP_DUPLICATE_LIB_OK = "TRUE"

  Write-Host "Running rl_basic"
  if ($pythonSpec.Mode -eq "conda") {
    Write-Host "Using conda env: $($pythonSpec.EnvName)"
    & conda --no-plugins run -n $pythonSpec.EnvName python -m tinker_cookbook.recipes.rl_basic
  }
  else {
    Write-Host "Using python: $($pythonSpec.Command)"
    & $pythonSpec.Command -m tinker_cookbook.recipes.rl_basic
  }
  if ($LASTEXITCODE -ne 0) {
    throw "rl_basic failed with exit code $LASTEXITCODE"
  }
}
finally {
  Pop-Location
}
