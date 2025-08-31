from setuptools import setup, find_packages

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Network Model Analysis for adversarial detection and explanation"

setup(
    name="better_xai_nma",
    version="1.0.2",
    author="BETTER_XAI",
    author_email="BETTERXAI2025@gmail.com",
    description="NMA: Dendrogram-based model analysis, white-box testing, and adversarial detection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[  
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[
        "tensorflow>=2.10.0",
        "pandas>=1.3.0",
        "python-igraph>=0.10.0", 
        "numpy>=1.21.0",
        "scikit-learn>=1.0.0",
        "matplotlib>=3.5.0",
        "nltk>=3.7",
        "keras>=2.10.0",
        "Pillow>=8.0.0",
    ],
)


