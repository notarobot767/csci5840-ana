#!/usr/bin/env python3

import dev.show
import dev.creds
import gui.objects
import gui.add
import gui.remove
import gui.modify

import razzledazzle, file_object

from flask import Flask, render_template, redirect, jsonify, abort, url_for, flash, request, Response
from random import choice, randint
import subprocess, sys

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
            comp4_template="components/dev_mgmt/numbered_content.html",
            content=content,
            device=device,
            label=label
        )
    return _no_such_device(device)

@app.route("/device/view/<device>/yaml")
def device_view_device_yaml(device):
    content = dev.creds.get_device_yaml(device)
    label = "yaml"
    return _render_device_funct(device, content, label)

@app.route("/device/view/<device>/ospf")
def device_view_device_ospf(device):
    content = dev.show.get_ospf_neighbors(device)
    label = "ospf"
    return _render_device_funct(device, content, label)

@app.route("/device/view/<device>/isis")
def device_view_device_isis(device):
    content = dev.show.get_isis_neighbors(device)
    label = "isis"
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
        comp4_template="components/dev_mgmt/diff_content.html",
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
            success, err = gui.add.add_device(
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
        comp1_func=gui.objects.get_dev_app_buttons(),
        comp2_template="components/dev_mgmt/add.html",
        vendors=gui.add.get_vendors(),
        templates=gui.add.get_templates()
    )

@app.route("/device/remove")
def device_remove():
    devices = dev.creds.get_devices()
    if _is_safe_devices(devices):
        return redirect(url_for("device_remove_device", device=devices[0]))

    flash("No devices available to remove.", "warning")
    return render_template(
        "template.html",
        title="Remove Device",
        h1="Remove Device",
        comp1_func=gui.objects.get_dev_app_buttons(),
    )

@app.route("/device/remove/<device>", methods=["GET", "POST"])
def device_remove_device(device):
    if not _is_safe_device(device):
        return _no_such_device(device)

    if request.method == "POST":
        success, err = gui.remove.remove_device(device)
        if success:
            flash(f"Device '{device}' was successfully removed.", "success")
            return redirect(url_for("device_remove"))
        else:
            flash(err or f"Failed to remove device '{device}'.", "danger")

    return render_template(
        "template.html",
        title="Remove Device",
        h1=f"Remove Device: {device}",
        comp1_func=gui.objects.get_dev_app_buttons(),
        comp2_func=gui.objects.get_device_view_buttons(func="remove"),
        comp3_template="components/dev_mgmt/device_remove_prompt.html",
        device=device,
        yaml_content=dev.creds.get_device_yaml(device)
    )

@app.route("/device/modify")
def device_modify():
    devices = dev.creds.get_devices()
    if _is_safe_devices(devices):
        return redirect(url_for("device_modify_device", device=devices[0]))

    flash("No devices available to modify.", "warning")
    return render_template(
        "template.html",
        title="Modify Device",
        h1="Modify Device",
        comp1_func=gui.objects.get_dev_app_buttons(),
    )


@app.route("/device/modify/<device>", methods=["GET", "POST"])
def device_modify_device(device):
    if not _is_safe_device(device):
        return _no_such_device(device)

    if request.method == "POST":
        raw_yaml = request.form.get("raw_yaml", "")
        success, err = gui.modify.update_device_from_yaml(device, raw_yaml)
        if success:
            flash(f"Device '{device}' configuration updated successfully!", "success")
            return redirect(url_for("device_modify_device", device=device))
        else:
            flash(err, "danger")

    # Retrieve un-sanitized combined YAML so passwords/creds are editable
    raw_content = dev.creds.get_device_yaml(device, sanitize=False) or ""

    return render_template(
        "template.html",
        title="Modify Device",
        h1=f"Modify Device: {device}",
        comp1_func=gui.objects.get_dev_app_buttons(),
        comp2_func=gui.objects.get_device_view_buttons(func="modify", current_device=device),
        comp3_template="components/dev_mgmt/device_modify_form.html",
        device=device,
        raw_yaml_content=raw_content,
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

@app.route("/device/test")
def unit_test():
    return render_template(
        "template.html",
        title="UT",
        h1="Unit Testing",
        comp1_func=gui.objects.get_dev_app_buttons(),
        comp2_func=gui.objects.get_unit_test_buttons(),
    )

@app.route("/device/test/stream/runtests")
def stream_unit_tests():
    def generate():
        # -u forces unbuffered binary stdout/stderr
        # -v provides verbose progress line-by-line
        cmd = [sys.executable, "-u", "-m", "pytest", "-v", "-n", "auto"]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1  # Line buffered
        )

        for line in iter(process.stdout.readline, ""):
            # Format as Server-Sent Event (SSE)
            yield f"data: {line}\n\n"

        process.stdout.close()
        process.wait()
        yield "data: [DONE]\n\n"

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"  # Prevents Nginx/proxy from buffering chunks
        }
    )

@app.route("/device/test/runtests")
def run_unit_tests():
    terminal_template = "components/dev_mgmt/live_terminal.html"
    return render_template(
        "template.html",
        title="UT - Live Tests",
        h1="Running Unit Tests",
        comp1_func=gui.objects.get_dev_app_buttons(),
        comp2_func=gui.objects.get_unit_test_buttons(),
        comp3_template=terminal_template,
        stream_url="/device/test/stream/runtests"
    )

@app.route("/device/test/stream/codecoverage")
def stream_code_coverage():
    def generate():
        # -u: unbuffered stdout/stderr
        # --cov=src: target directory for coverage measurement
        # --cov-report=term-missing: print missing line numbers to terminal
        cmd = [
            sys.executable,
            "-u",
            "-m",
            "pytest",
            "-q",
            "-n",
            "auto",
            "--cov=src",
            "--cov-report=term-missing",
        ]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,  # Line-buffered
        )

        for line in iter(process.stdout.readline, ""):
            # Server-Sent Event (SSE) data frame
            yield f"data: {line}\n\n"

        process.stdout.close()
        process.wait()
        yield "data: [DONE]\n\n"

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

@app.route("/device/test/codecoverage")
def run_code_coverage():
    return render_template(
        "template.html",
        title="UT - Code Coverage",
        h1="Running Code Coverage",
        comp1_func=gui.objects.get_dev_app_buttons(),
        comp2_func=gui.objects.get_unit_test_buttons(),
        comp3_template="components/dev_mgmt/live_terminal.html",
        stream_url="/device/test/stream/codecoverage",
    )

def main():
    app.debug = True
    app.run(host="0.0.0.0", threaded=True)

if __name__ == "__main__":
    main()