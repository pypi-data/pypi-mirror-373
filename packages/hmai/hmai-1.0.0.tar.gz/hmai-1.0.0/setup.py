"""
Setup script for Hyper-Material AI (HMAI) framework.
"""

from setuptools import setup, find_packages
import os

# Get the directory containing this setup.py file
here = os.path.abspath(os.path.dirname(__file__))

# Read README for long description
readme_path = os.path.join(here, "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "HMAI: AI framework for inventing new classes of matter"

# Read requirements
requirements_path = os.path.join(here, "requirements.txt")
if os.path.exists(requirements_path):
    with open(requirements_path, "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
else:
    # Fallback requirements if file not found
    requirements = [
        "tensorflow>=2.8.0",
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "matplotlib>=3.5.0",
        "pyyaml>=6.0",
        "tqdm>=4.62.0",
        "h5py>=3.6.0",
        "scikit-learn>=1.1.0"
    ]

# Version
__version__ = "1.0.0"

setup(
    name="hmai",
    version=__version__,
    author="Krishna Bajpai, Vedanshi Gupta",
    author_email="krishn@krishnabajpai.me, vedanshigupta18@gmail.com",
    description="AI framework for inventing new classes of matter through generative quantum field theory",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hmai/framework",
    project_urls={
        "Bug Tracker": "https://github.com/hmai/framework/issues",
        "Documentation": "https://hmai.dev/docs",
        "Source Code": "https://github.com/hmai/framework",
        "Homepage": "https://hmai.dev",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "docs": [
            "mkdocs>=1.4.0",
            "mkdocs-material>=8.0.0",
            "mkdocs-material-extensions>=1.0.0",
        ],
        "quantum": [
            "qiskit>=0.39.0",
            "cirq>=0.15.0",
        ],
        "viz": [
            "plotly>=5.0.0",
            "bokeh>=2.4.0",
            "mayavi",
        ],
    },
    entry_points={
        "console_scripts": [
            "hmai=hmai.cli:main",
            "hmai-generate=hmai.cli:generate",
            "hmai-validate=hmai.cli:validate",
        ],
    },
    include_package_data=True,
    package_data={
        "hmai": [
            "data/*.json",
            "data/*.yaml",
            "models/*.h5",
            "templates/*.txt",
        ],
    },
    zip_safe=False,
    keywords=[
        "materials science",
        "quantum field theory", 
        "artificial intelligence",
        "machine learning",
        "physics simulation",
        "materials discovery",
        "exotic matter",
        "metamaterials",
        "quantum materials",
        "computational physics"
    ],
)
