#!/usr/bin/env python3

import device_mgmt

from flask import Flask, render_template, redirect, jsonify, abort, url_for, flash, request
from random import choice, randint

app=Flask(__name__)

app.secret_key = "dev-secret-key-change-in-production"

def motto():
    return choice([
        "Prepare for War",
        "Command, Communicate",
        "Ready Lightning",
        "Totus Pro Patria",
        "Knowledge Unity Speed",
        "Together We Will",
        "Ready Anywhere Anytime",
        "We Serve To Honor",
        "Pro Patria Vigilans"
    ])
app.add_template_global(motto)

@app.route("/")
def index():
    ascii_art = f"components/{choice([
        "ascii_choppers",
        "ascii_computer_big_dog",
        "ascii_mecha",
        "ascii_castle"
    ])}.html"

    return render_template(
        "template.html",
        title="Bad Code",
        h1="Bad Code",
        comp1="components/app_buttons.html",
        comp2=ascii_art
    )

@app.route("/device")
def device():
    return redirect(url_for("device_view"))

@app.route("/device/view")
def device_view():
    device_list = device_mgmt.get_device_list()
    if device_list:
        return redirect(url_for("device_view_device_yaml", device=device_list[0]))
    return redirect(url_for("device"))

@app.route("/device/view/<device>")
def device_view_device(device):
    return redirect(url_for("device_view_device_yaml", device=device))

@app.route("/device/view/<device>/yaml")
def device_view_device_yaml(device):
    devices = device_mgmt.get_device_list()
    if device and device in devices:
        return render_template(
            "template.html",
            device=device,
            devices=devices,
            title="view",
            h1=f"View Device: {device}",
            config_type="yaml",
            comp1="components/dev_mgmt/app_buttons.html",
            comp2="components/dev_mgmt/device_buttons_view.html",
            comp3="components/dev_mgmt/device_buttons_view_function.html",
            comp4="components/dev_mgmt/device_buttons_view_function_yaml.html",
            yaml_content=device_mgmt.get_device_yaml(device),
            device_data=device_mgmt.get_devices().get(device, {}),
        )
    return render_template(
        "template.html",
        title="view",
        h1=f"View Device: {device}",
    )

@app.route("/device/view/<device>/startup")
def device_view_device_startup(device):
    devices = device_mgmt.get_device_list()
    if device not in devices:
        flash(f"Device '{device}' does not exist.", "warning")
        return redirect(url_for("device_view"))

    success, result = device_mgmt.get_device_startup_config(device)

    if not success:
        flash(result, "danger")
        config_content = f"! Error retrieving configuration via SSH:\n! {result}"
    else:
        config_content = result

    return render_template(
        "template.html",
        device=device,
        devices=devices,
        title="view",
        h1=f"View Device: {device}",
        config_type="startup",
        comp1="components/dev_mgmt/app_buttons.html",
        comp2="components/dev_mgmt/device_buttons_view.html",
        comp3="components/dev_mgmt/device_buttons_view_function.html",
        comp4="components/dev_mgmt/device_buttons_view_function_startup.html",
        config_content=config_content,
        device_data=device_mgmt.get_devices().get(device, {})
    )

@app.route("/device/view/<device>/running")
def device_view_device_running(device):
    devices = device_mgmt.get_device_list()
    if device not in devices:
        flash(f"Device '{device}' does not exist.", "warning")
        return redirect(url_for("device_view"))

    success, result = device_mgmt.get_device_running_config(device)

    if not success:
        flash(result, "danger")
        config_content = f"! Error retrieving configuration via SSH:\n! {result}"
    else:
        config_content = result

    return render_template(
        "template.html",
        device=device,
        devices=devices,
        title="view",
        h1=f"View Device: {device}",
        config_type="running",
        comp1="components/dev_mgmt/app_buttons.html",
        comp2="components/dev_mgmt/device_buttons_view.html",
        comp3="components/dev_mgmt/device_buttons_view_function.html",
        comp4="components/dev_mgmt/device_buttons_view_function_running.html",
        config_content=config_content,
        device_data=device_mgmt.get_devices().get(device, {})
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
            success, err = device_mgmt.add_device(
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
    device_list = device_mgmt.get_device_list()
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
    devices = device_mgmt.get_device_list()

    if request.method == "POST":
        success, err = device_mgmt.remove_device(device)
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
        yaml_content=device_mgmt.get_device_yaml(device)
    )

@app.route("/device/modify")
def device_modify():
    device_list = device_mgmt.get_device_list()
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
    devices = device_mgmt.get_device_list()

    if device not in devices:
        flash(f"Device '{device}' does not exist.", "warning")
        return redirect(url_for("device_modify"))

    if request.method == "POST":
        raw_yaml = request.form.get("raw_yaml", "")
        success, err = device_mgmt.update_device_from_yaml(device, raw_yaml)
        if success:
            flash(f"Device '{device}' configuration updated successfully!", "success")
        else:
            flash(err, "danger")
        return redirect(url_for("device_modify_device", device=device))

    raw_content = device_mgmt.get_device_raw_combined_yaml(device)

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
    app.run(host="0.0.0.0")

if __name__ == "__main__":
    main()