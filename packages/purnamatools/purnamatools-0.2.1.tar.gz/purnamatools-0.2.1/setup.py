from setuptools import setup, find_packages
from pathlib import Path

# Read the long description from README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="purnamatools",
    version="0.2.1",
    author="Purnama Ridzky Nugraha",
    author_email="purnamanugraha492@gmail.com",
    description="Python package to simplify the initial stages of model building and analysis for data science projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "seaborn>=0.11.0",
        "matplotlib>=3.4.0",
        "scikit-learn>=1.0.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries"
    ],
    keywords="data-science machine-learning feature-selection model-analysis",
    url="https://github.com/PurnamaRidzkyN/purnamatools.git",  
)
