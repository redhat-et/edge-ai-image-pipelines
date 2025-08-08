source /app/bin/activate
uv pip install openai requests
python3 /share/wait-for-vllm.py
python3 /share/vllm-client.py
