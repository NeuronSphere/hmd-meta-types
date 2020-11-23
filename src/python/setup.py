from setuptools import setup, find_packages

with open("../../meta-data/VERSION", "r") as vfl:
    version = vfl.read().strip()

setup(
    name="hmd-meta-types",
    version=version,
    description="Base classes and framework for representing HMD type definitions of basic metatypes in code.",
    author="Alex Burgoon",
    author_email="alex.burgoon@hmdlabs.io",
    license="unlicensed",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
)
