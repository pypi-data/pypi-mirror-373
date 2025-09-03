from setuptools import setup, find_packages

setup(
    name="Claridata",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "scikit-learn",
        "loguru"
    ],
    author="Dhivakar G",
    author_email="dhivs838@gmail.com",
    description="Data cleaning and preprocessing package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Dhivakar2005/Claridata",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
