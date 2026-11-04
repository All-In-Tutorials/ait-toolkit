
from urllib.parse import urlsplit, urlunsplit

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)

from inspector.credential_input import request_test_credentials
from inspector.portal_config import load_portal_profile
from inspector.test_report import write_login_report


LOGIN_URL = "http://urbanlink.net.ph/urban/urbanlogin.html"
EXPECTED_HOST = "urbanlink.net.ph"


def safe_url(url):
    """Return URL without query parameters or fragments."""
    parsed = urlsplit(url)
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))


def validate_selector(page, selector, role):
    """Require exactly one visible and enabled matching element."""

    if not selector:
        print(f"{role}: selector is not configured.")
        return None

    try:
        locator = page.locator(selector)

        if locator.count() != 1:
            print(f"{role}: selector must match exactly one element.")
            return None

        if not locator.is_visible():
            print(f"{role}: element is not visible.")
            return None

        if not locator.is_enabled():
            print(f"{role}: element is disabled.")
            return None

        print(f"{role}: selector validated.")
        return locator

    except Exception:
        print(f"{role}: selector validation failed.")
        return None


def check_session(page):
    """Check for a configured logout element as session evidence."""

    profile = load_portal_profile(page.url)

    if not profile:
        return "REVIEW REQUIRED"

    selectors = profile.get("selectors", {})
    logout_selector = selectors.get("logout", "")

    logout = validate_selector(page, logout_selector, "Logout indicator")

    if logout:
        return "AUTHENTICATED - logout indicator detected"

    return "REVIEW REQUIRED - no confirmed logout indicator"



def run_login_test():
    print("\n========== AUTHORIZED LOGIN TEST ==========")
    print("Dedicated client test account only.")
    print("The toolkit will submit the form once.")
    print("Credentials will not be printed or saved.")
    print("===========================================\n")

    profile = load_portal_profile(LOGIN_URL)

    if not profile:
        print("No saved portal profile found.")
        return

    selectors = profile.get("selectors", {})

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            channel="chrome",
            headless=False
        )

        page = browser.new_page()
        page.set_default_timeout(10000)

        submission_attempted = False
        click_timed_out = False

        try:
            page.goto(LOGIN_URL, wait_until="domcontentloaded")

            current = urlsplit(page.url)

            if current.scheme != "http" or current.hostname != EXPECTED_HOST:
                print("Unexpected login destination. Test stopped.")
                return

            print("Login page:", safe_url(page.url))

            username = validate_selector(
                page, selectors.get("username", ""), "Username"
            )

            password = validate_selector(
                page, selectors.get("password", ""), "Password"
            )

            login_button = validate_selector(
                page, selectors.get("login", ""), "Login button"
            )

            if not all([username, password, login_button]):
                print("\nLogin test stopped. Fix the saved selectors first.")
                return

            confirmation = input(
                "\nSubmit the authorized test account once? Type YES: "
            ).strip()

            if confirmation != "YES":
                print("Submission cancelled.")
                return

            credentials = request_test_credentials()

            try:
                username.fill(credentials["username"])
                password.fill(credentials["password"])
            finally:
                credentials = None

            print("\nSubmitting the test account once...")

            submission_attempted = True

            try:
                login_button.click(timeout=15000)
            except PlaywrightTimeoutError:
                click_timed_out = True
                print(
                    "The click timed out. Submission may have occurred; "
                    "do not retry automatically."
                )

            try:
                page.wait_for_load_state(
                    "domcontentloaded",
                    timeout=10000
                )
            except PlaywrightTimeoutError:
                pass

            session_assessment = check_session(page)

            print("\n========== LOGIN TEST RESULT ==========")
            print("Final URL:", safe_url(page.url))
            print("Session assessment:", session_assessment)

            report_path = write_login_report(
                initial_url=LOGIN_URL,
                final_url=page.url,
                submission_attempted=submission_attempted,
                session_assessment=session_assessment,
                click_timed_out=click_timed_out
            )

            print("Report saved:", report_path.relative_to(
                report_path.parents[1]
            ))
            print("Credentials were not included in the report.")
            print("=======================================\n")

            input("Inspect the browser, then press Enter to close it...")

        except Exception as error:
            print("\nLogin test stopped.")
            print("Error type:", type(error).__name__)
            print("No automatic retry will be performed.")

        finally:
            browser.close()


if __name__ == "__main__":
    run_login_test()
