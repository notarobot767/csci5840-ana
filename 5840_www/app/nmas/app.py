#!/usr/bin/env python3

import dev.mgmt
import dev.show
import dev.creds
import gui.objects

import razzledazzle
import file_object


from flask import Flask, render_template, redirect, jsonify, abort, url_for, flash, request
from random import choice, randint

app=Flask(__name__)

app.secret_key = file_object.read_file("./secrets/flask.key").strip()
app.add_template_global(razzledazzle.motto, name="motto")

@app.route("/")
def index():
    return render_template(
        "template.html",
        title="Bad Code",
        h1="Bad Code",
        comp1_func=gui.objects.get_app_buttons(),
        comp2_template=razzledazzle.ascii_page()
    )

def _is_safe_devices(devices) -> bool:
    return devices and len(devices) > 0

def _is_safe_device(device) -> bool:
    devices = dev.creds.get_devices()
    return _is_safe_devices(devices) and device and device in devices

@app.route("/device")
def device():
    return redirect(url_for("device_view"))

@app.route("/device/view")
def device_view():
    devices = dev.creds.get_devices()
    if _is_safe_devices(devices):
        return redirect(url_for("device_view_device_yaml", device=devices[0]))
    return redirect(url_for("index"))

def _no_such_device(device):
    if not device:
        device = None
    return render_template(
        "template.html",
        title="view",
        h1=f"Error!",
        comp1_func=gui.objects.get_dev_app_buttons(),
        comp2_func=gui.objects.get_device_view_buttons(),
        comp3_func=f'<br><h2>No such device!<br>"{device}"</h2>'
    )

@app.route("/device/view/<device>")
def device_view_device(device):    
    if _is_safe_device(device):
        return redirect(url_for("device_view_device_yaml", device=device))
    return _no_such_device(device)

def _render_device_funct(device, content, label):
    if _is_safe_device(device):
        return render_template(
            "template.html",
            title="view",
            h1=f"View Device: {device}",
            comp1_func=gui.objects.get_dev_app_buttons(),
            comp2_func=gui.objects.get_device_view_buttons(),
            comp3_func=gui.objects.get_dev_func_buttons(device),
            comp4_template="components/numbered_content.html",
            content=content,
            device=device,
            label=label
        )
    return _no_such_device(device)

@app.route("/device/view/<device>/yaml")
def device_view_device_yaml(device):
    content = dev.mgmt.get_device_yaml(device)
    label = "yaml"
    return _render_device_funct(device, content, label)

@app.route("/device/view/<device>/ospf")
def device_view_device_ospf(device):
    content = dev.show.get_ospf_neighbors(device)
    label = "ospf"
    return _render_device_funct(device, content, label)

@app.route("/device/view/<device>/bgp")
def device_view_device_bgp(device):
    content = dev.show.get_bgp_neighbors(device)
    label = "bgp"
    return _render_device_funct(device, content, label)

@app.route("/device/view/<device>/route")
def device_view_device_route(device):
    content = dev.show.get_route_table(device)
    label = "route table"
    return _render_device_funct(device, content, label)

@app.route("/device/view/<device>/cpu")
def device_view_device_cpu(device):
    content = dev.show.get_device_cpu(device)
    label = "cpu"
    return _render_device_funct(device, content, label)

@app.route("/device/view/<device>/ping")
def device_view_device_ping(device):
    content = dev.show.get_ping(device)
    label = "ping"
    return _render_device_funct(device, content, label)

@app.route("/device/view/<device>/tshoot")
def device_view_device_tshoot(device):
    content = "TODO"
    label = "tshoot"
    return _render_device_funct(device, content, label)

@app.route("/device/view/<device>/running")
def device_view_device_running(device):
    content = dev.show.get_running(device)
    label = "running"
    return _render_device_funct(device, content, label)

@app.route("/device/view/<device>/startup")
def device_view_device_startup(device):
    content = dev.show.get_startup(device)
    label = "startup"
    return _render_device_funct(device, content, label)

@app.route("/device/view/<device>/golden")
def device_view_device_golden(device):
    content = dev.show.get_golden(device)
    label = "golden"
    return _render_device_funct(device, content, label)

def _render_device_diff(device, left_cfg, right_cfg, left_label, right_label, diff_tag):
    diff_rows = dev.show.build_side_by_side_diff(left_cfg, right_cfg)
    return render_template(
        "template.html",
        title="diff",
        h1=f"View Device: {device} ({diff_tag.title()} Diff)",
        comp1_func=gui.objects.get_dev_app_buttons(),
        comp2_func=gui.objects.get_device_view_buttons(),
        comp3_func=gui.objects.get_dev_func_buttons(device),
        comp4_template="components/diff_content.html",
        diff_rows=diff_rows,
        device=device,
        label=diff_tag,
        left_label=left_label,
        right_label=right_label,
    )

@app.route("/device/view/<device>/runstart/diff")
def device_view_device_startup_running_diff(device):
    startup_cfg = dev.show.get_startup(device)
    running_cfg = dev.show.get_running(device)
    return _render_device_diff(
        device=device,
        left_cfg=startup_cfg, left_label="Startup Config",
        right_cfg=running_cfg, right_label="Running Config",
        diff_tag="startup/running diff"
    )

