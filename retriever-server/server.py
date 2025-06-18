import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi import status
from modules.retriever_service import RetrieverService
from models.request_model import RequestModel
from models.code_response_model import CodeResponseModel
from models.etc_response_model import EtcResponseModel
from models.limit_response_model import LimitResponseModel

app = FastAPI()

VLLM_HOST = os.getenv("VLLM_HOST", "vllm_server")
VLLM_PORT = os.getenv("VLLM_PORT", "8002")
EMBEDDING_MODEL_PATH = os.getenv("EMBEDDING_MODEL_PATH", "/app/embedding-model")
CHROMA_DATA_PATH = os.getenv("CHROMA_DATA_PATH", "/app/chroma")
XLSX_FILES_PATH = os.getenv("XLSX_FILES_PATH", "/app/xlsx_files")

retriever = RetrieverService(persist_directory=CHROMA_DATA_PATH, embedding_model=CHROMA_DATA_PATH)

# Collection #
@app.on_event("startup")
def auto_create_collections():
    create_collections()

def create_collections():
    corsignor_file_path = os.path.join(XLSX_FILES_PATH, "corsignor.xlsx")
    etc_file_path = os.path.join(XLSX_FILES_PATH, "etc.xlsx")
    limit_file_path = os.path.join(XLSX_FILES_PATH, "limit.xlsx")

    try:
        retriever.delete_all_collections()
        retriever.index_xlsx("company", corsignor_file_path, "위탁사", {"위탁사명": 1}, [{"위탁사": 0}])
        retriever.index_xlsx("fund", corsignor_file_path, "펀드", {"펀드명": 1}, [{"펀드": 0}])
        retriever.index_xlsx("payment", corsignor_file_path, "결제방식(자금)", {"결제방식명": 1}, [{"결제방식": 0}])
        retriever.index_xlsx("money", corsignor_file_path, "통화", {"통화명": 1}, [{"통화": 0}])
        retriever.index_xlsx("etc", etc_file_path, "sheet1", {"content": 4}, [{"asset_kind": 5}, {"job_cd": 6}])
        retriever.index_xlsx("limit", limit_file_path, "Sheet1", {"해석": 3}, [{"제한코드": 1}, {"제한명": 2}])
        print("컬렉션 목록 생성 완료")
    except Exception as e:
        print(f"컬렉션 생성 중 에러 발생: {str(e)}")

# Query #
@app.post("/query/company", response_model=CodeResponseModel)
def find_company_code(data: RequestModel):
    return CodeResponseModel(code=retriever.find_company_code(data.query))

@app.post("/query/payment", response_model=CodeResponseModel)
def find_payment_code(data: RequestModel):
    return CodeResponseModel(code=retriever.find_payment_method_code(data.query))

@app.post("/query/fund", response_model=CodeResponseModel)
def find_fund_code(data: RequestModel):
    return CodeResponseModel(code=retriever.find_fund_code(data.query))

@app.post("/query/money", response_model=CodeResponseModel)
def find_money_code(data: RequestModel):
    return CodeResponseModel(code=retriever.find_money_code(data.query))

@app.post("/query/etc", response_model=EtcResponseModel)
def query_etc(data: RequestModel):
    asset_kind, job_code = retriever.match_by_etc_string(data.query)
    return EtcResponseModel(asset_kind=asset_kind, job_code=job_code)

@app.post("/query/limit", response_model=LimitResponseModel)
def query_limit(data: RequestModel):
    results = retriever.match_by_limit_string(data.query)
    return LimitResponseModel(limitations=results)

# Exception #
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "입력 값이 유효하지 않습니다."}
    )
    
@app.exception_handler(Exception)
async def internal_server_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요."}
    )