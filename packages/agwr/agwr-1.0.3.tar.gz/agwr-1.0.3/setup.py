from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agwr",
    version="1.0.0",
    author="AGWR开发团队",
    author_email="agwr@example.com",
    description="各向异性地理加权回归模型实现",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/agwr-team/agwr",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
        "pyproj>=3.0.0",
        "mgwr>=2.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    keywords="geographically weighted regression, spatial statistics, anisotropy, gwr, agwr",
    project_urls={
        "Bug Reports": "https://github.com/agwr-team/agwr/issues",
        "Source": "https://github.com/agwr-team/agwr",
        "Documentation": "https://agwr.readthedocs.io/",
    },
)