@app.route("/device/view/<device>/running/diff")
def device_view_device_running_diff(device):
    golden_cfg = dev.show.get_golden(device)
    running_cfg = dev.show.get_running(device)
    return _render_device_diff(
        device=device,
        left_cfg=golden_cfg, left_label="Golden Config",
        right_cfg=running_cfg, right_label="Running Config",
        diff_tag="running diff"
    )

@app.route("/device/view/<device>/startup/diff")
def device_view_device_startup_diff(device):
    golden_cfg = dev.show.get_golden(device)
    startup_cfg = dev.show.get_startup(device)
    return _render_device_diff(
        device=device,
        left_cfg=golden_cfg, left_label="Golden Config",
        right_cfg=startup_cfg, right_label="Startup Config",
        diff_tag="startup diff"
    )

@app.route("/device/add", methods=["GET", "POST"])
def device_add():
    vendors = [
        ("cisco_ios", "Cisco IOS"),
        ("cisco_xe", "Cisco IOS-XE"),
        ("cisco_xr", "Cisco IOS-XR"),
        ("juniper_junos", "Juniper Junos"),
        ("arista_eos", "Arista EOS")
    ]
    templates = ["ce", "pe", "core", "access"]

    if request.method == "POST":
        hostname = request.form.get("hostname", "").strip()
        ipv6 = request.form.get("ipv6", "").strip()
        vendor = request.form.get("vendor", "").strip()
        template = request.form.get("template", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not all([hostname, ipv6, vendor, template, username, password]):
            flash("All fields are required.", "danger")
        else:
            success, err = dev.mgmt.add_device(
                hostname=hostname,
                ipv6_addr=ipv6,
                vendor=vendor,
                template=template,
                username=username,
                password=password
            )
            if success:
                flash(f"Device '{hostname}' added successfully!", "success")
                return redirect(url_for("device_add"))
            else:
                flash(err, "warning")

    return render_template(
        "template.html",
        title="Add Device",
        h1="Add Device",
        comp1="components/dev_mgmt/app_buttons.html",
        comp2="components/dev_mgmt/add.html",
        vendors=vendors,
        templates=templates
    )

@app.route("/device/remove")
def device_remove():
    device_list = dev.mgmt.get_device_list()
    if device_list:
        return redirect(url_for("device_remove_device", device=device_list[0]))

    flash("No devices available to remove.", "warning")
    return render_template(
        "template.html",
        title="Remove Device",
        h1="Remove Device",
        comp1="components/dev_mgmt/app_buttons.html"
    )

@app.route("/device/remove/<device>", methods=["GET", "POST"])
def device_remove_device(device):
    devices = dev.mgmt.get_device_list()

    if request.method == "POST":
        success, err = dev.mgmt.remove_device(device)
        if success:
            flash(f"Device '{device}' was successfully removed.", "success")
            return redirect(url_for("device_remove"))
        else:
            flash(err or f"Failed to remove device '{device}'.", "danger")

    if device not in devices:
        flash(f"Device '{device}' does not exist.", "warning")
        return redirect(url_for("device_remove"))

    return render_template(
        "template.html",
        title="Remove Device",
        h1=f"Remove Device: {device}",
        comp1="components/dev_mgmt/app_buttons.html",
        comp2="components/dev_mgmt/device_buttons_remove.html",
        comp3="components/dev_mgmt/device_buttons_view_function_yaml.html",
        comp4="components/dev_mgmt/device_remove_prompt.html",
        device=device,
        devices=devices,
        yaml_content=dev.mgmt.get_device_yaml(device)
    )

@app.route("/device/modify")
def device_modify():
    device_list = dev.mgmt.get_device_list()
    if device_list:
        return redirect(url_for("device_modify_device", device=device_list[0]))

    flash("No devices available to modify.", "warning")
    return render_template(
        "template.html",
        title="Modify Device",
        h1="Modify Device",
        comp1="components/dev_mgmt/app_buttons.html"
    )

@app.route("/device/modify/<device>", methods=["GET", "POST"])
def device_modify_device(device):
    devices = dev.mgmt.get_device_list()

    if device not in devices:
        flash(f"Device '{device}' does not exist.", "warning")
        return redirect(url_for("device_modify"))

    if request.method == "POST":
        raw_yaml = request.form.get("raw_yaml", "")
        success, err = dev.mgmt.update_device_from_yaml(device, raw_yaml)
        if success:
            flash(f"Device '{device}' configuration updated successfully!", "success")
        else:
            flash(err, "danger")
        return redirect(url_for("device_modify_device", device=device))

    raw_content = dev.mgmt.get_device_raw_combined_yaml(device)

    return render_template(
        "template.html",
        title="Modify Device",
        h1=f"Modify Device: {device}",
        comp1="components/dev_mgmt/app_buttons.html",
        comp2="components/dev_mgmt/device_buttons_modify.html",
        comp3="components/dev_mgmt/device_modify_form.html",
        device=device,
        devices=devices,
        raw_yaml_content=raw_content
    )

@app.route("/roll/<int:num>d<int:sides>")
def roll(num, sides):
    if num < 1 or sides < 1:
        abort(400, description="Number of dice and sides must be >= 1")
    if num > 100 or sides > 1000:
        abort(400, description="Dice limits exceeded")
    rolls = [randint(1, sides) for _ in range(num)]
    return jsonify({
        "dice": f"{num}d{sides}",
        "roll": rolls,
        "total": sum(rolls)
    })
    
def main():
    app.debug = True
    app.run(host="0.0.0.0", threaded=True)

if __name__ == "__main__":
    main()