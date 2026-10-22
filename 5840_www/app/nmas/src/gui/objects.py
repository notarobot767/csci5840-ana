#!/usr/bin/env python3

from flask import request
import dev.creds

# ---------------------------------------------------------
# Reusable Core Renderers
# ---------------------------------------------------------

def render_button(
    name,
    href,
    title,
    target=None,
    rel=None,
    active_mode=None,
    is_active=None,
    variant="primary",
):
    """
    Renders a single Bootstrap button with custom color variant.
    - If `is_active` is explicitly passed (bool), it uses that.
    - Otherwise, falls back to `active_mode` ('prefix' or 'exact').
    - Renders f'btn-{variant}' if active, f'btn-outline-{variant}' if inactive.
    """
    if is_active is None:
        if active_mode == "prefix":
            is_active = request.path.startswith(href)
        elif active_mode == "exact":
            is_active = request.path.endswith(href) or request.path == href
        else:
            is_active = False

    btn_variant = f"btn-{variant}" if is_active else f"btn-outline-{variant}"
    aria_attr = ' aria-current="page"' if is_active else ""

    target_attr = f' target="{target}"' if target else ""
    rel_attr = f' rel="{rel}"' if rel else ""

    return (
        f'<a role="button" class="btn {btn_variant}"'
        f'{aria_attr}{target_attr}{rel_attr} href="{href}" '
        f'data-bs-toggle="tooltip" data-bs-placement="top" title="{title}">'
        f'{name}</a>'
    )

def render_button_group(buttons_data, aria_label):
    """Wraps an iterable of rendered button HTML strings in a btn-group."""
    items = "\n    ".join(buttons_data)
    return (
        f'<div class="btn-group" role="group" aria-label="{aria_label}">\n'
        f'    {items}\n'
        f'</div>\n<br>'
    )

# ---------------------------------------------------------
# Static Button Metadata
# ---------------------------------------------------------

APP_BUTTONS = [
    {
        "name": "Kibana",
        "href": "https://kibana.badcode.app/",
        "title": "Network Visualizer",
        "target": "_blank",
        "rel": "noopener noreferrer"
    },
    {
        "name": "Code",
        "href": "https://code.badcode.app/",
        "title": "VS Code Server",
        "target": "_blank",
        "rel": "noopener noreferrer"
    },
    {
        "name": "Guac",
        "href": "https://guac.badcode.app/guacamole/",
        "title": "Apache Guacamole",
        "target": "_blank",
        "rel": "noopener noreferrer"
    },
    {
        "name": "Device MGMT",
        "href": "/device",
        "title": "Device Management"
    },
    {
        "name": "Roll",
        "href": "/roll/1d20",
        "title": "Roll for initiative",
    }
]

DEVICE_APP_BUTTONS = [
    {"name": "View", "href": "/device/view", "title": "View Devices"},
    {"name": "Add", "href": "/device/add", "title": "Add Device"},
    {"name": "Remove", "href": "/device/remove", "title": "Remove Device"},
    {"name": "Modify", "href": "/device/modify", "title": "Modify Device"},
    {"name": "Unit-Test", "href": "/device/test", "title": "Unit Testing"}
]

DEV_FUNC_BUTTONS = [
    {"name": "Yaml", "title": "YAML Configuration", "location": "yaml"},
    {"name": "OSPF", "title": "OSPF Neighbor Table", "location": "ospf"},
    {"name": "ISIS", "title": "ISIS Neighbor Table", "location": "isis"},
    {"name": "BGP", "title": "BGP Neighbor Table", "location": "bgp"},
    {"name": "Route Table", "title": "Routing Table", "location": "route"},
    {"name": "CPU", "title": "CPU Utilization", "location": "cpu"},
    {"name": "Ping", "title": "Ping Test", "location": "ping"},
    {"name": "TSHOOT", "title": "Troubleshoot Diagnostics", "location": "tshoot"},
]

DEV_CONFIG_BUTTONS = [
    {"name": "Running Config", "title": "Running Configuration", "location": "running"},
    {"name": "Startup Config", "title": "Startup Configuration", "location": "startup"},
    {"name": "Golden Config", "title": "Golden Configuration", "location": "golden"},
]

