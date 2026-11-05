
from urllib.parse import urlsplit

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)

from inspector.credential_input import request_test_credentials
from inspector.portal_config import load_portal_profile
from inspector.login_tester import validate_selector, safe_url
from inspector.test_report import write_logout_report


LOGIN_URL = "http://urbanlink.net.ph/urban/urbanlogin.html"
EXPECTED_HOST = "urbanlink.net.ph"



def verify_logged_out(page):
    """
    Verify logout by requesting the protected status page.
    A redirect to the login page is evidence of session invalidation.
    """

    protected_url = "http://urbanlink.net.ph/urban/status"

    try:
        page.goto(
            protected_url,
            wait_until="domcontentloaded",
            timeout=15000
        )

        current = urlsplit(page.url)

        if current.hostname != EXPECTED_HOST:
            return "REVIEW REQUIRED - unexpected host"

        if current.path in (
            "/urban/urbanlogin.html",
            "/urban/login"
        ):
            return "LOGGED OUT - protected page redirected to login"

        return "REVIEW REQUIRED - protected page remains accessible"

    except PlaywrightTimeoutError:
        return "REVIEW REQUIRED - verification timed out"


def run_logout_test():

    login_attempted = False
    logout_attempted = False
    print("\n========== AUTHORIZED LOGOUT TEST ==========")
    print("Dedicated client test account only.")
    print("Login and logout will use the same browser session.")
    print("Logout will be clicked once.")
    print("=============================================\n")

    login_profile = load_portal_profile(LOGIN_URL)

    if not login_profile:
        print("Login profile not found.")
        return

    login_selectors = login_profile.get("selectors", {})

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            channel="chrome",
            headless=False
        )

        page = browser.new_page()
        page.set_default_timeout(10000)

        try:
            page.goto(LOGIN_URL, wait_until="domcontentloaded")

            current = urlsplit(page.url)

            if current.scheme != "http" or current.hostname != EXPECTED_HOST:
                print("Unexpected login destination. Test stopped.")
                return

            username = validate_selector(
                page, login_selectors.get("username", ""), "Username"
            )

            password = validate_selector(
                page, login_selectors.get("password", ""), "Password"
            )

            login_button = validate_selector(
                page, login_selectors.get("login", ""), "Login button"
            )

            if not all([username, password, login_button]):
                print("Login selectors are invalid. Test stopped.")
                return

            confirmation = input(
                "\nLog in with the authorized test account? Type YES: "
            ).strip()

            if confirmation != "YES":
                print("Test cancelled.")
                return

            credentials = request_test_credentials()

            try:
                username.fill(credentials["username"])
                password.fill(credentials["password"])
            finally:
                credentials = None

            print("\nSubmitting authorized login once...")

            login_attempted = True

            login_button.click(timeout=15000)

            try:
                page.wait_for_load_state(
                    "domcontentloaded",
                    timeout=10000
                )
            except PlaywrightTimeoutError:
                pass

            authenticated_profile = load_portal_profile(page.url)

            if not authenticated_profile:
                print("Authenticated page profile not found.")
                return

            logout_selector = authenticated_profile.get(
                "selectors", {}
            ).get("logout", "")

            logout_button = validate_selector(
                page, logout_selector, "Logout button"
            )

            if not logout_button:
                print("Logout control could not be validated.")
                return

            print("\nAuthenticated page:", safe_url(page.url))

            confirmation = input(
                "\nClick logout once? Type YES: "
            ).strip()

            if confirmation != "YES":
                print("Logout cancelled. Browser session remains open.")
                return

            print("\nClicking logout once...")

            try:
                logout_attempted = True
                logout_button.click(timeout=15000)
            except PlaywrightTimeoutError:
                print(
                    "Logout click timed out. The action may have occurred. "
                    "Do not retry automatically."
                )

            try:
                page.wait_for_load_state(
                    "domcontentloaded",
                    timeout=10000
                )
            except PlaywrightTimeoutError:
                pass

            print("\n========== LOGOUT TEST RESULT ==========")
            print("Final URL:", safe_url(page.url))

            logout_destination = page.url
            logout_assessment = verify_logged_out(page)

            print("Logout assessment:", logout_assessment)
            print("========================================\n")

            report_path = write_logout_report(
                initial_url=LOGIN_URL,
                final_url=logout_destination,
                login_attempted=login_attempted,
                logout_attempted=logout_attempted,
                logout_assessment=logout_assessment
            )

            print("Logout report saved:", report_path)
            print("Credentials recorded: False")

            input("Inspect the browser, then press Enter to close it...")

        except Exception as error:
            print("\nLogout test stopped.")
            print("Error type:", type(error).__name__)
            print("No automatic retry will be performed.")

        finally:
            browser.close()


if __name__ == "__main__":
    run_logout_test()
