from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="filterKaapi",
    version="0.1.4",
    description="FilterKaapi: A Tamil-inspired programming language",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Chiddesh",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "kaapi=kaapi_lang.cli:main",
        ]
    },
)
