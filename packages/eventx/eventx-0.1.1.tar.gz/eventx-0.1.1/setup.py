"""
Setup script for EventX v0.1.1
Robuste et compatible avec toutes versions pip/setuptools
"""

import os
import sys
from setuptools import setup

# Vérification version Python minimum
if sys.version_info < (3, 8):
    sys.exit("EventX requires Python 3.8 or higher")

# Lecture du README pour description longue
def read_file(filename):
    """Lecture sécurisée des fichiers"""
    current_dir = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(current_dir, filename)
    
    try:
        with open(filepath, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: {filename} not found")
        return ""
    except Exception as e:
        print(f"Warning: Could not read {filename}: {e}")
        return ""

# Lecture sécurisée du README
long_description = read_file("README.md")
if not long_description:
    long_description = "Event-driven messaging via exceptions - Ultra-lightweight event system for Python"

# Configuration du package
setup(
    name="eventx",
    version="0.1.1",
    author="Anzize Daouda",
    author_email="nexusstudio100@gmail.com",
    
    # Descriptions
    description="Event-driven messaging via exceptions - Ultra-lightweight event system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    # URLs et liens
    url="https://github.com/Tryboy869/eventx",
    project_urls={
        "Homepage": "https://github.com/Tryboy869/eventx",
        "Repository": "https://github.com/Tryboy869/eventx", 
        "Documentation": "https://github.com/Tryboy869/eventx#readme",
        "Bug Reports": "https://github.com/Tryboy869/eventx/issues",
        "Changelog": "https://github.com/Tryboy869/eventx/releases"
    },
    
    # Configuration du package
    py_modules=["eventx"],  # Single module
    python_requires=">=3.8",
    install_requires=[],  # Zero dependencies
    
    # Classification PyPI
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        "Topic :: Software Development :: Object Brokering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10", 
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Typing :: Typed"
    ],
    
    # Métadonnées supplémentaires
    keywords=[
        "events", "messaging", "exceptions", "event-driven", 
        "lightweight", "async-alternative", "microservices", 
        "python", "raise", "exception-based"
    ],
    
    # Dependencies optionnelles
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0", 
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "isort>=5.12.0"
        ],
        "test": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0"
        ]
    },
    
    # Compatibilité
    zip_safe=True,
    include_package_data=False,
)