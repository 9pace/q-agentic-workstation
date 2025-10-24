"""Setup script for Q Agentic Workstation."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read version
version_file = Path(__file__).parent / "qaw" / "__init__.py"
version = "0.1.0"
for line in version_file.read_text().splitlines():
    if line.startswith("__version__"):
        version = line.split('"')[1]
        break

setup(
    name="qaw",
    version=version,
    description="Q Agentic Workstation - Parallel agent execution for hyperdeveloping",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/q-agentic-workstation",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "psutil>=5.9.0",
        "textual>=0.47.0",
    ],
    entry_points={
        "console_scripts": [
            "qaw=qaw.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Tools",
    ],
)
