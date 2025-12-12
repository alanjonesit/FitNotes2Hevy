"""Setup configuration for fitnotes2hevy package."""

from pathlib import Path

from setuptools import find_packages, setup

# Read README
readme = Path("README.md").read_text(encoding="utf-8")

setup(
    name="fitnotes2hevy",
    version="1.0.0",
    author="Alan Jones",
    description="Convert FitNotes workout exports to Hevy-compatible CSV format",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/alanjonesit/FitNotes2Hevy",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "pandas>=2.0.0",
        "typer>=0.9.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "web": ["streamlit>=1.28.0"],
    },
    entry_points={
        "console_scripts": [
            "fitnotes2hevy=scripts.convert:app",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
