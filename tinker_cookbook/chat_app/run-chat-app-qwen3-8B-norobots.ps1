$CookbookRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$Env:TINKER_API_KEY = (Get-Content -Raw (Join-Path $CookbookRoot "api-key.txt")).Trim()
$Env:KMP_DUPLICATE_LIB_OK = "TRUE"
$Env:PYTHONUTF8 = "1"
if (-not $Env:UV_PROJECT_ENVIRONMENT) {
  $Env:UV_PROJECT_ENVIRONMENT = Join-Path $Env:LOCALAPPDATA "uv-envs\tinker-cookbook"
}
$Env:UV_LINK_MODE = "copy"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

# Qwen3-8B after NoRobots SFT: last checkpoint (step 16) from
# tinker_cookbook\training_logs\sl_basic_NoRobots_qwen3-8B\checkpoints.jsonl
Push-Location $CookbookRoot
try {
  uv run python -m tinker_cookbook.chat_app.tinker_chat_cli `
    base_model=Qwen/Qwen3-8B `
    model_path=tinker://b23706a7-a964-5fd1-a5b7-b8484a3f5c58:train:0/sampler_weights/000016
}
finally {
  Pop-Location
}
