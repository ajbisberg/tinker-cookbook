$Env:TINKER_API_KEY = (gc -Raw "..\..\api-key.txt").Trim()
python -m tinker_cookbook.chat_app.tinker_chat_cli `
  base_model=meta-llama/Llama-3.1-8B `
  model_path=tinker://2b17f030-08ae-5e2b-a212-eb43d780233d:train:0/sampler_weights/final
