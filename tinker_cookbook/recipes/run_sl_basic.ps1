Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Runs sl_basic (NoRobots SFT) in a uv-managed environment.
# The venv lives outside OneDrive so it isn't synced; override with UV_PROJECT_ENVIRONMENT.
# Extra arguments are forwarded as chz overrides, e.g.:
#   .\run_sl_basic.ps1 model_name=Qwen/Qwen3-8B learning_rate=1e-4

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
  throw "uv not found. Install it: powershell -c `"irm https://astral.sh/uv/install.ps1 | iex`""
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Push-Location $repoRoot
try {
  if (-not (Test-Path "api-key.txt")) {
    throw "Missing api-key.txt in $repoRoot"
  }

  if (-not $Env:UV_PROJECT_ENVIRONMENT) {
    $Env:UV_PROJECT_ENVIRONMENT = Join-Path $Env:LOCALAPPDATA "uv-envs\tinker-cookbook"
  }
  # OneDrive rejects the hardlinks uv uses by default.
  $Env:UV_LINK_MODE = "copy"
  $Env:TINKER_API_KEY = (Get-Content -Raw "api-key.txt").Trim()
  $Env:KMP_DUPLICATE_LIB_OK = "TRUE"

  Write-Host "Using uv env: $Env:UV_PROJECT_ENVIRONMENT"
  & uv sync --python 3.12
  if ($LASTEXITCODE -ne 0) {
    throw "uv sync failed with exit code $LASTEXITCODE"
  }

  Write-Host "Running sl_basic"
  & uv run python -m tinker_cookbook.recipes.sl_basic @args
  if ($LASTEXITCODE -ne 0) {
    throw "sl_basic failed with exit code $LASTEXITCODE"
  }
}
finally {
  Pop-Location
}
