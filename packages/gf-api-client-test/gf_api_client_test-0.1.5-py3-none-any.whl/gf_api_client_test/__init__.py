"""
广发证券开放平台 API 客户端
~~~~~~~~~~~~~~~~~~~~~

一个用于访问广发证券开放平台 API 的 Python 客户端：

    >>> from gf_api_client import APIConfig, GFAPIClient
    >>> config = APIConfig(key='your-key', app_id='your-app-id')
    >>> client = GFAPIClient(config)
    >>> result = client.query(endpoint, conditions, fields)

:copyright: (c) 2024 by GF.
:license: MIT, see LICENSE for more details.
"""

from .client import APIConfig, GFAPIClient
from .conditions import Condition

__version__ = '0.1.5'
__all__ = ['APIConfig', 'GFAPIClient', 'Condition']
