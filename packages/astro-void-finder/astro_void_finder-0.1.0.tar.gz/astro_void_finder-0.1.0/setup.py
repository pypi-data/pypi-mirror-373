from setuptools import setup, find_packages

setup(
    name="astro-void-finder",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "astropy>=4.0",
        "numba>=0.55.0",
        "h5py>=3.0.0",
        "matplotlib>=3.4.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "psutil>=5.8.0"
    ],
    author="JFBookwood",
    author_email="jesse.buchholz@jgmm.de",
    description="High-performance astrophysics library for void finding, neutrino physics, and N-body simulations",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/JFBookwood/astro-void-finder",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.8",
    keywords="astronomy astrophysics cosmology voids neutrinos n-body simulation",
)
