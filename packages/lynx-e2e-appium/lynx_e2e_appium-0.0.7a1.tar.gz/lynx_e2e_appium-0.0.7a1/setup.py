# -*- coding: utf-8 -*-
"""setup.py for distribution
"""

import codecs
import os

from setuptools import setup, find_packages

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_NAME = "lynx-e2e"
MODULE_NAME = "lynx_e2e"
DESCRIPTION = "Lynx E2E Driver"

def generate_version():
    version = "0.0.7-alpha.1"
    if os.path.isfile(os.path.join(BASE_DIR, "version.txt")):
        with codecs.open(os.path.join(BASE_DIR, "version.txt"), "r", encoding="utf-8") as fd:
            content = fd.read().strip()
            if content:
                version = content
    if os.path.isfile(os.path.join(BASE_DIR, MODULE_NAME, "__version__.py")):
        with codecs.open(os.path.join(BASE_DIR, MODULE_NAME, "__version__.py"), "r", encoding="utf-8") as fd:
            content = fd.read().strip()
            if content:
                start_index = content.find("version = ")
                if start_index != -1:
                    version = content[start_index + len("version = "):]
                else:
                    raise Exception("version not found")
    else:
        with codecs.open(os.path.join(BASE_DIR, MODULE_NAME, "__version__.py"), "w", encoding="utf-8") as fd:
            fd.write('version = "%s"\n' % version)
    return str(version)

def parse_appium_requirements():
    reqs = []
    if os.path.isfile(os.path.join(BASE_DIR, "appium_requirements.txt")):
        with codecs.open(os.path.join(BASE_DIR, "appium_requirements.txt"), 'r', encoding="utf-8") as fd:
            for line in fd.readlines():
                line = line.strip()
                if line:
                    reqs.append(line)
        return reqs

def deploy():
    setup(
        version=generate_version(),
        name=f"{PACKAGE_NAME}-appium",
        packages=find_packages(
            include=("lynx_e2e", "lynx_e2e.*"), 
            exclude=()
        ),
        include_package_data=True,
        data_files=[],
        description=DESCRIPTION,
        long_description=DESCRIPTION,
        author="gaohanqing",
        author_email="gaohqnuaa@foxmail.com",
        install_requires=parse_appium_requirements(),
    )

if __name__ == "__main__":
    deploy()
