$Env:TINKER_API_KEY = (Get-Content -Raw "..\..\api-key.txt").Trim()
$Env:KML_DUPLICATE_LIB_OK = "TRUE"
uv run python -m tinker_cookbook.chat_app.tinker_chat_cli `
  base_model=Qwen/Qwen3-30B-A3B