from setuptools import setup, find_packages

setup(
    name="janitor-cubix",              # distribution name on (Test)PyPI (lowercase recommended)
    version="0.0.3",
    description="Janitor Library",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Cubix523",
    license="MIT",
    packages=find_packages(),    # finds the 'Janitor' package
    install_requires=[],         # runtime dependencies only
    extras_require={"dev": ["pytest"]},
    python_requires=">=3.7",
)