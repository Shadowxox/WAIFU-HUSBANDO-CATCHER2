import os

ALL_MODULES = []

# Dynamically import all .py files except __init__.py
for file in os.listdir(os.path.dirname(__file__)):
    if file.endswith(".py") and file != "__init__.py":
        ALL_MODULES.append(file[:-3])
