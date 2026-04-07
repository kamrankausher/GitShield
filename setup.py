"""GitShield — AI-powered Git Guardian & Developer Intelligence System."""
from setuptools import setup, find_packages

setup(
    name="gitshield",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0",
        "rich>=13.0",
        "colorama>=0.4.6",
    ],
    entry_points={
        "console_scripts": [
            "gitshield=devflow.cli:main",
        ],
    },
    python_requires=">=3.9",
    author="GitShield Team",
    description="AI-powered Git Guardian — prevents secret leaks, enforces best practices, and coaches developers in real-time",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/your-username/gitshield",
)
