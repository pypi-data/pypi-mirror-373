#!/usr/bin/env python
"""Setup script for raystack."""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "FastAPI sizzles, Django dazzles. The best of both worlds in one framework."

setup(
    name="raystack",
    version="0.0.0",
    description="FastAPI sizzles, Django dazzles. The best of both worlds in one framework.",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Vladimir Penzin",
    author_email="pvenv@icloud.com",
    url="https://github.com/ForceFledgling/raystack",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.6",
    # data_files=[("", ["suppress_warnings.pth"])],  # Removed as no longer needed
    install_requires=[
        "uvicorn<0.20.0",
        "fastapi<0.100.0",
        "asgiref<4.0.0",
        "jinja2<3.2.0",
        "bcrypt<4.1.0",
        # "python-jose<3.4.0",  # Replaced with PyJWT
        "pyjwt<2.8.0",
        "itsdangerous<2.2.0",
        "python-multipart<0.1.0",
        "sqlalchemy<2.0.0",
        "alembic<1.12.0",
        "click<8.2.0",
    ],
    entry_points={
        "console_scripts": [
            "raystack=raystack.core.management:execute_from_command_line",
        ],
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Framework :: FastAPI",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    license="MIT License",
)
