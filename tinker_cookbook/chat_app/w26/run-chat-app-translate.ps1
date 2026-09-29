$Env:TINKER_API_KEY = (Get-Content -Raw "..\..\api-key.txt").Trim()
$Env:KML_DUPLICATE_LIB_OK = "TRUE"
python -m tinker_cookbook.chat_app.tinker_chat_cli `
  model_path=tinker://40aa1ba9-7a4d-5421-b420-947b01bf15d1:train:0/sampler_weights/final `
