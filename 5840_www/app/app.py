#!/usr/bin/env python3

import device_mgmt

from flask import Flask, render_template, redirect, jsonify, abort, url_for
from random import choice, randint

app=Flask(__name__)

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

    #ascii_art = "components/ascii_castle.html"

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
            comp1="components/dev_mgmt/app_buttons.html",
            comp2="components/dev_mgmt/device_buttons_view.html",
            comp3="components/dev_mgmt/device_buttons_view_function_yaml.html",
            yaml_content=device_mgmt.get_device_yaml(device),
            device_data=device_mgmt.get_devices().get(device, {}),
        )
    return render_template(
        "template.html",
        title="view",
        h1=f"View Device: {device}",
    )

@app.route("/device/add")
def device_add():
    return render_template(
        "template.html",
        title="add",
        h1="Add Device",
        comp1="components/dev_mgmt/app_buttons.html"
    )

@app.route("/device/remove")
def device_remove():
    return render_template(
        "template.html",
        title="remove",
        h1="Remove Device",
        comp1="components/dev_mgmt/app_buttons.html",
        comp2="components/dev_mgmt/device_buttons_remove.html",
        devices=device_mgmt.get_device_list(),
        selected_device=device_mgmt.get_device_list()[0]
    )

@app.route("/device/modify")
def device_modify():
    return render_template(
        "template.html",
        title="modify",
        h1="Modify Device",
        comp1="components/dev_mgmt/app_buttons.html"
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