DEV_DIFF_BUTTONS = [
    {"name": "Start/Run (diff)", "title": "Startup Config vs Running Config Diff", "location": "runstart/diff"},
    {"name": "Run/Golden (diff)", "title": "Running Config vs Golden Config Diff", "location": "running/diff"},
    {"name": "Start/Golden (diff)", "title": "Startup Config vs Golden Config Diff", "location": "startup/diff"},
]

UNIT_TEST = [
    {"name": "Run Tests", "title": "Run all unit tests", "href": "/device/test/runtests"},
    {"name": "Code Coverage", "title": "See test code coverage", "href": "/device/test/codecoverage"}
]

WRITE_CONFIG = [
    {"name": "Write Memory", "title": "Copy running config to startup", "location": "startup/write"},
    {"name": "Write Golden", "title": "Copy startup config to golden", "location": "golden/write"},
    {"name": "Baseline", "title": "Copy golden config to startup", "location": "golden/baseline"},
]

# ---------------------------------------------------------
# Public Generators
# ---------------------------------------------------------

def get_app_buttons():
    """Returns top-level external/internal app buttons."""
    buttons = [render_button(**b) for b in APP_BUTTONS]
    return render_button_group(buttons, "App Navigation")


def get_dev_app_buttons():
    """Returns CRUD device management buttons (View, Add, Remove, Modify)."""
    buttons = [
        render_button(**b, active_mode="prefix") 
        for b in DEVICE_APP_BUTTONS
    ]
    return render_button_group(buttons, "Device Management Actions")


def get_device_view_buttons(func="view",current_device=None):
    """
    Fetches registered devices from dev.creds.get_devices() and generates
    a button for each.
    
    Active if:
    1. current_device matches item, OR
    2. request.path is /device/view/<item> or begins with /device/view/<item>/
    """
    devices = dev.creds.get_devices()
    buttons = []

    for item in devices:
        item_path = f"/device/{func}/{item}"
        
        # Matches /device/view/r1 exactly OR any sub-route like /device/view/r1/ospf
        is_active = (
            item == current_device
            or request.path == item_path
            or request.path.startswith(f"{item_path}/")
        )

        buttons.append(
            render_button(
                name=item,
                title=f"{func} {item}",
                href=item_path,
                is_active=is_active,
                variant="secondary"
            )
        )

    return render_button_group(buttons, "Device View Actions")

def get_dev_func_buttons(device):
    """Returns function actions, configs, diffs, and write buttons for a specific device."""
    def _build_button(b, variant="primary"):
        return render_button(
            name=b["name"],
            title=b["title"],
            href=f"/device/view/{device}/{b['location']}",
            active_mode="exact",
            variant=variant,
        )

    func_group = render_button_group(
        [_build_button(b) for b in DEV_FUNC_BUTTONS],
        "Device Configuration Actions",
    )
    config_group = render_button_group(
        [_build_button(b) for b in DEV_CONFIG_BUTTONS],
        "Device Config Actions",
    )
    diff_group = render_button_group(
        [_build_button(b, variant="warning") for b in DEV_DIFF_BUTTONS],
        "Device Diff Actions",
    )
    write_group = render_button_group(
        [_build_button(b, variant="danger") for b in WRITE_CONFIG],
        "Device Write Actions",
    )

    return f"{func_group}\n{config_group}\n{diff_group}\n{write_group}"

def get_write_config_buttons(device):
    """Returns the write/sync configuration action buttons for a device in red."""
    buttons = [
        render_button(
            name=b["name"],
            title=b["title"],
            href=f"/device/view/{device}/{b['location']}",
            active_mode="exact",
            variant="danger",
        )
        for b in WRITE_CONFIG
    ]
    return render_button_group(buttons, "Device Write Config Actions")

def get_unit_test_buttons():
    """Returns the action buttons for Unit Testing (Run Tests, Code Coverage)."""
    buttons = [
        render_button(**b, active_mode="exact")
        for b in UNIT_TEST
    ]
    return render_button_group(buttons, "Unit Test Actions")

def main():
    pass

if __name__ == "__main__":
    main()