from setuptools import setup, find_packages
import os
import re

# Get the long description from the README file
try:
    # Try to find the README in various locations
    readme_paths = [
        "../../README.md",  # From packages/python relative to project root
        "../README.md",     # One directory up
        "README.md",        # Same directory
        os.path.join(os.path.dirname(__file__), "../../README.md")  # Absolute path
    ]
    
    readme_content = ""
    for path in readme_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                readme_content = f.read()
                break
        except (FileNotFoundError, IOError):
            continue
    
    if not readme_content:
        # Fallback if README.md not found
        readme_content = """
# Velatir Python SDK

SDK for monitoring and approval of AI function calls.
"""
except Exception:
    readme_content = "Velatir Python SDK"

setup(
    name="velatir",
    version="1.0.2",
    description="Python SDK for Velatir - AI function monitoring and approval",
    long_description=readme_content,
    long_description_content_type="text/markdown",
    author="Velatir",
    author_email="hello@velatir.com",
    url="https://www.velatir.com",
    packages=find_packages(exclude=["tests", "examples"]),
    install_requires=[
        "httpx>=0.23.0",
        "pydantic>=1.9.0",
        "tenacity>=8.0.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="ai, monitoring, functions, approval",
)
