import asyncio
import json
import random
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, Iterable, List

import zendriver
from zendriver import cdp
from zendriver.cdp.fetch import AuthChallengeResponse, AuthRequired, RequestPaused
from zendriver.core.element import Element
from noble_tls import Session, Client

from instagram_mcp.post_parser import parse_json_post, parse_html_post
from instagram_mcp.utils import parse_imginn_search_results, extract_json, Proxy, headers


class ChallengePlatform(Enum):
    """
    Enumeration of known Cloudflare challenge interaction types.
    Matches the 'cType' signature found in Cloudflare's challenge HTML payload.
    """
    JAVASCRIPT = "non-interactive"
    MANAGED = "managed"
    INTERACTIVE = "interactive"


def extract_clearance_cookie(cookies: Iterable[dict]) -> Optional[dict]:
    for cookie in cookies:
        if cookie["name"] == "cf_clearance":
            return cookie
    return None


class InstagramClient:
    def __init__(self, proxy_url: str = "", headless: bool = True):
        self.driver: zendriver.Browser = None
        self.base_url = "https://imginn.com"

        self.headless = headless
        self.proxy_url = proxy_url
        self._proxy = None

        self._timeout = 30.0

    # Cloudflare challenge
    async def detect_challenge(self) -> Optional[ChallengePlatform]:
        html = await self.driver.main_tab.get_content()
        for platform in ChallengePlatform:
            if f"cType: '{platform.value}'" in html:
                return platform
        return None

    async def get_cookies(self) -> List[Dict]:
        cookies = await self.driver.cookies.get_all()
        return [cookie.to_json() for cookie in cookies]

    async def solve_challenge(self) -> None:
        start_timestamp = datetime.now()

        while (
                extract_clearance_cookie(await self.get_cookies()) is None
                and await self.detect_challenge() is not None
                and (datetime.now() - start_timestamp).seconds < self._timeout
        ):
            widget_input = await self.driver.main_tab.find("input")

            if widget_input.parent is None or not widget_input.parent.shadow_roots:
                await asyncio.sleep(0.25)
                continue

            challenge = Element(
                widget_input.parent.shadow_roots[0],
                self.driver.main_tab,
                widget_input.parent.tree,
            )

            challenge = challenge.children[0]

            if (
                    isinstance(challenge, Element)
                    and "display: none;" not in challenge.attrs["style"]
            ):
                await asyncio.sleep(1)

                try:
                    position = await challenge.get_position()
                except Exception as e:
                    print(f"Error: {e}")
                    continue
                await self.driver.main_tab.mouse_click(
                    position.x + random.randint(14, 31),
                    position.y + random.randint(24, 42)
                )

    async def solve(self):
        if await self.detect_challenge():
            print("检测到 Cloudflare 挑战，开始处理")
            await self.solve_challenge()
            if extract_clearance_cookie(await self.get_cookies()):
                print("Cloudflare 挑战解决成功")
                return True
            else:
                raise Exception("Cloudflare 挑战解决失败")
        return True

    # launch browser
    async def _on_auth_required(self, event: AuthRequired) -> None:
        if event.auth_challenge.source == "Proxy":
            await self.driver.main_tab.send(
                cdp.fetch.continue_with_auth(
                    event.request_id,
                    AuthChallengeResponse(
                        response="ProvideCredentials",
                        username=self._proxy.username,
                        password=self._proxy.password,
                    ),
                )
            )
        else:
            await self.driver.main_tab.send(
                cdp.fetch.continue_with_auth(
                    event.request_id, AuthChallengeResponse(response="Default")
                )
            )

    async def _continue_request(self, event: RequestPaused) -> None:
        await self.driver.main_tab.send(
            cdp.fetch.continue_request(request_id=event.request_id)
        )

    async def init_cookie(self):
        try:
            config = zendriver.Config(
                headless=self.headless,
                browser="chrome",
                no_sandbox=True,
                browser_connection_timeout=2,
                browser_connection_max_tries=10,
            )
            if self.proxy_url:
                self._proxy = Proxy.from_url(self.proxy_url)
                config.add_argument(f"--proxy-server={self._proxy.url}")

            self.driver = zendriver.Browser(config)
            await self.driver.start()
            if self._proxy is not None:
                await self.driver.get()
                self.driver.main_tab.add_handler(AuthRequired, self._on_auth_required)
                self.driver.main_tab.add_handler(RequestPaused, self._continue_request)
                self.driver.main_tab.feed_cdp(cdp.fetch.enable(handle_auth_requests=True))

            await self.driver.get(self.base_url)
            await self.driver.main_tab.wait_for_ready_state("interactive")
            await self.solve()
        except Exception as e:
            print(f"初始化浏览器失败: {e}")
            raise

    # deal instagram
    async def search_user(self, username: str) -> Dict[str, Any]:
        """搜索 Instagram 用户"""
        if not self.driver:
            await self.init_cookie()

        search_url = f"{self.base_url}/search/?q={username}"

        try:
            await self.driver.get(search_url)
            await self.driver.main_tab.wait_for_ready_state("interactive")
            await self.solve()

            html = await self.driver.main_tab.get_content()

            return {
                "success": True,
                "data": parse_imginn_search_results(html)
            }
        except Exception as e:
            print(f"访问失败: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def get_profile(self, username: str) -> Dict[str, Any]:
        """获取用户资料"""
        if not self.driver:
            await self.init_cookie()

        profile_url = f"{self.base_url}/api/search/?name={username}"

        try:
            await self.driver.get(profile_url)
            await self.driver.main_tab.wait_for_ready_state("complete")
            await self.solve()

            result = await self.driver.main_tab.get_content()
            result = extract_json(result)
            return {
                "success": True,
                "data": result
            }

        except Exception as e:
            print(f"获取用户资料失败: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def get_user_posts(self, _id: str, cursor: str = "") -> Dict[str, Any]:
        """获取用户帖子下一页"""
        if not self.driver:
            await self.init_cookie()

        api_url = f"{self.base_url}/api/posts/?id={_id}&cursor="
        if cursor:
            api_url += cursor

        try:
            await self.driver.get(api_url)
            await self.driver.main_tab.wait_for_ready_state("complete")
            await self.solve()

            result = await self.driver.main_tab.get_content()
            result = extract_json(result)
            return {
                "success": True,
                "data": result.get("items", []),
                "cursor": result.get("cursor", ""),
                "hasNext": result.get("hasNext", False),
                "_id": _id,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    async def get_post_details(self, post_shortcode: str) -> Dict[str, Any]:
        """获取帖子详情 - 参考 instaloader 的方式解析 Instagram HTML"""
        try:
            # 使用 noble_tls 直接请求 Instagram 帖子页面
            session = Session(client=Client.CHROME_133, random_tls_extension_order=True)
            response = await session.get(
                "https://www.instagram.com/graphql/query",
                headers=headers,
                params={
                    "variables": json.dumps({"shortcode": post_shortcode}, separators=(',', ':')),
                    "doc_id": "8845758582119845",
                    "server_timestamps": "true"
                },
                proxy=self.proxy_url
            )
            html = response.json()
            if html.get("status") != "ok":
                print(html)
                print("从ins直接获取post详情失败, 转为imginn获取")
                if not self.driver:
                    await self.init_cookie()

                await self.driver.get(self.base_url + "/p/" + post_shortcode + "/")
                await self.driver.main_tab.wait_for_ready_state("interactive")
                await self.solve()
                html = await self.driver.main_tab.get_content()
                return {
                    "success": True,
                    "data": parse_html_post(html)
                }
            else:
                return {
                    "success": True,
                    "data": parse_json_post(html)
                }
        except Exception as e:
            print(f"获取post详情失败: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def close(self):
        if self.driver:
            await self.driver.cookies.clear()
            await self.driver.stop()
            self.driver = None
