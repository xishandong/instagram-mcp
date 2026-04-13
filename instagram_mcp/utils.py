import json
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "dpr": "2",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-prefers-color-scheme": "light",
    "sec-ch-ua": "\"Not:A-Brand\";v=\"99\", \"Google Chrome\";v=\"145\", \"Chromium\";v=\"145\"",
    "sec-ch-ua-full-version-list": "\"Not:A-Brand\";v=\"99.0.0.0\", \"Google Chrome\";v=\"145.0.7632.117\", \"Chromium\";v=\"145.0.7632.117\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": "\"\"",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-ch-ua-platform-version": "\"12.0.0\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "viewport-width": "1512"
}


@dataclass
class Proxy:
    """A class representing a proxy server."""

    scheme: str
    host: str
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None

    @classmethod
    def from_url(cls, proxy_url: str):
        """
        Create a Proxy instance from a proxy URL.

        Parameters
        ----------
        proxy_url : str
            The proxy server URL.

        Returns
        -------
        Proxy
            The Proxy instance.
        """
        parsed = urlparse(proxy_url)

        return cls(
            scheme=parsed.scheme,
            host=parsed.hostname or "",
            port=parsed.port,
            username=parsed.username,
            password=parsed.password,
        )

    @property
    def url(self) -> str:
        """
        Get the proxy URL without authentication.

        Returns
        -------
        str
            The proxy URL.
        """
        host = self.host

        if self.port:
            host += f":{self.port}"

        return f"{self.scheme}://{host}"


def parse_imginn_search_results(html_content):
    """
    从Imginn搜索结果HTML中解析用户信息

    Args:
        html_content (str): HTML内容

    Returns:
        list: 包含用户信息的字典列表
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # 找到所有用户项
    user_items = soup.find_all('a', class_='tab-item user-item')

    users = []

    for item in user_items:
        user_info = {}

        # 获取用户链接
        href = item.get('href', '')
        if href:
            user_info['profile_url'] = f"https://imginn.com{href}"

        # 获取头像图片
        img_tag = item.find('img')
        if img_tag:
            user_info['avatar_url'] = img_tag.get('src', '')
            user_info['alt_text'] = img_tag.get('alt', '')
        else:
            user_info['avatar_url'] = ''
            user_info['alt_text'] = ''

        # 获取完整名称
        fullname_div = item.find('div', class_='fullname')
        if fullname_div:
            # 提取文本内容，移除认证徽章等元素
            span_tag = fullname_div.find('span')
            if span_tag:
                user_info['full_name'] = span_tag.get_text(strip=True)
            else:
                user_info['full_name'] = fullname_div.get_text(strip=True)

            # 检查是否有认证徽章
            badge = fullname_div.find('svg', class_='Zi--BadgeCert')
            user_info['is_verified'] = badge is not None
        else:
            user_info['full_name'] = ''
            user_info['is_verified'] = False

        # 获取用户名
        username_div = item.find('div', class_='username')
        if username_div:
            # 移除多余的空格和@符号
            username_text = username_div.get_text(strip=True)
            if username_text.startswith('@'):
                user_info['username'] = username_text[1:]
            else:
                user_info['username'] = username_text
        else:
            user_info['username'] = ''

        users.append(user_info)

    return users


def extract_json(html_content):
    """从 HTML 内容中提取 JSON 数据"""
    import re
    
    soup = BeautifulSoup(html_content, "html.parser")

    # 1. 首先尝试从 <pre> 标签中提取（用于 imginn API）
    json_script = soup.find('pre')
    if json_script:
        json_text = json_script.text
        try:
            json_data = json.loads(json_text)
            return json_data
        except json.JSONDecodeError:
            pass

    # 2. 尝试从 body 中直接提取 JSON 数组（imginn 的 posts API 返回格式）
    body_text = soup.get_text(strip=True)
    if body_text.startswith('[') or body_text.startswith('{'):
        try:
            return json.loads(body_text)
        except json.JSONDecodeError:
            pass

    # 3. 尝试用正则提取 JSON 数组
    json_match = re.search(r'\[\{.*?\}\]', html_content, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    # 4. 如果内容本身就是 JSON（没有 HTML 包装）
    if html_content.strip().startswith('[') or html_content.strip().startswith('{'):
        try:
            return json.loads(html_content)
        except json.JSONDecodeError:
            pass

    return None
