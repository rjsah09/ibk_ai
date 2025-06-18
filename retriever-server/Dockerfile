FROM python:3.12

# 시스템 종속성 설치
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# 패키지 설치
COPY ../requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 작업 디렉토리
WORKDIR /app

# 코드 복사
COPY ./modules /app/modules
COPY ./models /app/models
COPY ./server.py /app/server.py

# 모델 및 데이터 복사
# COPY ./embedding-model /app/embedding-model # 삭제
# COPY ./chroma /app/chroma
# COPY ./xlsx_files /app/xlsx_files

# 실행 명령
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8003"]
