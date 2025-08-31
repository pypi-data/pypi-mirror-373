"""
Setup script for XBus
Fallback pour compatibilité avec anciennes versions pip/setuptools
"""

from setuptools import setup
import os

# Lecture du README pour description longue
current_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_dir, "README.md"), encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="eventx",
    version="0.1.0",
    author="Anzize Daouda",
    author_email="nexusstudio100@gmail.com",
    description="Event-driven messaging via exceptions - Ultra-lightweight event system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Tryboy869/eventx",
    project_urls={
        "Repository": "https://github.com/Tryboy869/eventx",
        "Bug Reports": "https://github.com/Tryboy869/eventx/issues",
    },
    py_modules=["xbus"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11", 
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[],  # Zero dependencies
    keywords="events messaging exceptions event-driven lightweight microservices",
)