
from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",
            headless=False
        )

        page = browser.new_page()

        print("Chrome launched successfully!")
        print("Opening a test page...")

        page.goto("https://example.com")

        print("Page title:", page.title())
        input("Press ENTER to close Chrome...")

        browser.close()


if __name__ == "__main__":
    main()
