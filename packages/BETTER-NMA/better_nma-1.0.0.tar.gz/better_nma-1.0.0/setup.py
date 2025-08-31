from setuptools import setup, find_packages

setup(
    name="BETTER_NMA",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "tensorflow",
        "pandas",
        "igraph",
        "numpy",
        "scikit-learn",
        "matplotlib",
        "nltk",
        "keras",
    ],
)


