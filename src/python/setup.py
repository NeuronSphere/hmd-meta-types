from setuptools import setup, find_packages
import pathlib

repo_dir = pathlib.Path(__file__).absolute().parent.parent.parent
version_file = repo_dir / "meta-data" / "VERSION"

with open(version_file, "r") as vfl:
    version = vfl.read().strip()

setup(
    name="hmd-meta-types",
    version=version,
    description="Base classes and framework for representing HMD type definitions of basic metatypes in code.",
    author="Alex Burgoon",
    author_email="alex.burgoon@hmdlabs.io",
    license="Apache 2.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
)
