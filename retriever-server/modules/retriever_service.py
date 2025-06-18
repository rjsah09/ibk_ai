from .chroma_persistent import ChromaPersistent
import pandas as pd

class RetrieverService:
    def __init__(self, persist_directory: str="./chroma", embedding_model:str="intfloat/multilingual-e5-large"):
        self.persistent = ChromaPersistent(persist_directory=persist_directory, embedding_model=embedding_model)
    
    def index_xlsx(self, collection_name: str, file_path: str, sheet_name: str, keyword: dict, metadata: list):
        '''xlsx 파일 읽어 컬렉션 생성 및 인덱싱 (startup 시 실행)'''
        df_all = pd.read_excel(file_path, sheet_name=sheet_name, header=0)
        df_all.columns = df_all.columns.str.strip()
        columns_all = df_all.columns.tolist()

        keyword_index = list(keyword.values())[0]
        metadata_indices = [list(m.values())[0] for m in metadata]

        content_col = columns_all[keyword_index]
        metadata_cols = [columns_all[i] for i in metadata_indices]

        content_key = list(keyword.keys())[0]
        metadata_keys = [list(m.keys())[0] for m in metadata]

        df = df_all[[content_col] + metadata_cols]

        rows_as_dicts = df.to_dict(orient="records")
        documents_to_index = []

        for row in rows_as_dicts:
            content = str(row.get(content_col, ""))
            metadata_dict = {
                k: row.get(c, "") for k, c in zip(metadata_keys, metadata_cols)
            }

            doc = {
                "content": content,
                "metadata": metadata_dict
            }
            documents_to_index.append(doc)

        if collection_name not in self.persistent.get_collection_names():
            self.persistent.create_collection(collection_name)
            
        chunk_size = 1000
        for i in range(0, len(documents_to_index), chunk_size):
            chunk = documents_to_index[i:i + chunk_size]
            self.persistent.index(collection_name=collection_name, document=chunk)

    def delete_all_collections(self):
        '''컬렉션 초기화'''
        self.persistent.delete_all_collections()
    
    # ---------------------------------------- deprecated ------------------------------------------------- #
    def find_company_code(self, company_string: str) -> str:
        '''위탁사 탭. 위탁사명 -> 위탁사 코드'''
        return self.find_code_from_custody(collection_name="company", keyword=company_string, code_name="위탁사")
    
    def find_payment_method_code(self, payment_method_string: str) -> str:
        '''결제방식(자금) 탭. 결제방식명 -> 결제방식 코드'''
        return self.find_code_from_custody(collection_name="company", keyword=payment_method_string, code_name="결제방식")
         
    def find_fund_code(self, fund_string: str) -> str:
        '''펀드 탭. 펀드명 -> 펀드 코드'''
        return self.find_code_from_custody(collection_name="company", keyword=fund_string, code_name="펀드")
    
    def find_money_code(self, money_string: str) -> str:
        '''통화 탭. 통화명 -> 통화 코드 '''
        return self.find_code_from_custody(collection_name="company", keyword=money_string, code_name="통화")
    
    def match_by_etc_string(self, etc_string: str) -> tuple:
        '''PEF 파일. 회사명 -> Asset_kind, job_code'''
        retrieved = self.persistent.query(collection_name="etc", query_text=etc_string, k=5)
        
        if self.calculate_similarity(distance=retrieved[0]["distance"], alpha=3.0) >= 70.0:
            result = retrieved[0]["metadata"]
            asset_kind = result["asset_kind"]
            job_code = result["job_cd"]

            return (asset_kind, job_code)
        
        return ("", "")
    
    def match_by_limit_string(self, limit_string: str) -> list:
        '''PEF 파일. 회사명 -> Asset_kind, job_code'''
        retrieved = self.persistent.query(collection_name="limit", query_text=limit_string, k=1)
        
        result = []
        for item in retrieved:
            similarity = self.calculate_similarity(distance=item["distance"], alpha=1.0)
            if similarity >= 60.0:
                result.append({
                "item": item["content"],
                "limit_code": item["metadata"]["제한코드"],
                "limit_name": item["metadata"]["제한명"],
                "similarity": similarity
            })
                
        return result
    # ---------------------------------------- deprecated ------------------------------------------------- #
        
    def calculate_similarity(self, distance: float, alpha: float):
        '''코사인 거리 -> 유사도 변환'''
        scaled = (1.0 - (distance / 2.0)) ** alpha * 100.0
        return max(0.0, min(100.0, scaled))
    
    def find_from_custody(self, collection_name: str, keyword: str) -> list:
        '''컬렉션명, 쿼리 -> 질의 결과'''
        retrieved = self.persistent.query(collection_name=collection_name, query_text=keyword, k=5)
    
        result = []
        for item in retrieved:
            similarity = self.calculate_similarity(distance=item["distance"], alpha=2.0)
            if similarity >= 70.0:
                result.append({
                    "item": item["content"],
                    "code": item["metadata"],
                    "similarity": similarity
                })
    
        return result
    
    def find_top_from_custody(self, collection_name: str, keyword: str) -> dict:
        k_result = self.find_code_from_custody(collection_name=collection_name, keyword=keyword)
        
        if k_result:
            return k_result[0]
        
        return {}
    
    # deprecated #
    def find_code_from_custody(self, collection_name: str, keyword: str, code_name: str) -> str:
        '''컬렉션명, 쿼리, 코드명 -> 질의 결과(코드: str)'''
        result = self.find_from_custody(collection_name=collection_name, keyword=keyword)
        
        if result and "code" in result[0] and code_name in result[0]["code"]:
            return str(result[0]["code"][code_name])

        return ""
