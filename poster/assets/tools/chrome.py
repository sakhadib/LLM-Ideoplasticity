"""Small helpers: print an HTML file to PDF and screenshot it with headless Chrome via Playwright."""
import pathlib

from playwright.sync_api import sync_playwright


def html_to_pdf(html_path, pdf_path, width_mm, height_mm, wait_js=None, timeout=120000):
    url = pathlib.Path(html_path).resolve().as_uri()
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel='chrome')
        except Exception:
            browser = p.chromium.launch(channel='msedge')
        page = browser.new_page()
        msgs = []
        page.on('console', lambda m: msgs.append(m.text))
        page.on('pageerror', lambda e: msgs.append('PAGEERROR ' + str(e)))
        page.on('requestfailed', lambda r: msgs.append('REQFAILED ' + r.url[:120]))
        page.goto(url, wait_until='networkidle', timeout=timeout)
        page.evaluate('document.fonts.ready')
        if wait_js:
            page.wait_for_function(wait_js, timeout=timeout)
        page.pdf(path=str(pdf_path), width=f'{width_mm}mm', height=f'{height_mm}mm', print_background=True,
                 prefer_css_page_size=True, margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'})
        browser.close()
    return msgs


def html_to_png(html_path, png_path, width_px, height_px, scale=1, omit_background=False, wait_js=None, timeout=120000):
    url = pathlib.Path(html_path).resolve().as_uri()
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel='chrome')
        except Exception:
            browser = p.chromium.launch(channel='msedge')
        ctx = browser.new_context(viewport={'width': width_px, 'height': height_px}, device_scale_factor=scale)
        page = ctx.new_page()
        page.goto(url, wait_until='networkidle', timeout=timeout)
        page.evaluate('document.fonts.ready')
        if wait_js:
            page.wait_for_function(wait_js, timeout=timeout)
        page.screenshot(path=str(png_path), omit_background=omit_background)
        browser.close()
