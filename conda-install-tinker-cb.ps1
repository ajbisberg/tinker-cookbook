conda create -n tinker-cb -c conda-forge -c pytorch -c nvidia python=3.11 pytorch numpy pillow pip -y; conda activate tinker-cb; pip install --no-deps -e .; pip install tinker-cookbook
