$CookbookRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$Env:TINKER_API_KEY = (Get-Content -Raw (Join-Path $CookbookRoot "api-key.txt")).Trim()
$Env:KMP_DUPLICATE_LIB_OK = "TRUE"
$Env:PYTHONUTF8 = "1"
if (-not $Env:UV_PROJECT_ENVIRONMENT) {
  $Env:UV_PROJECT_ENVIRONMENT = Join-Path $Env:LOCALAPPDATA "uv-envs\tinker-cookbook"
}
$Env:UV_LINK_MODE = "copy"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

# Vanilla Qwen3.5-9B-Base (pretrained only, no chat tuning), for comparison with the NoRobots SFT checkpoint.
Push-Location $CookbookRoot
try {
  uv run python -m tinker_cookbook.chat_app.tinker_chat_cli `
    base_model=Qwen/Qwen3.5-9B-Base
}
finally {
  Pop-Location
}
