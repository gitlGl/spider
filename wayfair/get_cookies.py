from playwright.sync_api import Playwright, sync_playwright, expect
import time,os

current_file_path = os.path.abspath(__file__)
os.chdir(os.path.dirname(current_file_path))  

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto('https://partners.wayfair.com/auth/realms/Partner_Home/protocol/openid-connect/auth?client_id=partner-home-monolith&response_type=code&scope=openid&redirect_uri=https%3A%2F%2Fpartners.wayfair.com%2Fv%2Flogin%2Flogin&state=2c16af53b4a32cc374a87b4fd4f047c8')

  
    time.sleep(30)
    storage = context.storage_state(path="state.json")#保存cookies到文件备用

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)