$CookbookRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$Env:TINKER_API_KEY = (Get-Content -Raw (Join-Path $CookbookRoot "api-key.txt")).Trim()
$Env:KMP_DUPLICATE_LIB_OK = "TRUE"
$Env:PYTHONUTF8 = "1"
if (-not $Env:UV_PROJECT_ENVIRONMENT) {
  $Env:UV_PROJECT_ENVIRONMENT = Join-Path $Env:LOCALAPPDATA "uv-envs\tinker-cookbook"
}
$Env:UV_LINK_MODE = "copy"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

# Qwen3.5-9B-Base after NoRobots SFT: last checkpoint (step 40, after resume) from
# tinker_cookbook\training_logs\sl_basic_NoRobots_qwen3.5-9B-base\checkpoints.jsonl
Push-Location $CookbookRoot
try {
  uv run python -m tinker_cookbook.chat_app.tinker_chat_cli `
    base_model=Qwen/Qwen3.5-9B-Base `
    model_path=tinker://7beee836-4c9c-595f-88dc-389ebac96afc:train:0/sampler_weights/000040
}
finally {
  Pop-Location
}
