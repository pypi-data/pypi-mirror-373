from setuptools import setup, find_packages  # type: ignore

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="proteinpy",
    version="0.1.2",
    description="A Python toolkit for fetching and analyzing protein sequences.",
    long_description=long_description, 
    long_description_content_type="text/markdown",  
    author="arctictern",
    author_email="anik.bioinfo@gmail.com",
    packages=find_packages(),
    install_requires=[
        "requests",
        "matplotlib"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ],
    python_requires=">=3.7",
)
