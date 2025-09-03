import json

import requests
from requests.auth import HTTPBasicAuth

from k2magic.dataframe_db_exception import DataFrameDBException


def get(url, auth, tenant: str = None) -> json:
    headers = {}
    if tenant:
        headers = {'tenant': tenant}
        # K2A接口要求用完整用户名，即'租户名--用户名'的格式，这里自动适配这个要求
        if isinstance(auth, HTTPBasicAuth) and auth.username.find('--') == -1:
            new_username = f'{tenant}--{auth.username}'
            auth = HTTPBasicAuth(new_username, auth.password)

    response = requests.get(url, auth=auth, verify=False, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 400:
        raise DataFrameDBException(f"{response.status_code} 业务错误 {url}: {response.json().get('message')}")
    elif response.status_code == 401:
        raise DataFrameDBException(f"{response.status_code} 认证错误 {url}: {response.json().get('message')}")
    elif response.status_code == 403:
        raise DataFrameDBException(f"{response.status_code} 认证错误 {url}: {response.json().get('message')}")
    elif response.status_code == 500:
        raise DataFrameDBException(f"{response.status_code} 服务器内部错误 {url}")
    else:
        raise DataFrameDBException(f"{response.status_code} Failed to fetch from {url}")


def get_stream(url, auth, tenant: str = None):
    headers = {}
    if tenant:
        headers = {'tenant': tenant}
    response = requests.get(url, auth=auth, verify=False, headers=headers, stream=True)
    if response.status_code == 200:
        # response.raise_for_status()
        return response
    elif response.status_code == 400:
        raise DataFrameDBException(f"{response.status_code} 业务错误 {url}: {response.json().get('message')}")
    elif response.status_code == 401:
        raise DataFrameDBException(f"{response.status_code} 认证错误 {url}: {response.json().get('message')}")
    elif response.status_code == 403:
        raise DataFrameDBException(f"{response.status_code} 认证错误 {url}: {response.json().get('message')}")
    elif response.status_code == 500:
        raise DataFrameDBException(f"{response.status_code} 服务器内部错误 {url}")
    else:
        raise DataFrameDBException(f"{response.status_code} Failed to fetch from {url}")

