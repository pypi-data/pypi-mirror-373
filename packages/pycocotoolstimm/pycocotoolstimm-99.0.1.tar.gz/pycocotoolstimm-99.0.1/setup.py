from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pycocotoolstimm",
    version="99.0.1",
    description="Safe demo package (PoC by @bh3x)",
    long_description=long_description,
    long_description_content_type="text/markdown",  # important for Markdown
    author="bh3x",
    packages=find_packages(),
    python_requires=">=3.7",
)