import asyncio
import random
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, Iterable, List

import zendriver
from zendriver import cdp
from zendriver.cdp.fetch import AuthChallengeResponse, AuthRequired, RequestPaused
from zendriver.core.element import Element

from instagram_mcp.post_parser import parse_html_post
from instagram_mcp.utils import parse_imginn_search_results, extract_json, Proxy
from loguru import logger

# Monkey-patch: 新版 Chrome 移除了 sameParty 字段，zendriver 未适配会导致 KeyError
_original_cookie_from_json = cdp.network.Cookie.from_json.__func__


@classmethod
def _patched_cookie_from_json(cls, json):
    json.setdefault("sameParty", False)
    return _original_cookie_from_json(cls, json)


cdp.network.Cookie.from_json = _patched_cookie_from_json


class ChallengePlatform(Enum):
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
        # 自动处理 Docker 环境下的代理地址转换
        # 用户配置 127.0.0.1 或 localhost 时，在容器内自动转换为 host.docker.internal
        self.proxy_url = self._normalize_proxy_url(proxy_url)
        self._proxy = None

        self._timeout = 30.0

    @staticmethod
    def _is_running_in_docker() -> bool:
        """
        检测是否运行在 Docker 容器内
        
        Returns:
            bool: True 如果在 Docker 容器内，否则 False
        """
        import os
        
        # 方法 1: 检查 /.dockerenv 文件（Docker 容器内存在此文件）
        if os.path.exists("/.dockerenv"):
            return True
        
        # 方法 2: 检查 cgroup 中是否包含 docker 或 containerd
        try:
            with open("/proc/1/cgroup", "r") as f:
                cgroup_content = f.read()
                if "docker" in cgroup_content or "containerd" in cgroup_content:
                    return True
        except Exception:
            pass
        
        return False

    @staticmethod
    def _normalize_proxy_url(proxy_url: str) -> str:
        """
        标准化代理 URL，自动处理 Docker 环境下的本地地址转换
        
        在 Docker 容器内，127.0.0.1 和 localhost 指向容器本身而非宿主机。
        此方法检测运行环境，仅在容器内时将本地地址转换为 host.docker.internal。
        
        Args:
            proxy_url: 用户配置的代理 URL
            
        Returns:
            标准化后的代理 URL
        """
        if not proxy_url:
            return proxy_url
        
        # 仅在 Docker 容器内才进行地址转换
        if not InstagramClient._is_running_in_docker():
            logger.debug("检测到非 Docker 环境，保持代理地址不变")
            return proxy_url
        
        # 检测是否是本地地址
        local_patterns = [
            ("http://127.0.0.1:", "http://host.docker.internal:"),
            ("http://localhost:", "http://host.docker.internal:"),
            ("socks5://127.0.0.1:", "socks5://host.docker.internal:"),
            ("socks5://localhost:", "socks5://host.docker.internal:"),
        ]
        
        normalized = proxy_url
        for src, dest in local_patterns:
            if src in proxy_url.lower():
                normalized = proxy_url.replace(
                    src.split("://")[1].split(":")[0],
                    "host.docker.internal"
                )
                logger.info(f"Docker 环境检测到本地代理，已自动转换：{proxy_url} → {normalized}")
                break
        
        return normalized

    # Cloudflare challenge
    async def detect_challenge(self) -> Optional[ChallengePlatform]:
        html = await self.driver.main_tab.get_content()
        for platform in ChallengePlatform:
            if f"cType: '{platform.value}'" in html:
                return platform
        return None

    async def get_cookies(self) -> List[Dict]:
        try:
            result = await asyncio.wait_for(
                self.driver.main_tab.send(cdp.network.get_all_cookies()),
                timeout=5.0,
            )
            return [cookie.to_json() for cookie in result]
        except asyncio.TimeoutError:
            logger.warning("获取 cookies 超时")
            return []
        except Exception as e:
            logger.error(f"获取 cookies 失败: {e}")
            return []

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
                    continue
                await self.driver.main_tab.mouse_click(
                    position.x + random.randint(14, 31),
                    position.y + random.randint(24, 42)
                )

    async def solve(self):
        if await self.detect_challenge():
            logger.info("检测到 Cloudflare 挑战，开始处理")
            await self.solve_challenge()
            if extract_clearance_cookie(await self.get_cookies()):
                logger.info("Cloudflare 挑战解决成功")
                return True
            else:
                logger.error("Cloudflare 挑战解决失败")
                raise NotImplemented
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
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            )

            if self.proxy_url:
                logger.info(f"使用代理: {self.proxy_url}")
                self._proxy = Proxy.from_url(self.proxy_url)
                config.add_argument(f"--proxy-server={self._proxy.url}")

            self.driver = zendriver.Browser(config)
            await self.driver.start()

            if self._proxy is not None:
                await self.driver.get()
                self.driver.main_tab.add_handler(AuthRequired, self._on_auth_required)
                self.driver.main_tab.add_handler(RequestPaused, self._continue_request)
                self.driver.main_tab.feed_cdp(cdp.fetch.enable(handle_auth_requests=True))

        except Exception as e:
            logger.error(f"初始化浏览器失败: {e}")
            raise

    # deal instagram
    async def search_user(self, username: str) -> Dict[str, Any]:
        """搜索 Instagram 用户"""
        if not self.driver:
            await self.init_cookie()

        search_url = f"{self.base_url}/search/?q={username}"

        try:
            await self.driver.get(search_url)
            try:
                await self.driver.main_tab.wait_for_ready_state("interactive", timeout=30)
            except Exception as e:
                logger.warning(e)

            await self.solve()

            html = await self.driver.main_tab.get_content()
            logger.success("search_user call success")
            return {
                "success": True,
                "data": parse_imginn_search_results(html)
            }
        except Exception as e:
            logger.error(f"访问失败: {e}")
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

            for _ in range(3):
                result = await self.driver.main_tab.get_content()
                result = extract_json(result)
                if result:
                    logger.success("get_profile call success")
                    return {
                        "success": True,
                        "data": result
                    }
            else:
                raise

        except Exception as e:
            logger.error(f"获取用户资料失败: {e}")
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

            for _ in range(3):
                result = await self.driver.main_tab.get_content()
                result = extract_json(result)
                if result:
                    logger.success(f"get_user_posts call success, cursor: {result.get('cursor', '')}")
                    return {
                        "success": True,
                        "data": {
                            "_id": _id,
                            "cursor": result.get("cursor", ""),
                            "hasNext": result.get("hasNext", False),
                            "posts": result.get("items", []),
                        },
                    }
        except Exception as e:
            logger.exception(e)
            return {
                "success": False,
                "error": str(e),
            }

    async def get_post_detail(self, post_shortcode: str) -> Dict[str, Any]:
        """获取帖子详情 - 参考 instaloader 的方式解析 Instagram HTML"""
        try:
            if not self.driver:
                await self.init_cookie()

            await self.driver.get(self.base_url + "/p/" + post_shortcode + "/")
            try:
                await self.driver.main_tab.wait_for_ready_state("interactive", timeout=30)
            except Exception as e:
                logger.error(e)
            await self.solve()

            html = await self.driver.main_tab.get_content()
            logger.success("get_post_detail call success")
            return {
                "success": True,
                "data": parse_html_post(html)
            }
        except Exception as e:
            logger.error(f"获取post详情失败: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def close(self):
        if self.driver and self.proxy_url and "127.0.0.1" not in self.proxy_url:
            await self.driver.cookies.clear()

        if self.driver:
            await self.driver.stop()
        self.driver = None


async def main():
    ins = InstagramClient(
        proxy_url="http://127.0.0.1:7890",
        headless=True
    )
    data = await ins.get_user_posts("7140177628")
    logger.debug(data)
    await ins.close()


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())

