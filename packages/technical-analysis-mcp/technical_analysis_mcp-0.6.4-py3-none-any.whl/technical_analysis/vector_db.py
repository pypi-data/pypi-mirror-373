import json
import logging
from openai import OpenAI, APITimeoutError, APIConnectionError, InternalServerError, NotFoundError
import requests
import os

api_key = os.getenv("OPENAI_API_KEY", "default_api_key")
token = os.getenv("HTTP_TOKEN", "default_token")


headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
        }
base_url = "https://milvus-db-stock-zfmfpoutfn.cn-hangzhou.fcapp.run"

import os



class VectorDB():
    """ A class that stores the vectors """

    def __init__(self, collection, col_for_index="title", anns_field = "vector"):
        self.collection = collection
        self.col_for_index = col_for_index
        self.anns_field = anns_field
        # 初始化 OpenAI 客户端
        self.openai = OpenAI(
                api_key=api_key,
                base_url="https://api.siliconflow.cn/v1"
            )
    
    def embedding(self, text )->list[float]:
        """计算字符串的Embedding"""
        try:
            
            # 调用 Embedding API
            response = self.openai.embeddings.create(
                model="BAAI/bge-m3",  # 使用的 Embedding 模型
                input=[text]          # 输入文本（支持批量）
            )
            
            # 提取 Embedding 向量
            if response.data and len(response.data) > 0:
                return response.data[0].embedding  # 返回第一个 Embedding
            else:
                raise ValueError("No embedding data returned from API")
                
        except (APITimeoutError, APIConnectionError, InternalServerError, NotFoundError) as e:
            # 重新抛出 API 错误
            raise e
        except Exception as e:
            # 捕获其他未知错误
            raise RuntimeError(f"Failed to generate embedding: {str(e)}")
    
    def make_index(self, data: list[dict]):

        records = []
        for item in data:
            vector = self.embedding(item[self.col_for_index])
            url = f"{base_url}/collections/{self.collection}/insert"
            item["id"] = hash(item[self.col_for_index])
            item[self.anns_field] = vector
            assert item["id"] != 0, f"每个向量ID必须为整数\n {item}"
            assert len(item[self.anns_field]) == 1024, "向量维度必须为 1024"
            assert all(isinstance(x, float) for x in item[self.anns_field]), "向量必须是 float"
            records.append(item)

        payload = json.dumps({
            "data": records
        })
        

        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()

    def retrieve(self, query, output_fields = ["id"], limit = 3):
        try:
            vector = self.embedding(query)
            res = requests.request("POST", f"{base_url}/collections/{self.collection}/search", headers=headers, 
                                    data=json.dumps({'anns_field': self.anns_field,'data':vector, 'output_fields': output_fields, 'limit': limit}))
            res = res.json()
            if res.get('success', True):
                return res.get('data', [])
            else:
                logging.error(res)
                return []
        except Exception as e:
            raise RuntimeError(f"Error in milvus: {e}")
        except Exception as e:
            raise e
        

