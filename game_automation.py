# game_automation.py
import asyncio
from playwright.async_api import async_playwright


async def run_account(account_id, cookie):
    """
    异步运行指定账号的游戏流程.

    Args:
        account_id: 账号 ID.
        cookie: 账号 Cookie（字典或列表）.

    Returns:
        游戏统计数据 (例如: 赢了多少次, 输了多少次, 总收益).
    """
    print(f"开始运行账号 {account_id}...")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            if isinstance(cookie, list):
                await context.add_cookies(cookie)
            elif isinstance(cookie, dict):
                await context.add_cookies([cookie])
            page = await context.new_page()
            await page.goto("https://www.magicnewton.com/portal/rewards", wait_until='networkidle')

            # 调试：打印页面 HTML
            print(await page.content())

            # 等待页面加载并检查登录状态
            await page.wait_for_selector('p.gGRRlH.WrOCw.AEdnq.hGQgmY.jdmPpC', timeout=10000)
            user_email = await page.evaluate(
                "() => document.querySelector('p.gGRRlH.WrOCw.AEdnq.hGQgmY.jdmPpC')?.innerText || ''")
            if not user_email:
                print("Failed to get user email.  Check login status.")
                await browser.close()
                return {'wins': 0, 'losses': 0, 'profit': 0}
            print(f"Logged in as: {user_email}")

            # 投骰子游戏
            dice_stats = {'wins': 0, 'losses': 0, 'profit': 0}
            try:
                await page.wait_for_selector('.game-dice-start-button', timeout=10000)
                start_button = await page.query_selector('.game-dice-start-button')
                if start_button:
                    await start_button.click()
                    await asyncio.sleep(2)

                    await page.wait_for_selector('.game-dice-result', timeout=10000)
                    result_element = await page.query_selector('.game-dice-result')
                    if result_element:
                        result_text = await result_element.inner_text()
                        print(f"Dice result: {result_text}")

                        if "win" in result_text.lower():
                            dice_stats['wins'] = 1
                        else:
                            dice_stats['losses'] = 1

                        await page.wait_for_selector('.earned-credits-balance-number', timeout=10000)
                        credits_element = await page.query_selector('.earned-credits-balance-number')
                        if credits_element:
                            credits_text = await credits_element.inner_text()
                            try:
                                credits = int(credits_text.replace(",", ""))
                                dice_stats['profit'] = credits
                            except ValueError:
                                print("Error parsing credits. Could not get the profit")


            except Exception as e:
                print(f"Error in Dice game: {e}")

            await browser.close()
            print(
                f"账号 {account_id} 运行结束, 统计数据： wins={dice_stats['wins']}, losses={dice_stats['losses']}, profit={dice_stats['profit']}")
            return dice_stats

    except Exception as e:
        print(f"Error running account {account_id}: {e}")
        return {'wins': 0, 'losses': 0, 'profit': 0}


# 同步包装器以便 GUI 调用
def run_account_sync(account_id, cookie):
    return asyncio.run(run_account(account_id, cookie))
