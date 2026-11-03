
import json
from pathlib import Path
from urllib.parse import urlparse


CONFIG_PATH = (
    Path(__file__).resolve().parent.parent
    / "config"
    / "portals.json"
)

PORTAL_ROLES = (
    "username",
    "password",
    "login",
    "logout",
)


def load_config():
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        example_path = CONFIG_PATH.with_name(
            "portals.example.json"
        )

        if example_path.exists():
            CONFIG_PATH.write_text(
                example_path.read_text(encoding="utf-8"),
                encoding="utf-8"
            )
        else:
            return {"portals": {}}

    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as file:
            config = json.load(file)

    except (json.JSONDecodeError, OSError):
        return {"portals": {}}

    if not isinstance(config, dict):
        return {"portals": {}}

    if not isinstance(config.get("portals"), dict):
        return {"portals": {}}

    return config


def get_portal_id(url):
    """Generate a portal identifier from its hostname."""

    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower()

    if not hostname:
        raise ValueError("Could not determine portal hostname.")

    return hostname


def get_profile_id(url):
    """Get the page path used as the configuration profile ID."""

    parsed = urlparse(url)
    return parsed.path.rstrip("/") or "/"


def load_portal_profile(url):
    """Load a saved configuration for a specific portal page."""

    config = load_config()

    portal_id = get_portal_id(url)
    profile_id = get_profile_id(url)

    portal = config["portals"].get(portal_id)

    if not portal:
        return None

    return portal.get("profiles", {}).get(profile_id)


def display_saved_selectors(profile, url):
    """Display selectors saved for a portal page."""

    portal_id = get_portal_id(url)
    profile_id = get_profile_id(url)

    print("\n========== SAVED PORTAL CONFIGURATION ==========")
    print(f"Portal: {portal_id}")
    print(f"Page: {profile_id}")

    selectors = profile.get("selectors", {})

    for role in PORTAL_ROLES:
        selector = selectors.get(role, "")

        if selector:
            print(f"{role.upper()}: {selector}")
        else:
            print(f"{role.upper()}: Not configured")

    print("================================================")


def verify_saved_selectors(page, profile):
    """Check whether saved selectors match exactly one element."""

    results = {}

    print("\n========== SAVED SELECTOR VERIFICATION ==========")

    selectors = profile.get("selectors", {})

    for role in PORTAL_ROLES:
        selector = selectors.get(role, "")

        if not selector:
            results[role] = {
                "selector": "",
                "valid": False,
                "count": 0,
                "status": "NOT CONFIGURED",
            }

            print(f"{role.upper()}: NOT CONFIGURED")
            continue

        try:
            count = page.locator(selector).count()

            if count == 1:
                status = "VALID"
                valid = True
            elif count == 0:
                status = "NOT FOUND"
                valid = False
            else:
                status = "AMBIGUOUS"
                valid = False

        except Exception:
            count = 0
            status = "INVALID SELECTOR"
            valid = False

        results[role] = {
            "selector": selector,
            "valid": valid,
            "count": count,
            "status": status,
        }

        print(f"\n{role.upper()}: {status}")
        print(f"    Selector: {selector}")
        print(f"    Matching elements: {count}")

    print("\n========== VERIFICATION COMPLETE ==========")

    return results


def confirm_candidates(page, candidates):
    """Ask the user to confirm or correct detected selectors."""

    confirmed = {}

    print("\n========== MANUAL SELECTOR CONFIRMATION ==========")

    for candidate in candidates:
        role = candidate["role"].lower()
        suggested = candidate["selector"]

        print(f"\nRole: {role.upper()}")
        print(f"Suggested selector: {suggested}")

        try:
            count = page.locator(suggested).count()
        except Exception:
            count = 0

        print(f"Matching elements: {count}")

        if count == 0:
            print("Suggested selector does not match an element.")
        
        choice = input(
            "Press ENTER to accept, enter a replacement selector, "
            "or type 'skip': "
        ).strip()

        if choice.lower() == "skip":
            continue

        selector = choice or suggested

        try:
            matches = page.locator(selector).count()
        except Exception as error:
            print("Invalid selector:", error)
            continue

        if matches == 0:
            print("Selector not found. Candidate skipped.")
            continue

        if matches > 1:
            print(
                f"Warning: {matches} elements match this selector. "
                "Choose a more specific selector."
            )
            continue

        confirmed[role] = selector
        print(f"Confirmed: {role.upper()}")

    print("\n========== CONFIRMATION COMPLETE ==========")

    return confirmed



def save_portal_config(url, confirmed):
    """Save confirmed selectors for a specific portal page."""

    config = load_config()
    parsed = urlparse(url)

    portal_id = get_portal_id(url)
    profile_id = parsed.path.rstrip("/") or "/"

    portal = config["portals"].setdefault(
        portal_id,
        {
            "base_url": f"{parsed.scheme}://{portal_id}",
            "profiles": {},
        },
    )

    profiles = portal.setdefault("profiles", {})

    profile = profiles.setdefault(
        profile_id,
        {
            "selectors": {
                role: "" for role in PORTAL_ROLES
            },
        },
    )

    selectors = profile.setdefault("selectors", {})

    for role in PORTAL_ROLES:
        selectors.setdefault(role, "")

    selectors.update(confirmed)

    with CONFIG_PATH.open("w", encoding="utf-8") as file:
        json.dump(config, file, indent=4)

    print(f"\nConfiguration saved for: {portal_id}")
    print(f"Page profile: {profile_id}")
    print(f"File: {CONFIG_PATH}")

