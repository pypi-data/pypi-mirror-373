"""Run setuptools."""

import pathlib

from setuptools import find_packages, setup

setup(
    name="arkprts",
    version="0.3.18",
    description="Arknights python wrapper.",
    url="https://github.com/thesadru/arkprts",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    package_data={"arkprts": ["py.typed"]},
    install_requires=["aiohttp", "pydantic==2.*"],
    extras_require={
        "all": ["UnityPy>=1.22.2", "rsa", "pycryptodome", "bson"],
        "rsa": ["rsa"],
        "aes": ["pycryptodome"],
        "assets": ["UnityPy>=1.22.2", "pycryptodome", "bson"],
    },
    long_description=pathlib.Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    license="MIT",
)
