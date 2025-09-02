from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="crc1625_api",
    version="0.1.5",
    packages=find_packages(),
    install_requires=[
   "requests",
  "pandas",
  "openpyxl",
  "scipy",
  "numpy"
    ],
    author="Doaa Mohamed",
    author_email="doaamahmoud262@yahoo.com",
    description="Python wrapper for the CRC 1625 MatInf VRO API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.ruhr-uni-bochum.de/icams-mids/crc1625rdmswrapper",
    project_urls={
        "Source": "https://gitlab.ruhr-uni-bochum.de/icams-mids/crc1625rdmswrapper",
        "Tracker": "https://gitlab.ruhr-uni-bochum.de/icams-mids/crc1625rdmswrapper/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    python_requires='>=3.7',
)
