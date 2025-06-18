FROM nvidia/cuda:12.3.2-base-ubuntu22.04

RUN apt update && apt install -y python3 python3-pip git

WORKDIR /app

RUN pip install torch --index-url https://download.pytorch.org/whl/cu121
RUN pip install vllm

# CMD ["python3", "-m", "vllm.entrypoints.openai.api_server", \
#      "--model", "/app/vllm-model", \
#      "--dtype", "bfloat16", \
#      "--port", "8002", \
#      "--host", "0.0.0.0"]

CMD ["/bin/bash", "-c", "python3 -m vllm.entrypoints.openai.api_server \
     --model ${VLLM_MODEL_PATH} \
     --dtype bfloat16 \
     --port ${VLLM_PORT} \
     --host ${VLLM_HOST}"]

