$CookbookRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$Env:TINKER_API_KEY = (Get-Content -Raw (Join-Path $CookbookRoot "api-key.txt")).Trim()
$Env:PYTHONUTF8 = "1"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

Push-Location $CookbookRoot
try {
  uv run python -m tinker_cookbook.chat_app.tinker_chat_cli `
    base_model=meta-llama/Llama-3.1-8B-Instruct
}
finally {
  Pop-Location
}
