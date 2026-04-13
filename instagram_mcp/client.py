"""
Instagram MCP Client - 基于 zendriver 的 Instagram 数据访问客户端
通过 imginn.com 访问 Instagram 公开数据，自动处理 Cloudflare 验证
"""

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
    """修复新版 Chrome Cookie 兼容性问题"""
    json.setdefault("sameParty", False)
    return _original_cookie_from_json(cls, json)


cdp.network.Cookie.from_json = _patched_cookie_from_json


class ChallengePlatform(Enum):
    """Cloudflare 挑战类型枚举"""
    JAVASCRIPT = "non-interactive"
    MANAGED = "managed"
    INTERACTIVE = "interactive"


def extract_clearance_cookie(cookies: Iterable[dict]) -> Optional[dict]:
    """从 Cookie 列表中提取 cf_clearance"""
    for cookie in cookies:
        if cookie["name"] == "cf_clearance":
            return cookie
    return None


class InstagramClient:
    """
    Instagram 数据访问客户端
    
    通过 imginn.com 访问 Instagram 公开数据，支持：
    - 搜索用户
    - 获取用户资料
    - 获取用户帖子（带分页）
    - 获取帖子详情
    - 自动处理 Cloudflare 验证
    - 代理支持
    """
    
    def __init__(self, proxy_url: str = "", headless: bool = True):
        """
        初始化 Instagram 客户端
        
        Args:
            proxy_url: 代理地址，如 "http://127.0.0.1:7890"
            headless: 是否使用无头模式
        """
        self.driver: zendriver.Browser = None
        self.base_url = "https://imginn.com"

        self.headless = headless
        self.proxy_url = proxy_url
        self._proxy = None

        self._timeout = 30.0

    # ========== Cloudflare 验证相关 ==========
    
    async def detect_challenge(self) -> Optional[ChallengePlatform]:
        """检测 Cloudflare 挑战类型"""
        html = await self.driver.main_tab.get_content()
        for platform in ChallengePlatform:
            if f"cType: '{platform.value}'" in html:
                return platform
        return None

    async def get_cookies(self) -> List[Dict]:
        """获取当前浏览器的所有 Cookie"""
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
            logger.error(f"获取 cookies 失败：{e}")
            return []

    async def solve_challenge(self) -> None:
        """自动处理 Cloudflare 验证挑战"""
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

    async def solve(self) -> bool:
        """
        检测并解决 Cloudflare 挑战
        
        Returns:
            bool: 是否成功解决挑战
        """
        if await self.detect_challenge():
            logger.info("检测到 Cloudflare 挑战，开始处理")
            await self.solve_challenge()
            if extract_clearance_cookie(await self.get_cookies()):
                logger.info("Cloudflare 挑战解决成功")
                return True
            else:
                logger.error("Cloudflare 挑战解决失败")
                raise NotImplementedError("Cloudflare 挑战解决失败")
        return True

    # ========== 浏览器初始化 ==========
    
    async def _on_auth_required(self, event: AuthRequired) -> None:
        """处理代理认证"""
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
        """处理被暂停的请求"""
        await self.driver.main_tab.send(
            cdp.fetch.continue_request(request_id=event.request_id)
        )

    async def init_cookie(self):
        """初始化浏览器和 Cookie"""
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
                logger.info(f"使用代理：{self.proxy_url}")
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
            logger.error(f"初始化浏览器失败：{e}")
            raise

    # ========== Instagram API 方法 ==========
    
    async def search_user(self, username: str) -> Dict[str, Any]:
        """
        搜索 Instagram 用户
        
        Args:
            username: 用户名或关键词
            
        Returns:
            Dict: 搜索结果，包含用户列表
        """
        if not self.driver:
            await self.init_cookie()

        search_url = f"{self.base_url}/search/?q={username}"

        try:
            await self.driver.get(search_url)
            try:
                await self.driver.main_tab.wait_for_ready_state("interactive", timeout=30)
            except Exception as e:
                logger.warning(f"等待页面交互超时：{e}")

            await self.solve()

            html = await self.driver.main_tab.get_content()
            logger.success("search_user call success")
            return {
                "success": True,
                "data": parse_imginn_search_results(html)
            }
        except Exception as e:
            logger.error(f"搜索用户失败：{e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def get_profile(self, username: str) -> Dict[str, Any]:
        """
        获取用户详细资料
        
        Args:
            username: Instagram 用户名
            
        Returns:
            Dict: 用户资料，包含粉丝数、帖子数等
        """
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
                    raise ValueError("无法解析 JSON 数据")

        except Exception as e:
            logger.error(f"获取用户资料失败：{e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def get_user_posts(self, _id: str, cursor: str = "") -> Dict[str, Any]:
        """
        获取用户帖子列表（支持分页）
        
        Args:
            _id: 用户 ID（从 get_profile 获取）
            cursor: 分页游标（可选，用于获取下一页）
            
        Returns:
            Dict: 帖子列表，包含帖子数据和分页信息
        """
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
            logger.error(f"获取用户帖子失败：{e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def get_post_detail(self, post_shortcode: str) -> Dict[str, Any]:
        """
        获取帖子详情
        
        Args:
            post_shortcode: 帖子短代码（URL 中 /p/ 后的部分）
            
        Returns:
            Dict: 帖子详情，包含图片/视频、点赞数、评论数等
        """
        try:
            if not self.driver:
                await self.init_cookie()

            await self.driver.get(self.base_url + "/p/" + post_shortcode + "/")
            try:
                await self.driver.main_tab.wait_for_ready_state("interactive", timeout=30)
            except Exception as e:
                logger.error(f"等待页面交互超时：{e}")
                
            await self.solve()

            html = await self.driver.main_tab.get_content()
            logger.success("get_post_detail call success")
            return {
                "success": True,
                "data": parse_html_post(html)
            }
        except Exception as e:
            logger.error(f"获取帖子详情失败：{e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def close(self):
        """关闭浏览器并清理资源"""
        if self.driver and self.proxy_url and "127.0.0.1" not in self.proxy_url:
            await self.driver.cookies.clear()

        if self.driver:
            await self.driver.stop()
        self.driver = None


async def main():
    """测试入口"""
    ins = InstagramClient(
        proxy_url="http://127.0.0.1:1087",
        headless=True
    )
    
    # 测试搜索
    search_result = await ins.search_user("jennie")
    print(f"搜索：{search_result}")
    
    # 测试获取资料
    profile = await ins.get_profile("jennierubyjane")
    print(f"资料：{profile}")
    
    # 测试获取帖子
    if profile.get("data"):
        user_id = profile["data"].get("pk")
        if user_id:
            posts = await ins.get_user_posts(user_id)
            print(f"帖子：{len(posts.get('data', {}).get('posts', []))} 个")
    
    await ins.close()


if __name__ == '__main__':
    asyncio.run(main())
