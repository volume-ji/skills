---
name: browser-agent
description: This skill provides browser automation capabilities for web browsing, page interaction, and screenshot capture. Use this skill when the user needs to interact with web pages programmatically, navigate to URLs, click elements, fill forms, scroll pages, or capture screenshots. The skill leverages Playwright with E2B sandbox to provide a cloud-based browser environment.
---

# Browser Agent Skill

This skill enables browser automation through Playwright and E2B sandbox, allowing programmatic control of web browsers for web scraping, testing, and interaction tasks.

## Purpose

Provide automated browser interaction capabilities including navigation, element manipulation, form filling, scrolling, and screenshot capture in a cloud-based sandbox environment.

## When to Use

- Navigate to specific URLs and load web pages
- Identify and interact with clickable elements on a page
- Fill forms with text input
- Scroll through web pages
- Capture screenshots of web pages
- Extract text content from web pages
- Execute JavaScript in the browser context
- Wait for page navigation or element loading

## Skill Structure

The skill includes:

- **scripts/browser_skills.py**: Core browser automation class `SandboxBrowserSkills` with all interaction methods
- **scripts/config.py**: Configuration module for E2B API settings and sandbox template
- **scripts/__init__.py**: Module exports

## Usage

### Initialize the Browser Environment

First, import and start the browser sandbox:

```python
from skills.browser_skills import SandboxBrowserSkills

# Create instance and start the browser
browser = SandboxBrowserSkills()
await browser.start(timeout=600)  # timeout in seconds

# The VNC URL will be printed for visual monitoring
```

### Common Operations

**Navigate to a URL:**
```python
result = await browser.navigate("https://example.com")
print(result)  # "已导航到: https://example.com"
```

**Highlight and identify interactive elements:**
```python
elements = await browser.highlight_elements()
# Returns a list of highlighted elements with IDs for interaction
# Elements are color-coded by type (links, buttons, inputs)
```

**Click an element by ID (from highlight):**
```python
result = await browser.click_element(5)
print(result)  # "已点击元素 [5]"
```

**Click an element by text content:**
```python
result = await browser.click_text("Submit")
print(result)  # "已点击: Submit"
```

**Fill an input field:**
```python
# Fill specific input by selector
result = await browser.fill_input("hello world", selector="input[type='text']")

# Or fill the currently focused input
result = await browser.fill_input("search term")
```

**Scroll the page:**
```python
await browser.scroll_down(500)   # Scroll down 500 pixels
await browser.scroll_up(300)     # Scroll up 300 pixels
```

**Take a screenshot:**
```python
result = await browser.screenshot("homepage.png")
print(result)  # "已截图: homepage.png"
```

**Get page content:**
```python
# Get current URL
url = await browser.get_current_url()

# Get page text content (limited length)
text = await browser.get_page_text(max_length=2000)

# Get specific element text
element_text = await browser.get_element_text("h1")
```

**Execute JavaScript:**
```python
result = await browser.execute_script("document.title")
print(result)  # Returns the page title
```

**Press keyboard keys:**
```python
result = await browser.press_key("Enter")
result = await browser.press_key("Escape")
```

**Wait for navigation:**
```python
result = await browser.wait_for_navigation(timeout=30000)
```

### Cleanup

Always stop the browser when done to free resources:

```python
await browser.stop()
```

## Configuration

The browser behavior is controlled by environment variables in `config.py`:

- `E2B_DOMAIN`: E2B service domain (default: ap-guangzhou.tencentags.com)
- `E2B_API_KEY`: E2B API key for authentication
- `E2B_AGS_TEMPLATE`: Sandbox template name

Set these as environment variables before starting the browser, or modify directly in `config.py`.

## Method Reference

### Lifecycle Methods

- `start(timeout: int = 600)` - Initialize sandbox and connect browser
- `stop()` - Close browser and kill sandbox

### Navigation

- `navigate(url: str)` - Navigate to specified URL
- `get_current_url()` - Get current page URL
- `wait_for_navigation(timeout: int = 30000)` - Wait for page load

### Element Interaction

- `highlight_elements()` - Highlight all interactive elements with IDs
- `click_element(element_id: int)` - Click element by highlight ID
- `click_text(text: str)` - Click element containing text

### Input

- `fill_input(text: str, selector: str = None)` - Fill text in input field
- `press_key(key: str)` - Press keyboard key

### Page Content

- `get_page_text(max_length: int = 2000)` - Extract page text
- `get_element_text(selector: str)` - Get text of specific element
- `execute_script(script: str)` - Execute JavaScript and return result

### Scrolling

- `scroll_down(pixels: int = 500)` - Scroll page down
- `scroll_up(pixels: int = 500)` - Scroll page up

### Visual

- `screenshot(filename: str)` - Capture screenshot and save to file

## Best Practices

1. **Always call `start()` before any browser operations**
2. **Always call `stop()` when finished** to release sandbox resources
3. **Use `highlight_elements()` first** to understand page structure before interaction
4. **Use timeouts appropriately** for navigation and element operations
5. **Handle exceptions** for network errors or element not found scenarios
6. **Monitor VNC URL** for visual debugging during development

## Error Handling

Common issues and solutions:

- **"E2B_API_KEY 未设置"**: Set the API key in environment or config.py
- **Element not found**: Use `highlight_elements()` to verify element exists
- **Timeout errors**: Increase timeout values for slow-loading pages
- **Connection errors**: Verify E2B_DOMAIN and network connectivity
