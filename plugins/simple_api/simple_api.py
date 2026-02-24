import requests


def get_handwriting_image_bytes(text: str):
    try:
        url = 'https://api.dragonlongzhu.cn//api/shouxie/xiezi/xiezi.php'
        response = requests.get(url, params={'text': text})
        if response.status_code != 200:
            return None
        return response.content
    except Exception as e:
        print(e)
        return None


def get_answer() -> str:
    url = 'http://api.yujn.cn/api/daan.php'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(e)
    return ''


def get_word(keyword: str) -> str:
    url = 'https://api.dragonlongzhu.cn/api/wenan_sou.php'
    try:
        response = requests.get(url, params={'msg': keyword}, timeout=2)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(e)
    return ''


def password(content: str, key: int, mode: int) -> str:
    try:
        key = int(key)
    except Exception as e:
        print(e)
        return ''
    if mode != 1 and mode != 2:
        return ''
    url = 'https://api.dragonlongzhu.cn/api/tea_key.php'
    data = {
        'msg': content,
        'key': key,
        'type': mode,
    }
    try:
        response = requests.get(url, params=data, timeout=5)
        response_json = response.json()
        if response.status_code == 200:
            if mode == 1:
                return response_json['tea_encryptedData']
            if mode == 2:
                return response_json['tea_decryptedData']
            return ''
        else:
            return ''
    except Exception as e:
        print(e)
        return ''
