
from playwright.sync_api import sync_playwright


def inspect_portal(page):
    elements = page.locator(
        "input, button, select, textarea, a"
    ).evaluate_all("""
        elements => elements.map((el, index) => ({
            index: index + 1,
            tag: el.tagName.toLowerCase(),
            type: el.getAttribute('type') || '',
            name: el.getAttribute('name') || '',
            id: el.id || '',
            className: typeof el.className === 'string'
                ? el.className : '',
            text: (el.innerText || el.value || '').trim(),
            placeholder: el.getAttribute('placeholder') || '',
            href: el.getAttribute('href') || ''
        }))
    """)

    print("\\n========== PORTAL INSPECTION ==========")

    for item in elements:
        description = (
            item["text"]
            or item["placeholder"]
            or item["name"]
            or "(no label)"
        )

        print(
            f'[{item["index"]}] '
            f'{item["tag"]} | '
            f'{item["type"]} | '
            f'{description}'
        )

        if item["name"]:
            print(f'    name="{item["name"]}"')

        if item["id"]:
            print(f'    id="{item["id"]}"')

        if item["className"]:
            print(f'    class="{item["className"]}"')

    print("\\n========== INSPECTION COMPLETE ==========")


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
            page.goto(url, wait_until="domcontentloaded", timeout=30000)

            input(
                "\\nInspect the loaded page in Chrome. "
                "Press ENTER here when ready..."
            )

            inspect_portal(page)

            input("\\nPress ENTER to close Chrome...")

        except Exception as error:
            print("Inspection error:", error)

        finally:
            browser.close()


if __name__ == "__main__":
    main()
