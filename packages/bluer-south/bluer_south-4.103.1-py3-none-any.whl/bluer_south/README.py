import os

from bluer_objects import file, README

from bluer_south import NAME, VERSION, ICON, REPO_NAME
from bluer_south.content import items


def build():
    return README.build(
        items=items,
        path=os.path.join(file.path(__file__), ".."),
        ICON=ICON,
        NAME=NAME,
        VERSION=VERSION,
        REPO_NAME=REPO_NAME,
    )
