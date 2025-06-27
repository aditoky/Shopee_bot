# utils.py

import random
import requests

from config import PROXY_LIST, USER_AGENTS

def get_random_proxy():
    for _ in range(3):
        proxy = random.choice(PROXY_LIST)
        if check_proxy(proxy):
            return proxy
    return None

def check_proxy(proxy):
    try:
        test_url = "https://shopee.co.id/api/v4/pages/get_homepage_category_list"
        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        response = requests.get(test_url, proxies=proxies, timeout=10)
        return response.status_code == 200
    except:
        return False

def get_random_user_agent():
    return random.choice(USER_AGENTS)
