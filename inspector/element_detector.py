
def inspect_page(page):
    """Collect read-only information about DOM elements on the page."""

    results = {
        "inputs": [],
        "buttons": [],
        "forms": [],
        "links": [],
    }

    # Detect input fields, text areas, and dropdowns.
    results["inputs"] = page.locator(
        "input, textarea, select"
    ).evaluate_all("""
        elements => elements.map(el => ({
            tag: el.tagName.toLowerCase(),
            type: el.type || "",
            name: el.getAttribute("name") || "",
            id: el.id || "",
            class: el.className || "",
            label: Array.from(el.labels || [])
                .map(label => label.innerText.trim())
                .filter(Boolean).join(", "),
            placeholder: el.getAttribute("placeholder") || "",
            required: el.required,
            disabled: el.disabled
        }))
    """)

    # Detect button elements and input buttons.
    results["buttons"] = page.locator(
        "button, input[type='button'], input[type='submit'], "
        "input[type='reset']"
    ).evaluate_all("""
        elements => elements.map(el => ({
            tag: el.tagName.toLowerCase(),
            type: el.type || "",
            text: (el.innerText || el.value || "").trim(),
            id: el.id || "",
            class: el.className || "",
            disabled: el.disabled
        }))
    """)

    # Detect forms without submitting them.
    results["forms"] = page.locator("form").evaluate_all("""
        elements => elements.map(form => {
            const action = new URL(form.action, document.baseURI);
            return {
                method: (form.method || "get").toUpperCase(),
                action: action.origin + action.pathname,
                id: form.id || "",
                class: form.className || "",
                fields: form.elements.length
            };
        })
    """)

    # Detect links and remove query strings and fragments.
    results["links"] = page.locator("a[href]").evaluate_all("""
        elements => elements.map(link => {
            const url = new URL(link.href, document.baseURI);
            return {
                text: (link.innerText || link.getAttribute("aria-label") || "").trim(),
                url: url.origin + url.pathname,
                id: link.id || "",
                class: link.className || ""
            };
        })
    """)

    return results


def print_inspection(results):
    """Print collected DOM information in a readable format."""

    sections = [
        ("INPUT ELEMENTS", "inputs"),
        ("BUTTON ELEMENTS", "buttons"),
        ("FORMS", "forms"),
        ("LINKS", "links"),
    ]

    print("\n========== PORTAL INSPECTION ==========")

    for title, key in sections:
        print(f"\n--- {title} ---")

        elements = results[key]

        if not elements:
            print("No elements detected.")
            continue

        for index, element in enumerate(elements, start=1):
            print(f"[{index}]")

            for field, value in element.items():
                if value != "" and value is not None:
                    print(f"    {field}: {value}")

    print("\n========== INSPECTION COMPLETE ==========")
