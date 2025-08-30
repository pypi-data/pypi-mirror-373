# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from time import sleep


def bar(open_time):
    print("bar is open")
    for _ in range(open_time):
        print(".")
        sleep(1)
    print()
    print("bar is closed")
