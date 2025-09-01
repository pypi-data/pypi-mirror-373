from setuptools import setup, find_packages
from pathlib import Path

# Récupère le contenu du README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")
description = (
    (this_directory / "pybirdsreynolds" / "DESCRIPTION.txt")
    .read_text(encoding="utf-8")
    .strip()
)

setup(
    name="pybirdsreynolds",
    version="2.0.6",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thib1984/pybirdsreynolds",
    author="thib1984",
    author_email="thibault.garcon@gmail.com",
    license="MIT",
    license_files=[],
    packages=["pybirdsreynolds"],
    install_requires=["scipy"],
    zip_safe=False,
    entry_points={
        "console_scripts": ["pybirdsreynolds=pybirdsreynolds.__init__:pybirdsreynolds"],
    },
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    include_package_data=True,
    package_data={"pybirdsreynolds": ["DESCRIPTION.txt", "EPILOG.txt"]},
)
