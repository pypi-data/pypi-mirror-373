from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bayesian-network-generator",
    version="1.0.0",
    author="Rudzani Mulaudzi",
    author_email="rudzani.mulaudzi2@students.wits.ac.za",
    description="Advanced Bayesian Network Generator with comprehensive topology and distribution support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rudzanimulaudzi/bayesian-network-generator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.9.0",
        "pandas>=1.0.0",
        "networkx>=2.0.0",
        "pgmpy>=0.1.17",
        "matplotlib>=3.0.0",
        "seaborn>=0.9.0",
        "scikit-learn>=0.20.0",
        "scipy>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "bayesian-network-generator=bayesian_network_generator.cli:main",
        ],
    },
    keywords="bayesian networks machine learning probabilistic graphical models",
    project_urls={
        "Bug Reports": "https://github.com/rudzanimulaudzi/bayesian-network-generator/issues",
        "Source": "https://github.com/rudzanimulaudzi/bayesian-network-generator",
        "Documentation": "https://github.com/rudzanimulaudzi/bayesian-network-generator/blob/main/README.md",
    },
)