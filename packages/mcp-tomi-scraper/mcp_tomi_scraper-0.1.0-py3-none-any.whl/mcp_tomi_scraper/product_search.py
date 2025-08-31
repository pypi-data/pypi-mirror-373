# product_search.py
from playwright.sync_api import sync_playwright, expect
import logging
import time
import json
import os

logger = logging.getLogger(__name__)

class ProductScraperWithCache:
    """
    使用 Playwright 爬取指定网站的产品信息，并支持缓存登录状态。
    此类专为被 MCP 工具导入而设计。
    """

    def __init__(self, state_file_path="tomi_login_state.json"):
        # ✅ 修复：移除 URL 末尾的多余空格
        self.base_url = "https://tid.51tomi.com/newView/NewproductSearch"
        self.state_file_path = state_file_path
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    # ========================
    # 添加：上下文管理器支持
    # ========================
    def __enter__(self):
        self.start(headless=True)  # 在服务器上默认 headless=True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def start(self, headless=True):
        """启动浏览器，并根据情况加载或等待登录。"""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=headless,
                slow_mo=50,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-blink-features=AutomationControlled"
                ]
            )

            # --- 状态加载逻辑 ---
            if os.path.exists(self.state_file_path):
                logger.info(f"尝试加载已保存的登录状态: {self.state_file_path}")
                self.context = self.browser.new_context(
                    storage_state=self.state_file_path,
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
            else:
                logger.info("未找到已保存的登录状态文件，需要手动登录...")
                self.context = self.browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )

            self.page = self.context.new_page()
            logger.info("Playwright 浏览器启动成功")

            # --- 登录检查/等待逻辑 ---
            if not os.path.exists(self.state_file_path):
                logger.info("请在打开的浏览器中手动完成登录流程...")
                logger.info("登录成功并可以访问目标页面后，按 Enter 键继续执行爬取...")
                self.page.goto(self.base_url)
                input("等待手动登录...按 Enter 继续:")
                logger.info("正在保存登录状态...")
                storage_state = self.context.storage_state()
                with open(self.state_file_path, "w", encoding="utf-8") as f:
                    json.dump(storage_state, f, ensure_ascii=False, indent=2)
                logger.info(f"登录状态已保存至: {self.state_file_path}")
            else:
                logger.info("已加载登录状态，正在访问目标页面...")
                self.page.goto(self.base_url)

        except Exception as e:
            logger.error(f"启动 Playwright 或登录时失败: {e}")
            raise

    def close(self):
        """关闭浏览器和 Playwright"""
        if self.browser:
            self.browser.close()
            logger.info("浏览器已关闭")
        if self.playwright:
            self.playwright.stop()
            logger.info("Playwright 已停止")

    def search_products(self, keyword):
        """
        根据关键词搜索产品，并返回包含名称、链接、图片、分类、国别、备案、评分的产品信息列表。
        """
        products = []
        try:
            logger.info(f"正在搜索关键词: {keyword}")
            # 确保在正确的页面
            if self.page.url != self.base_url:
                self.page.goto(self.base_url)

            # 等待并操作搜索框
            self.page.wait_for_selector("input.navList_input", timeout=15000)
            search_input = self.page.locator("input.navList_input")
            search_button = self.page.locator("div.but_text")

            search_input.fill(keyword)
            time.sleep(0.5)
            search_button.click()

            logger.info("等待搜索结果加载...")
            # 等待产品列表容器出现
            self.page.wait_for_selector("div.productList_left .tabs-row_bra", timeout=20000)

            # 关键：等待至少一个产品项的“关键元素”出现，确保内容已填充
            logger.info("等待第一个产品的具体信息加载...")
            try:
                self.page.wait_for_selector("div.productList_left .tabs-row_bra >> div.product", timeout=10000)
                self.page.wait_for_selector("div.productList_left .tabs-row_bra >> div.picture_bra img", timeout=10000)
                logger.info("✅ 产品详细信息已开始加载")
            except Exception as e:
                logger.warning(f"⚠️ 等待产品详细信息超时，但将继续尝试提取: {e}")

            product_item_locators = self.page.locator("div.productList_left .tabs-row_bra")
            count = min(product_item_locators.count(), 10)  # 取前10个
            logger.info(f"找到 {count} 个搜索结果项")

            for i in range(count):
                try:
                    product_element = product_item_locators.nth(i)

                    # --- 为每个产品项增加内部等待 ---
                    logger.debug(f"正在提取第 {i+1} 个产品...")

                    # 等待中文名出现
                    if product_element.locator("div.ingredient-table > div.product").count() == 0:
                        logger.warning(f"⚠️ 第 {i+1} 个产品缺少中文名")
                        name_zh = "未知"
                    else:
                        # 使用 inner_text() 前，确保元素可见（wait_for会自动等待）
                        name_zh = product_element.locator("div.ingredient-table > div.product").first.inner_text().strip()

                    # 等待英文名
                    if product_element.locator("div.ingredient-table > div.translate").count() == 0:
                        name_en = ""
                    else:
                        name_en = product_element.locator("div.ingredient-table > div.translate").first.inner_text().strip()

                    full_name = f"{name_zh} ({name_en})".strip(" ()")

                    # 图片链接
                    img_locator = product_element.locator("div.picture_bra img.pic")
                    if img_locator.count() > 0:
                        # get_attribute 可能会因图片懒加载而超时，使用 evaluate 获取 src
                        img_src = img_locator.first.get_attribute("src")
                        # 如果是懒加载，src 可能是占位图，data-src 才是真实地址
                        if not img_src or "placeholder" in img_src:
                            img_src = img_locator.first.get_attribute("data-src") or img_src
                    else:
                        img_src = ""

                    # --- 获取链接：更安全的方式 ---
                    link = ""
                    # 尝试1: 查找 a 标签
                    a_locator = product_element.locator("a").first
                    if a_locator.count() > 0:
                        try:
                            # 使用 evaluate 避免 get_attribute 超时
                            href = a_locator.get_attribute("href")
                            if href:
                                link = f"https://tid.51tomi.com{href}" if href.startswith("/") else href
                        except:
                            logger.debug(f"第 {i+1} 个产品的 a 标签无 href")

                    # 尝试2: 从 data-url 获取
                    if not link:
                        data_url = product_element.get_attribute("data-url")
                        if data_url:
                            link = f"https://tid.51tomi.com{data_url}" if data_url.startswith("/") else data_url

                    # --- 提取其他信息 ---
                    classification = self._safe_inner_text(product_element, "div.classification")
                    region = self._safe_inner_text(product_element, "div.region")
                    message = self._safe_inner_text(product_element, "div.message")
                    grade = self._safe_inner_text(product_element, "div.mark .grade")

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
                    logger.info(f"✅ 提取产品: {full_name}")

                    time.sleep(0.3)  # 减少频率

                except Exception as e:
                    logger.error(f"❌ 提取第 {i+1} 个产品时发生错误: {e}")
                    # 打印当前产品项的 HTML 用于调试
                    try:
                        html = product_element.inner_html()
                        logger.debug(f"第 {i+1} 个产品项 HTML: {html[:500]}...")
                    except:
                        pass
                    continue

        except Exception as e:
            logger.error(f"❌ 执行搜索产品 '{keyword}' 时发生错误: {e}")

        return products

    def _safe_inner_text(self, locator, selector):
        """安全地获取元素的 inner_text，避免超时"""
        try:
            el = locator.locator(selector).first
            if el.count() > 0:
                return el.inner_text().strip()
            return ""
        except:
            return ""
# ========================
# 独立运行此文件时的测试入口
# ========================
if __name__ == "__main__":
    # 为独立运行配置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    state_file = "tomi_login_state.json"

    # ✅ 使用 with 语句，现在可以正常工作了
    with ProductScraperWithCache(state_file_path=state_file) as scraper:
        try:
            results = scraper.search_products("防晒")
            for product in results:
                print(f"{product['name']} | 评分: {product['grade']}")
        except Exception as e:
            logger.error(f"测试出错: {e}")