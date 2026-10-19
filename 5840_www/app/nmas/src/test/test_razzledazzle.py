#!/usr/bin/env python3

import razzledazzle

def test_motto():
    output = razzledazzle.motto()
    assert output is not None
    assert isinstance(output, str)

def test_ascii_page():
    output = razzledazzle.ascii_page()
    assert output is not None
    assert isinstance(output, str)
    assert output.endswith(".html")

def main():
    pass

if __name__ == "__main__":
    main()