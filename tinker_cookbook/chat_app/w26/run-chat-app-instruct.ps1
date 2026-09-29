$Env:TINKER_API_KEY = (Get-Content -Raw "api-key.txt").Trim()
$Env:KML_DUPLICATE_LIB_OK = "TRUE"
python -m tinker_cookbook.chat_app.tinker_chat_cli `
  base_model=meta-llama/Llama-3.1-8B `
  model_path=tinker://92c308d4-09a8-566d-b33f-824d618e9aef:train:0/sampler_weights/final `
