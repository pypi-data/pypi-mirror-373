import base64
import json
import requests
from isrpa.Template_Exception import *


def OCR_frome_image_path(img_path, apiKey, secretKey, code_type=8000, option='vCode'):
    """
    执行OCR识别请求，将图片进行Base64编码并发送给OCR服务。

    - img_path: 图片文件路径
    - apiKey: API密钥
    - secretKey: Secret密钥
    - code_type: 验证码类型（如 字符验证码8000，滑块验证9000，点击验证9000）
    - result: OCR服务返回的结果中的 result 字段值
    """
    with open(img_path, 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        "code_type": code_type,
        "image": encoded_image,
        "apiKey": apiKey,
        "secretKey": secretKey,
    }

    # OCR 服务接口
    url = 'https://ai.i-search.com.cn/ocr/v2/'
    response = requests.post(url + option, json=payload, headers=headers)

    # 解析返回的 JSON 数据
    response_data = json.loads(response.text)

    # 返回 result 字段的值
    return response_data.get('result')


def OCR_from_image(img, apiKey, secretKey, code_type=8000, option='vCode'):
    """
    执行OCR识别请求，将图片进行Base64编码并发送给OCR服务。

    - img: 图片的二进制数据
    - apiKey: API密钥
    - secretKey: Secret密钥
    - code_type: 验证码类型（如 8000）
    - result: OCR服务返回的结果中的 result 字段值
    """
    encoded_image = base64.b64encode(img).decode('utf-8')
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        "code_type": code_type,
        "image": encoded_image,
        "apiKey": apiKey,
        "secretKey": secretKey,
    }

    # OCR 服务接口
    url = 'https://ai.i-search.com.cn/ocr/v2/'
    response = requests.post(url + option, json=payload, headers=headers)

    # 解析返回的 JSON 数据
    response_data = json.loads(response.text)
    try:
        result = response_data.get('result')
    except Exception:
        raise LoginFailed
    return result


if __name__ == '__main__':
    img_path = r'D:\Node_example\滑块验证码.png'
    apiKey = "aa9b5dc8a35c4f93a10fb53e3aebbb0b"
    secretKey = "eb50c22a83bd43daad6532722c8a921a"
    code_type = 9000
    result = OCR_frome_image_path(img_path, apiKey, secretKey, code_type)
    print(result)
