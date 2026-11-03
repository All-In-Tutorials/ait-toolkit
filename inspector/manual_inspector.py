
from playwright.sync_api import sync_playwright

from .element_detector import inspect_page, print_inspection
from .candidate_detector import detect_candidates, print_candidates

from .portal_config import (
    PORTAL_ROLES,
    confirm_candidates,
    save_portal_config,
    load_portal_profile,
    display_saved_selectors,
    verify_saved_selectors,
)


def print_quick_summary(active_selectors, verification):
    print("\n========== INSPECTION SUMMARY ==========")

    for role in PORTAL_ROLES:
        selector = active_selectors.get(role)

        if selector:
            print(f"{role.upper()}: Reused or confirmed")
            print(f"    Selector: {selector}")
        else:
            result = verification.get(role)

            if result and not result.get("valid"):
                print(f"{role.upper()}: Needs configuration")
            else:
                print(f"{role.upper()}: Not configured")

    print("========================================")


def main():
    url = input("Enter authorized portal URL: ").strip()

    if not url.startswith(("http://", "https://")):
        print("Please enter a complete HTTP or HTTPS URL.")
        return

    mode = input(
        "\nChoose inspection mode:\n"
        "[Q] Quick inspection (default)\n"
        "[F] Full inspection\n"
        "Your choice: "
    ).strip().lower()

    full_mode = mode in ("f", "full")

    if mode not in ("", "q", "quick", "f", "full"):
        print("Invalid choice. Using Quick inspection.")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",
            headless=False
        )

        page = browser.new_page()

        try:
            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            input(
                "\nInspect the loaded page in Chrome. "
                "Press ENTER here when ready..."
            )

            profile = load_portal_profile(url)

            verification = {}
            reusable_selectors = {}

            if profile:
                verification = verify_saved_selectors(
                    page,
                    profile
                )

                reusable_selectors = {
                    role: result["selector"]
                    for role, result in verification.items()
                    if result.get("valid")
                }

                if full_mode:
                    display_saved_selectors(profile, url)
                    print("\nValid saved selectors:")
                    for role, selector in reusable_selectors.items():
                        print(f"{role.upper()}: {selector}")

                else:
                    print("\n========== SAVED SELECTORS ==========")
                    print(f"Portal: {url}")

                    for role in PORTAL_ROLES:
                        selector = reusable_selectors.get(role)

                        if selector:
                            print(f"{role.upper()}: VALID")
                        else:
                            print(f"{role.upper()}: NOT CONFIGURED OR INVALID")

                    print("=====================================")

            else:
                print("\nNo saved configuration found for this page.")

            # Determine which roles still need configuration.
            if full_mode:
                roles_to_detect = set(PORTAL_ROLES)
            else:
                roles_to_detect = (
                    set(PORTAL_ROLES) - set(reusable_selectors)
                )

            confirmed = {}

            # Skip DOM inspection and candidate detection when all
            # roles are already configured in Quick mode.
            if roles_to_detect:
                results = inspect_page(page)

                if full_mode:
                    print_inspection(results)

                candidates = detect_candidates(results)

                candidates_to_process = [
                    candidate
                    for candidate in candidates
                    if candidate["role"].lower() in roles_to_detect
                ]

                if full_mode:
                    print_candidates(candidates_to_process)
                elif candidates_to_process:
                    print("\nCandidates found for unconfigured roles:")
                    print_candidates(candidates_to_process)

                if candidates_to_process:
                    confirmed = confirm_candidates(
                        page,
                        candidates_to_process
                    )

                    if confirmed:
                        save_portal_config(url, confirmed)
                elif not full_mode:
                    print("\nNo new candidates found for unconfigured roles.")

            else:
                print("\nAll configured roles have valid saved selectors.")
                print("DOM inspection and candidate detection skipped.")

            # Combine valid saved selectors and newly confirmed selectors.
            active_selectors = {
                **reusable_selectors,
                **confirmed,
            }

            if full_mode:
                print("\n========== ACTIVE SELECTORS ==========")

                for role, selector in active_selectors.items():
                    print(f"{role.upper()}: {selector}")

                if not active_selectors:
                    print("No active selectors.")

                print("=======================================")
            else:
                print_quick_summary(
                    active_selectors,
                    verification
                )

            input("\nPress ENTER to close Chrome...")

        except Exception as error:
            print("Inspection error:", error)

        finally:
            browser.close()


if __name__ == "__main__":
    main()
