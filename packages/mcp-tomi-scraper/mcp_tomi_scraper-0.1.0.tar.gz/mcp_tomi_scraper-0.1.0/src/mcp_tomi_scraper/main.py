# mcp_scraper_tool.py
import sys
import json
import logging
import os
import time
from jsonrpc import JSONRPCResponseManager, dispatcher
from playwright.sync_api import sync_playwright
from product_search import ProductScraperWithCache
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TransparentLabelScraper:
    def __init__(self, headless=True, state_file_path="tomi_login_state.json"):
        self.base_url = "https://tid.51tomi.com/newView/NewproductSearch"
        self.headless = headless
        self.state_file_path = state_file_path
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.is_running = False

    def start_browser(self):
        """启动浏览器并加载登录状态"""
        if self.is_running:
            logger.warning("浏览器已在运行中。")
            return {"status": "warning", "message": "浏览器已在运行中。"}

        try:
            logger.info("正在启动 Playwright...")
            self.playwright = sync_playwright().start()

            logger.info(f"启动 Chromium 浏览器 (headless={self.headless})")
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-features=TranslateUI"
                ],
                slow_mo=50
            )

            # 加载登录状态
            if os.path.exists(self.state_file_path):
                logger.info(f"✅ 加载登录状态文件: {self.state_file_path}")
                with open(self.state_file_path, "r", encoding="utf-8") as f:
                    storage_state = json.load(f)
                self.context = self.browser.new_context(
                    storage_state=storage_state,
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
                )
            else:
                logger.info("⚠️ 未找到登录状态文件，将创建新上下文（首次运行需在本地登录）")
                self.context = self.browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
                )

            self.page = self.context.new_page()
            self.is_running = True
            logger.info("🟢 浏览器启动成功")
            return {"status": "success", "message": "浏览器启动成功。"}

        except Exception as e:
            logger.error(f"🔴 启动浏览器失败: {e}")
            return {"status": "error", "message": str(e)}

    def close_browser(self):
        """关闭浏览器"""
        if not self.is_running:
            logger.warning("浏览器未运行。")
            return {"status": "warning", "message": "浏览器未运行。"}
        try:
            logger.info("正在关闭浏览器...")
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            self.is_running = False
            logger.info("🟢 浏览器已关闭")
            return {"status": "success", "message": "浏览器已关闭。"}
        except Exception as e:
            logger.error(f"🔴 关闭浏览器失败: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            self.browser = None
            self.context = None
            self.page = None
            self.playwright = None

    def search_products(self, keyword: str, max_pages: int = 1) -> dict:
        """搜索产品，带详细调试"""
        if not self.is_running:
            return {"status": "error", "message": "浏览器未启动。"}

        products = []
        try:
            logger.info(f"🔍 开始搜索关键词: '{keyword}'")

            # 1. 访问页面
            logger.info(f"🌐 访问 URL: {self.base_url}")
            self.page.goto(self.base_url)

            # 2. 打印页面标题和内容片段（关键调试）
            title = self.page.title()
            content_snippet = self.page.content()[:1000]
            logger.info(f"📌 页面标题: {title}")
            logger.info(f"📄 页面内容片段: {content_snippet}")

            if "JavaScript enabled" in content_snippet:
                logger.error("❌ 页面提示需要启用 JavaScript，可能是反爬或网络问题")
                return {"status": "error", "message": "页面未正确加载，可能被反爬"}

            # 3. 等待并检查搜索框
            logger.info("⏳ 等待搜索框出现 (input.navList_input)...")
            self.page.wait_for_timeout(3000)  # 给 JS 足够时间加载

            input_locator = self.page.locator("input.navList_input")
            if input_locator.count() == 0:
                logger.error("❌ 未找到搜索输入框！")
                logger.info(f"当前页面内容: {self.page.content()[:2000]}")
                return {"status": "error", "message": "未找到搜索输入框，请检查选择器或网络"}
            else:
                logger.info("✅ 找到搜索输入框")

            # 4. 输入关键词
            logger.info(f"⌨️ 输入关键词: {keyword}")
            input_locator.fill(keyword)

            # 5. 点击搜索按钮
            button_locator = self.page.locator("div.but_text")
            if button_locator.count() == 0:
                logger.error("❌ 未找到搜索按钮！")
                return {"status": "error", "message": "未找到搜索按钮"}
            logger.info("🖱️ 点击搜索按钮")
            button_locator.click()

            # 6. 等待搜索结果
            logger.info("⏳ 等待搜索结果加载...（等待 5 秒）")
            self.page.wait_for_timeout(5000)

            # 7. 检查产品列表
            product_items = self.page.locator("div.productList_left .tabs-row_bra")
            count = product_items.count()
            logger.info(f"📊 找到 {count} 个产品项")

            if count == 0:
                logger.warning("⚠️ 未找到任何产品，请检查：")
                logger.warning("   - 选择器是否正确")
                logger.warning("   - 网络是否被拦截")
                logger.warning("   - 是否需要登录")
                logger.info(f"当前页面内容: {self.page.content()[:2000]}")
            else:
                for i in range(min(count, 10)):  # 最多取10个
                    try:
                        item = product_items.nth(i)

                        name_zh = item.locator("div.ingredient-table > div.product").first.inner_text().strip()
                        name_en = item.locator("div.ingredient-table > div.translate").first.inner_text().strip()
                        full_name = f"{name_zh} ({name_en})".strip(" ()")

                        img_src = item.locator("div.picture_bra img.pic").first.get_attribute("src") or ""

                        # 尝试获取链接
                        link = ""
                        href = item.locator("a").first.get_attribute("href")
                        if href:
                            link = f"https://tid.51tomi.com{href}" if href.startswith("/") else href

                        classification = item.locator("div.classification").first.inner_text().strip()
                        region = item.locator("div.region").first.inner_text().strip()
                        message = item.locator("div.message").first.inner_text().strip()
                        grade = item.locator("div.mark .grade").first.inner_text().strip()

                        product_info = {
                            "name": full_name,
                            "link": link,
                            "image": img_src,
                            "classification": classification,
                            "region": region,
                            "message": message,
                            "grade": grade
                        }
                        products.append(product_info)
                        logger.info(f"✅ 提取产品 {i+1}: {full_name}")

                    except Exception as e:
                        logger.error(f"❌ 提取第 {i+1} 个产品失败: {e}")
                        continue

            return {
                "status": "success",
                "data": products,
                "count": len(products),
                "keyword": keyword
            }

        except Exception as e:
            logger.error(f"🔴 搜索失败: {e}")
            return {"status": "error", "message": str(e)}

    def get_hot_products(self) -> dict:
        """获取热门产品榜（保持原逻辑）"""
        if not self.is_running:
            return {"status": "error", "message": "浏览器未启动。"}

        try:
            logger.info("🔥 正在获取热门产品榜")
            self.page.goto(self.base_url)
            self.page.wait_for_timeout(3000)

            elements = self.page.query_selector_all("div.Factory_List div.Ranking_List_nrArr div.Ranking_List_text")
            hot_products = [{"name": el.inner_text().strip()} for el in elements if el.inner_text().strip()]

            logger.info(f"✅ 成功获取 {len(hot_products)} 个热门产品")
            return {
                "status": "success",
                "data": hot_products,
                "count": len(hot_products)
            }

        except Exception as e:
            logger.error(f"🔴 获取热门产品失败: {e}")
            return {"status": "error", "message": str(e)}

    def __enter__(self):
        res = self.start_browser()
        if res['status'] != 'success':
            raise Exception(res['message'])
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_browser()


# === MCP 接口 ===
scraper_instance = None
# ========================
# MCP 方法定义
# ========================

@dispatcher.add_method
def initialize():
    """初始化工具，启动浏览器。"""
    global scraper_instance
    if scraper_instance is not None:
        return {"message": "浏览器已在运行中。"}

    try:
        # 创建 ProductScraperWithCache 实例
        # 在服务器上请使用 headless=True
        scraper_instance = ProductScraperWithCache(state_file_path="tomi_login_state.json")
        scraper_instance.start(headless=True)  # 服务器环境必须为 True
        return {"message": "浏览器启动成功。"}
    except Exception as e:
        logger.error(f"initialize 失败: {e}")
        raise

@dispatcher.add_method
def search_products(keyword: str, max_pages: int = 1):
    """
    使用 ProductScraperWithCache 执行搜索。
    """
    global scraper_instance
    if scraper_instance is None:
        raise Exception("请先调用 'initialize'。")

    try:
        # 直接调用封装好的方法
        raw_products = scraper_instance.search_products(keyword)
        # 按 MCP 要求的格式返回
        return {
            "status": "success",
            "data": raw_products,
            "count": len(raw_products),
            "keyword": keyword
        }
    except Exception as e:
        logger.error(f"search_products 执行失败: {e}")
        raise

@dispatcher.add_method
def get_hot_products():
    """
    获取热门产品榜。（保留原逻辑）
    注意：此方法仍使用 mcp_scraper_tool.py 自己的 page。
    """
    global scraper_instance
    if scraper_instance is None:
        raise Exception("请先调用 'initialize'。")

    try:
        page = scraper_instance.page  # 复用已启动的页面
        logger.info("正在获取热门产品榜")
        # 假设页面已在 base_url
        hot_product_elements = page.query_selector_all("div.Factory_List div.Ranking_List_nrArr div.Ranking_List_text")
        hot_products = [{"name": el.inner_text().strip()} for el in hot_product_elements if el.inner_text().strip()]
        return {
            "status": "success",
            "data": hot_products,
            "count": len(hot_products)
        }
    except Exception as e:
        logger.error(f"get_hot_products 执行失败: {e}")
        raise

@dispatcher.add_method
def finalize():
    """关闭浏览器。"""
    global scraper_instance
    if scraper_instance is not None:
        scraper_instance.close()
        scraper_instance = None
    return {"message": "资源已清理。"}

# ========================
# 主程序入口
# ========================
if __name__ == "__main__":
    logger.info("MCP 工具已启动，等待请求...")
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            response = JSONRPCResponseManager.handle(line, dispatcher)
            sys.stdout.write(json.dumps(response.data, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    except Exception as e:
        logger.critical(f"异常: {e}", exc_info=True)
    finally:
        if scraper_instance:
            scraper_instance.close()
        logger.info("MCP 工具已退出")