import os

import requests
from dotenv import load_dotenv

load_dotenv("/isearch/aiAgent/.env", override=True)
address = os.getenv("address")
def store_key(key_name,key_value,user_name):
    """
        用户凭证存储
        key_name:凭证key
        key_value:凭证value
        user_name:用户名

    """
    # address = os.environ.get("address", "192.168.12.249")
    url = f"{address}/console/api/user_credentials"
    headers = {
        'Content-Type': 'application/json',  # 说明请求体是 JSON 格式
    }
    # 请求体的数据
    data = {
        'certificate_key': key_name,
        'certificate_value': encode(key_value),
        'user_name': user_name
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        return "failure"
    json = response.json()
    return json['certificate_key']

def get_key(key_name, user_name):
    """
        获取用户凭证
        key_name：凭证key
        user_name:用户名称
    """
    # address = os.environ.get("address", "192.168.12.249")
    url = f"{address}/console/api/user_credentials?certificate_key={key_name}&user_name={user_name}"
    response = requests.get(url)
    if response.status_code != 200:
        return "failure"
    json = response.json()

    return json['certificate_value']

def delete_key(key_name,user_name):
    """
        删除凭证
        key_name：凭证key
        user_name:用户名称
    """
    # address = os.environ.get("address", "192.168.12.249")
    url = f"{address}/console/api/user_credentials"
    headers = {
        'Content-Type': 'application/json',  # 说明请求体是 JSON 格式
    }
    # 请求体的数据
    data = {
        'certificate_key': key_name,
        'user_name': user_name
    }
    requests.delete(url, headers=headers, json=data)

def list(user_name):
    """
        获取所有凭证key
        user_name:用户名称
    """
    # address = os.environ.get("address", "192.168.12.249")
    url = f"{address}/console/api/user_credentials/list?user_name={user_name}"
    response = requests.get(url)
    if response.status_code != 200:
        return "failure"
    json = response.json()

    return json

def exist(key_name, user_name):
    """
        获取用户凭证
        key_name：凭证key
        user_name:用户名称
    """
    # address = os.environ.get("address", "192.168.12.249")
    url = f"{address}/console/api/user_credentials?certificate_key={key_name}&user_name={user_name}"
    response = requests.get(url)
    if response.status_code != 200:
        return False


    return True

def encode(certificate_value):
    """
        获取密钥
        key_name：凭证key
    """
    url = f"{address}/console/api/get_encode_credentials"
    headers = {
        'Content-Type': 'application/json',  # 说明请求体是 JSON 格式
    }
    # 请求体的数据
    data = {
        'certificate_value': certificate_value,
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        return "failure"
    json = response.json()
    return json['certificate_value']


if __name__ == '__main__':
    print(exist("ccc","zhouly@i-search.com.cn"))