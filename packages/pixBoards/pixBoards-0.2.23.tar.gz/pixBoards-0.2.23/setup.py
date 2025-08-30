import os
import re

from setuptools import find_packages, setup

with open("readme.md", "r") as f:
    description = f.read()


def parse_requirements(filename="requirements.txt"):
    with open(filename, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


version = "0.2.23"

with open(os.path.join("pixBoards", "__init__.py"), "r") as f:
    init = f.read()


with open(os.path.join("pixBoards", "__init__.py"), "w") as f:
    new_version_line = f'__version__ = "{version}" '
    init = re.sub(r"^__version__\s*=.*$", new_version_line, init, flags=re.MULTILINE)
    f.write(init)

setup(
    name="pixBoards",
    version=version,
    packages=find_packages(),
    include_package_data=True,
    package_data={"pixBoards": ["templates/*.*"]},
    install_requires=parse_requirements(),
    entry_points={
        "console_scripts": [
            "run=pixBoards.cli:main",
        ],
    },
    long_description=description,
    long_description_content_type="text/markdown",
)

"""
python3 setup.py sdist bdist_wheel
git add . && git commit -m "fixes"
git push
twine upload dist/*
"""
