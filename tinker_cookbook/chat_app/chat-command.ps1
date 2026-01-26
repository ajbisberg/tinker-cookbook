$Env:TINKER_API_KEY = (Get-Content -Raw "api-key.txt").Trim()
$Env:KML_DUPLICATE_LIB_OK = "TRUE"
python -m tinker_cookbook.chat_app.tinker_chat_cli `
  base_model=moonshotai/Kimi-K2-Thinking
