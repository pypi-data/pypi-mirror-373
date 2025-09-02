from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="snp",
    version="0.1.0",
    author="Bistoon Hosseini",
    author_email="bistoon.hosseini@gmail.com",
    description="Stepwise Noise Peeling for Nadaraya-Watson Regression",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bistoonh/SNP-Python",
    project_urls={
        "Bug Reports": "https://github.com/bistoonh/SNP-Python/issues",
        "Source": "https://github.com/bistoonh/SNP-Python",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
        "scipy>=1.6.0",
    ],
    extras_require={
        "examples": ["matplotlib>=3.3.0", "pandas>=1.2.0"],
        "dev": ["pytest>=6.0", "pytest-cov>=2.10.0"],
        "all": ["matplotlib>=3.3.0", "pandas>=1.2.0", "pytest>=6.0", "pytest-cov>=2.10.0"],
    },
    keywords="regression, smoothing, bandwidth-selection, nadaraya-watson, kernel-regression",
)