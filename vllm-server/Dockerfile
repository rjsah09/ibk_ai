FROM nvidia/cuda:12.4-base-ubuntu22.04

RUN apt update && apt install -y python3 python3-pip git
RUN pip install torch --index-url https://download.pytorch.org/whl/cu121
RUN pip install vllm

WORKDIR /app

# CMD ["python3", "-m", "vllm.entrypoints.openai.api_server", \
#      "--model", "/app/vllm-model", \
#      "--dtype", "bfloat16", \
#      "--port", "8002", \
#      "--host", "0.0.0.0"]

CMD ["python3", "-m", "vllm.entrypoints.openai.api_server", \
     "--model", "${VLLM_MODEL_PATH}", \
     "--dtype", "bfloat16", \
     "--port", "${VLLM_PORT}", \
     "--host", "${VLLM_HOST}"]

