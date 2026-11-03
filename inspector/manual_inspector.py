
from playwright.sync_api import sync_playwright
from .element_detector import inspect_page, print_inspection


def main():
    url = input("Enter authorized portal URL: ").strip()

    if not url.startswith(("http://", "https://")):
        print("Please enter a complete HTTP or HTTPS URL.")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",
            headless=False
        )

        page = browser.new_page()

        try:
            # Open the authorized portal.
            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            # Allow manual inspection before collecting DOM data.
            input(
                "\nInspect the loaded page in Chrome. "
                "Press ENTER here when ready..."
            )

            # Collect and display DOM information.
            results = inspect_page(page)
            print_inspection(results)

            input("\nPress ENTER to close Chrome...")

        except Exception as error:
            print("Inspection error:", error)

        finally:
            browser.close()


if __name__ == "__main__":
    main()
