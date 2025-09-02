import setuptools
from pathlib import Path


setuptools.setup(
    name="pkg-pdf",
    version="0.1.0",
    author="Vinothkumar A",
    long_description=Path("README").read_text(encoding="utf-8"),
    packages=setuptools.find_packages(
        exclude=["tests", "project.txt", "data",
                 "test", "tests.*", "docs", "docs.*"]
    ),
)
