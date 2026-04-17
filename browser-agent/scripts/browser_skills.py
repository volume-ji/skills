import asyncio
from playwright.async_api import async_playwright
from e2b import Sandbox
from config import E2B_API_KEY, E2B_ags_template


class SandboxBrowserSkills:
    """基于云端沙箱的浏览器操作能力集"""

    def __init__(self):
        self.sandbox = None
        self.playwright = None
        self.browser = None
        self.page = None
        self.vnc_url = None

    async def start(self, timeout: int = 600):
        """启动云沙箱并连接浏览器

        Args:
            timeout: 超时时间（秒）

        Returns:
            self

        Raises:
            ValueError: E2B_API_KEY 未设置
        """
        if not E2B_API_KEY or E2B_API_KEY.startswith("oak_xxx"):
            raise ValueError("E2B_API_KEY 未设置")

        # 创建浏览器沙箱
        self.sandbox = Sandbox.create(template=E2B_ags_template, timeout=timeout)

        # 生成 VNC 链接
        self.vnc_url = (
            f"https://{self.sandbox.get_host(9000)}/novnc/vnc_lite.html"
            f"?path=websockify"
            f"?access_token={self.sandbox._envd_access_token}"
        )
        print(f"VNC: {self.vnc_url}")

        # 通过 CDP 协议连接远程浏览器
        cdp_url = f"https://{self.sandbox.get_host(9000)}/cdp"
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.connect_over_cdp(
            cdp_url,
            headers={"X-Access-Token": str(self.sandbox._envd_access_token)}
        )

        context = self.browser.contexts[0]
        self.page = context.pages[0] if context.pages else await context.new_page()
        return self

    async def stop(self):
        """关闭沙箱和浏览器"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        if self.sandbox:
            self.sandbox.kill()

    async def navigate(self, url: str) -> str:
        """导航到指定 URL

        Args:
            url: 目标网址

        Returns:
            操作结果消息
        """
        await self.page.goto(url, wait_until="domcontentloaded")
        return f"已导航到: {url}"

    async def highlight_elements(self) -> str:
        """高亮所有可交互元素并返回编号列表

        Returns:
            高亮元素的编号和文本列表
        """
        elements = await self.page.evaluate('''() => {
            document.querySelectorAll('[data-highlight-id]').forEach(el => { el.style.outline = ''; });
            document.querySelectorAll('.highlight-label').forEach(el => el.remove());
            const colors = { link: '#FF6B6B', button: '#4ECDC4', input: '#45B7D1', other: '#DDA0DD' };
            const results = []; let id = 1;
            document.querySelectorAll('a[href], button, [role="button"], input:not([type="hidden"]), textarea').forEach(el => {
                const rect = el.getBoundingClientRect();
                if (rect.width === 0 || rect.height === 0 || rect.top > window.innerHeight) return;
                let type = 'other', color = colors.other;
                if (el.tagName === 'A') { type = 'link'; color = colors.link; }
                else if (el.tagName === 'BUTTON') { type = 'button'; color = colors.button; }
                else if (el.tagName === 'INPUT') { type = 'input'; color = colors.input; }
                el.style.outline = '3px solid ' + color;
                el.setAttribute('data-highlight-id', id);
                const label = document.createElement('div');
                label.className = 'highlight-label';
                label.textContent = id;
                label.style.cssText = 'position:absolute;background:' + color + ';color:white;padding:2px 6px;border-radius:10px;font-size:12px;font-weight:bold;z-index:10000;left:' + (rect.left+window.scrollX-10) + 'px;top:' + (rect.top+window.scrollY-10) + 'px;';
                document.body.appendChild(label);
                results.push({ id, type, text: (el.innerText?.trim() || el.value || '').substring(0, 40) });
                id++;
            });
            return results.slice(0, 30);
        }''')
        result = f"已高亮 {len(elements)} 个元素:\n"
        for el in elements[:12]:
            emoji = {'link': '🔗', 'button': '🔘', 'input': '📝'}.get(el['type'], '⚪')
            result += f"  [{el['id']:2d}] {emoji} {el['text'][:30]}\n"
        return result

    async def click_element(self, element_id: int) -> str:
        """点击指定编号的元素

        Args:
            element_id: 高亮元素编号

        Returns:
            操作结果消息
        """
        clicked = await self.page.evaluate(f'(id) => {{ const el = document.querySelector("[data-highlight-id=\\"" + id + "\\"]"); if (el) {{ el.click(); return true; }} return false; }}', element_id)
        await asyncio.sleep(0.5)
        return f"已点击元素 [{element_id}]" if clicked else "未找到元素"

    async def click_text(self, text: str) -> str:
        """点击包含指定文本的元素

        Args:
            text: 要点击的文本

        Returns:
            操作结果消息
        """
        await self.page.get_by_text(text, exact=False).first.click(timeout=5000)
        return f"已点击: {text}"

    async def get_page_text(self, max_length: int = 2000) -> str:
        """获取页面文本

        Args:
            max_length: 最大返回长度

        Returns:
            页面文本内容
        """
        text = await self.page.inner_text("body")
        return f"页面文本:\n{text[:max_length]}..."

    async def scroll_down(self, pixels: int = 500) -> str:
        """向下滚动页面

        Args:
            pixels: 滚动像素数

        Returns:
            操作结果消息
        """
        await self.page.mouse.wheel(0, pixels)
        return "已滚动"

    async def scroll_up(self, pixels: int = 500) -> str:
        """向上滚动页面

        Args:
            pixels: 滚动像素数

        Returns:
            操作结果消息
        """
        await self.page.mouse.wheel(0, -pixels)
        return "已向上滚动"

    async def screenshot(self, filename: str) -> str:
        """截图并保存

        Args:
            filename: 保存文件名

        Returns:
            操作结果消息
        """
        await self.page.screenshot(path=filename)
        return f"已截图: {filename}"

    async def fill_input(self, text: str, selector: str = None) -> str:
        """在输入框中填入文本

        Args:
            text: 要填入的文本
            selector: CSS 选择器（可选，不填则填入当前焦点的输入框）

        Returns:
            操作结果消息
        """
        if selector:
            await self.page.fill(selector, text)
            return f"已在 {selector} 填入: {text}"
        else:
            await self.page.keyboard.type(text)
            return f"已填入: {text}"

    async def press_key(self, key: str) -> str:
        """按键

        Args:
            key: 按键名称（如 Enter, Escape 等）

        Returns:
            操作结果消息
        """
        await self.page.keyboard.press(key)
        return f"已按键: {key}"

    async def wait_for_navigation(self, timeout: int = 30000) -> str:
        """等待页面导航完成

        Args:
            timeout: 超时时间（毫秒）

        Returns:
            操作结果消息
        """
        await self.page.wait_for_load_state("networkidle", timeout=timeout)
        return "页面导航完成"

    async def get_current_url(self) -> str:
        """获取当前页面 URL

        Returns:
            当前 URL
        """
        return self.page.url

    async def get_element_text(self, selector: str) -> str:
        """获取指定元素的文本

        Args:
            selector: CSS 选择器

        Returns:
            元素文本内容
        """
        text = await self.page.inner_text(selector)
        return text

    async def execute_script(self, script: str) -> str:
        """执行 JavaScript 脚本

        Args:
            script: JavaScript 代码

        Returns:
            执行结果
        """
        result = await self.page.evaluate(script)
        return f"执行结果: {result}"
