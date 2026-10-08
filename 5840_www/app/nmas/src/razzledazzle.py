#!/usr/bin/env python3

from random import choice

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

def ascii_page():
    return f"components/{choice([
        "ascii_choppers",
        "ascii_computer_big_dog",
        "ascii_mecha",
        "ascii_castle"
    ])}.html"

def main():
    pass

if __name__ == "__main__":
    main()