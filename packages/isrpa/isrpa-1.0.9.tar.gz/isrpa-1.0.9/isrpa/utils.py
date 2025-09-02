import os

import redis
import requests
import tldextract
from dotenv import load_dotenv

load_dotenv("/isearch/aiAgent/.env", override=True)
address = os.getenv("address")
client = redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), db=os.getenv("REDIS_DB"),
                     password=os.getenv("REDIS_PASSWORD"))


def getPath(user_name):
    """
        环境变量设置
        windows
        setx address "192.168.12.249"

        linux
        export address = "192.168.12.249"
        source /etc/profile
    :param port:
    :return:
    """

    # address = os.environ.get("address", "192.168.12.249")

    url = f"{address}/client/getPath"
    headers = {
        'Content-Type': 'application/json',  # 说明请求体是 JSON 格式
    }
    # 请求体的数据
    data = {
        'user_name': user_name
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        return "failure"
    data = response.json()
    return f"ws://{data.get('ip_address')}:{data.get('port')}"


def get_ssh_path(user_name):
    """
        环境变量设置
        windows
        setx address "192.168.12.249"

        linux
        export address = "192.168.12.249"
        source /etc/profile
    :param port:
    :return:
    """
    url = f"{address}/client/getPath"
    headers = {'Content-Type': 'application/json'}
    data = {'user_name': user_name}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        return "failure"
    data = response.json()
    port = data.get('port')

    def get_ws_url():
        url = f"http://localhost:{port}/json/version"
        response = requests.get(url)
        if response.status_code != 200:
            return "failure"
        return response.json().get('webSocketDebuggerUrl')

    ws_url = get_ws_url()
    return ws_url


def get_active_url(user_name):
    """
    获取当前激活page对象
    """
    url = f"{address}/client/getPath"
    headers = {'Content-Type': 'application/json'}
    data = {'user_name': user_name}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        return "failure"
    data = response.json()
    port = data.get('port')

    def get_json():
        url = f"http://localhost:{port}/json"
        response = requests.get(url)
        if response.status_code != 200:
            return "failure"
        return response.json()

    pages = get_json()
    if pages:
        for page in pages:
            if (
                    page.get("url").startswith("chrome-extension://") or
                    page.get("url").startswith("chrome-untrusted://") or
                    page.get("title") == "MagicalAutomator-sidePanel"
            ):
                continue
            # else:
            #     if page.get("url") == "chrome://newtab/":
            #         return "chrome://new-tab-page/"
            return page.get("id")
    return None


def get_active_page(browser, active_page_id):
    """
    获取当前激活page对象
    """
    for page in browser.contexts[0].pages:
        client = page.context.new_cdp_session(page)
        target_info = client.send("Target.getTargetInfo")
        if target_info.get('targetInfo').get('targetId') == active_page_id:
            page.bring_to_front()
            return page


def set_playwright_file_path(key, value):
    client.set(key, value, ex=30)


def upload_file(file_path, dest_file, user_name):
    """
    通知客户端上传文件
    :param file_path:待上传文件
    :param dest_file:上传目标目录
    :param port:
    :return:
    """

    # address = os.environ.get("address", "192.168.12.249")
    url = f"{address}/client/noticeUpload"
    headers = {
        'Content-Type': 'application/json',  # 说明请求体是 JSON 格式
    }
    # 请求体的数据
    data = {
        'file_path': file_path,
        'dest_file': dest_file,
        'user_name': user_name
    }
    requests.post(url, headers=headers, json=data)


def vCode(image: str, code_type, apiKey, secretKey):
    """
    ocr 识别图片验证码
    :param image: 图片base64
    :param code_type: 7000:问答题、智能回答题；8000:不定长度英文数字汉字混合；9000:坐标选一（滑动）；9001:坐标多选，返回1~4个坐标；9002:坐标多选，返回3~5个坐标；9003:点击两个相同的字
    :param apiKey:
    :param secretKey:
    :return:
    """
    url = "https://ai.i-search.com.cn/ocr/v2/vCode"
    headers = {
        'Content-Type': 'application/json',  # 说明请求体是 JSON 格式
    }

    # 请求体的数据
    data = {
        'image': image,
        'code_type': code_type,
        'apiKey': apiKey,
        'secretKey': secretKey
    }
    response = requests.post(url, headers=headers, json=data)
    status_code = response.status_code
    if status_code != 200:
        return {"error_msg": "failure", "error_code": status_code}
    return response.json()


def save_file(url, cookies, file_path):
    """
    playwright保存文件
    """
    extracted = tldextract.extract(url)
    top_level_domain = f"{extracted.domain}.{extracted.suffix}"
    cookie = {}
    for item in cookies:
        if top_level_domain in item.get("domain"):
            cookie[item["name"]] = item["value"]
    response = requests.get(url, cookies=cookie)
    with open(file_path, 'wb') as file:
        file.write(response.content)
