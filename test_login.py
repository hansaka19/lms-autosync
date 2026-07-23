from playwright.sync_api import sync_playwright
from lms_autosync import auth

with sync_playwright() as pw:
    browser, context, page = auth.login(pw)
    print("Login OK - current URL:", page.url)
    browser.close()