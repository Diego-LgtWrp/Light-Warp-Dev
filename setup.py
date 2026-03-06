from setuptools import setup, find_packages

setup(
    name="lightwarp",
    version="0.1.0",
    description="LightWarp animation pipeline — shared tools, DCC integrations, and utilities.",
    packages=find_packages(include=["lightwarp", "lightwarp.*"]),
    python_requires=">=3.8",
)
