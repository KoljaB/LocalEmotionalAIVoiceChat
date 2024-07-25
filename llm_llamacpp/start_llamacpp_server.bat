@echo off
cd /d %~dp0
set MODEL_PATH=model\openhermes-2.5-mistral-7b.Q5_K_M.gguf

call ..\venv\Scripts\activate.bat
python -m llama_cpp.server ^
--model "%MODEL_PATH%" ^
--n_ctx 2048 ^
--n_gpu_layers 25 ^
--n_threads 6 ^
--n_batch 512 ^
--seed 0 ^
--rope_freq_base 10000.0 ^
--rope_freq_scale 1.0 ^
--use_mmap True ^
--use_mlock False ^
--mul_mat_q True
cmd