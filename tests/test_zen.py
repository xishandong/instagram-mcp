import asyncio

import zendriver as zd


async def test_zen():
    browser = await zd.start(
        headless=False,
        browser_connection_timeout=2,
        browser_connection_max_tries=10, )
    print(browser)
    page = await browser.get("https://www.browserscan.net/bot-detection")
    print(page)
    await browser.stop()


if __name__ == "__main__":
    asyncio.run(test_zen())
