from pathlib import Path

from setuptools import setup, find_packages
import os

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

VERSION = os.environ.get("PACKAGE_VERSION", "0.0.1")

setup(
    name="owasp-dependency-track-client",
    description="Inofficial OWASP Dependency Track API Python client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=VERSION,
    url="https://github.com/mreiche/owasp-dependency-track-python-client",
    author="Mike Reiche",
    packages=find_packages(),
    install_requires=["attrs>=22.1.0", "httpx>=0.23.0", "python-dateutil>=2.8.2"],
)
