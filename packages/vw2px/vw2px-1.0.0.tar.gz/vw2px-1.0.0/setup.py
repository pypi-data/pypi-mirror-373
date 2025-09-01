#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

# Читаем README файл
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Читаем requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="vw2px",
    version="1.0.0",
    author="Bluesuma",
    author_email="v1tuze@yandex.ru",
    description="Конвертер размеров из VW в PX для проектов Vue, React, Next.js и других веб-проектов",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Bluesuma/vw2px",
    project_urls={
        "Bug Tracker": "https://github.com/Bluesuma/vw2px/issues",
        "Documentation": "https://github.com/Bluesuma/vw2px#readme",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    keywords="vw, px, converter, css, vue, react, nextjs, web, development, frontend",
    packages=find_packages(),
    py_modules=["vw2px"],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "vw2px=vw2px:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    platforms=["any"],
)
