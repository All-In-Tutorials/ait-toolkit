
import re


def make_selector(element):
    """Build a practical CSS selector from available attributes."""

    tag = element.get("tag", "")
    element_id = element.get("id", "")
    name = element.get("name", "")
    field_type = element.get("type", "")
    class_name = element.get("class", "")

    if element_id and re.fullmatch(
        r"[A-Za-z_][A-Za-z0-9_-]*", element_id
    ):
        return f"#{element_id}"

    if name:
        safe_name = name.replace("\\", "\\\\").replace('"', '\\"')
        return f'{tag}[name="{safe_name}"]'

    selector = tag or "*"

    if field_type:
        selector += f'[type="{field_type}"]'

    for class_token in class_name.split():
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", class_token):
            selector += f".{class_token}"

    return selector


def detect_candidates(results):
    """Suggest likely portal element purposes using DOM metadata."""

    candidates = []

    # Analyze input fields.
    for element in results.get("inputs", []):
        searchable = " ".join([
            element.get("name", ""),
            element.get("id", ""),
            element.get("label", ""),
            element.get("placeholder", ""),
        ]).lower()

        field_type = element.get("type", "").lower()

        # Username candidate.
        username_score = 0
        username_reasons = []

        if re.search(r"username|user_name|user|login", searchable):
            username_score += 3
            username_reasons.append("Username-related attribute")

        if field_type == "email":
            username_score += 2
            username_reasons.append("Email input type")

        if username_score >= 3:
            candidates.append({
                "role": "USERNAME",
                "selector": make_selector(element),
                "element": element,
                "score": username_score,
                "reasons": username_reasons,
            })

        # Password candidate.
        password_score = 0
        password_reasons = []

        if field_type == "password":
            password_score += 4
            password_reasons.append("Password input type")

        if re.search(r"password|passwd|pass_word", searchable):
            password_score += 3
            password_reasons.append("Password-related attribute")

        if password_score >= 3:
            candidates.append({
                "role": "PASSWORD",
                "selector": make_selector(element),
                "element": element,
                "score": password_score,
                "reasons": password_reasons,
            })

    # Analyze buttons and submit controls.
    for element in results.get("buttons", []):
        searchable = " ".join([
            element.get("text", ""),
            element.get("id", ""),
            element.get("class", ""),
        ]).lower()

        role = None
        score = 0
        reasons = []

        if re.search(r"log[\s_-]*out|logout|logoff|sign[\s_-]*out", searchable):
            role = "LOGOUT"
            score = 4
            reasons.append("Logout-related label or attribute")

        elif re.search(
            r"log[\s_-]*in|login|sign[\s_-]*in|authenticate|connect",
            searchable
        ):
            role = "LOGIN"
            score = 4
            reasons.append("Login-related label or attribute")

        if role:
            candidates.append({
                "role": role,
                "selector": make_selector(element),
                "element": element,
                "score": score,
                "reasons": reasons,
            })

    return candidates


def print_candidates(candidates):
    """Display suggested element purposes."""

    print("\n========== CANDIDATE DETECTION ==========")

    if not candidates:
        print("No likely username, password, login, or logout elements found.")

    for index, candidate in enumerate(candidates, start=1):
        element = candidate["element"]

        if candidate["score"] >= 4:
            confidence = "Strong match"
        else:
            confidence = "Possible match"

        print(f"\n[{index}] {candidate['role']} CANDIDATE")
        print(f"    Selector: {candidate['selector']}")
        print(f"    Element: {element.get('tag', 'unknown')}")
        print(f"    Type: {element.get('type', 'unknown')}")
        print(f"    Confidence: {confidence}")

        if element.get("type") == "hidden":
            print("    Note: Hidden field; manual confirmation required.")

        for reason in candidate["reasons"]:
            print(f"    Reason: {reason}")

    print("\nManual confirmation is required.")
    print("========== CANDIDATE DETECTION COMPLETE ==========")
