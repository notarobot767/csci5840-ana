#!/usr/bin/env python3

from flask import Flask, render_template, redirect, jsonify, abort
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
        h1="Home",
        comp1="components/app_buttons.html",
        comp2=ascii_art
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