"""
API 客户端模块
~~~~~~~~~~~

提供了 API 客户端的核心实现。
"""

import hashlib
import hmac
import base64
import time
import requests
import json
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass
import pandas as pd

@dataclass
class APIConfig:
    """API配置类"""
    key: str
    app_id: str
    base_url: str = "https://openapi.gf.com.cn"

class GFAPIClient:
    """广发证券 API 客户端"""
    
    def __init__(self, config: APIConfig):
        """
        初始化客户端
        
        Args:
            config: API配置对象
        """
        self.config = config
        
    def _generate_signature(self, method: str, endpoint: str, body: str, timestamp: str) -> str:
        """
        生成API签名
        
        Args:
            method: HTTP方法
            endpoint: API端点
            body: 请求体
            timestamp: 时间戳
            
        Returns:
            签名字符串
        """
        message = f'{method}\n{endpoint}\n{body}\n{timestamp}'
        key_bytes = bytes(self.config.key, 'utf-8')
        message_bytes = bytes(message, 'utf-8')
        hmac_digest = hmac.new(key_bytes, message_bytes, hashlib.sha256).digest()
        signature = base64.b64encode(hmac_digest)
        return 'HMAC ' + signature.decode('utf-8')
    
    def _get_headers(self, endpoint: str, body: str) -> Dict[str, str]:
        """
        生成请求头
        
        Args:
            endpoint: API端点
            body: 请求体
            
        Returns:
            请求头字典
        """
        timestamp = str(int(time.time()))
        return {
            'Content-Type': 'application/json',
            'X-App-Id': self.config.app_id,
            'X-Timestamp': timestamp,
            'X-Signature': self._generate_signature('POST', endpoint, body, timestamp)
        }
    
    def query(self, 
              endpoint: str,
              conditions: List[str],
              fields: List[str],
              orderFields: Optional[List[str]] = None,
              page_size: int = 200,
              auto_paging: bool = True,
              return_dataframe: bool = True) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
        """
        查询数据
        
        Args:
            endpoint: API端点
            conditions: 查询条件列表
            fields: 返回字段列表
            orderFieds：排序条件
            page_size: 每页记录数
            auto_paging: 是否自动分页获取所有数据
            return_dataframe: 是否返回DataFrame格式
            
        Returns:
            查询结果，可以是DataFrame或字典列表
            
        Raises:
            requests.exceptions.RequestException: 当API请求失败时
        """
        all_results = []
        page_index = 1
        total_records = None
        
        if orderFields is None:
            orderFields = ["rec_id,desc"]
        
        while True:
            data = {
                "target_user_id": self.config.key,
                "target_client_id": self.config.app_id,
                "conditions": conditions,
                "fields": fields,
                "orderFields": orderFields,
                "pageindex": str(page_index),
                "pagesize": str(page_size),
                "asc": True
            }
            
            body = json.dumps(data)
            headers = self._get_headers(endpoint, body)
            url = self.config.base_url + endpoint
            
            try:
                response = requests.post(url, headers=headers, data=body)
                response.raise_for_status()
                result = response.json()
                
                if 'data' in result and result['data']:
                    current_page_data = result['data']
                    all_results.extend(current_page_data)
                
                if total_records is None:
                    if 'totalrecords' in result:
                        total_records = int(result['totalrecords'])
                    elif 'pagination' in result and 'total' in result['pagination']:
                        total_records = int(result['pagination']['total'])
                
                if not auto_paging or total_records is None:
                    break
                
                if len(all_results) >= total_records:
                    break
                
                page_index += 1
                time.sleep(0.5)  # 添加短暂延迟，避免请求过快
                
            except requests.exceptions.RequestException as e:
                print(f"API请求失败: {str(e)}")
                print(f"状态码: {response.status_code if 'response' in locals() else 'N/A'}")
                print(f"响应内容: {response.text if 'response' in locals() else 'N/A'}")
                raise
        
        print(f"获取数据 {len(all_results)} 条")
        if return_dataframe and all_results:
            return pd.DataFrame(all_results)
        return all_results
