from playwright.sync_api import sync_playwright

def open_browser(headless=False):
    p = sync_playwright().start()
    browser = p.firefox.launch(headless=headless)
    page = browser.new_page()
    return page
    