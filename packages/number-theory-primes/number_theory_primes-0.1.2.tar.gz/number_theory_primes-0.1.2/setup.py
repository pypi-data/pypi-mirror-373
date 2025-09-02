from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="number-theory-primes",
    version="0.1.2",
    author="Madhulatha Mandarapu, Sandeep Kunkunuru",
    author_email="madhulatha@vaidhyamegha.com, sandeep.kunkunuru@gmail.com",
    description="Advanced primality testing algorithms including AKS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VaidhyaMegha/primes",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "sympy>=1.8",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5",
        ],
        "benchmarks": [
            "matplotlib>=3.3",
            "seaborn>=0.11",
            "pandas>=1.3",
        ],
    },
)
