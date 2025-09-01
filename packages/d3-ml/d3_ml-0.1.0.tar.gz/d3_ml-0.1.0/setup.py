from setuptools import setup, find_packages

setup(
    name="d3-ml",
    version="0.1.0",
    description="Simple ML preprocessing toolkit",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "scikit-learn",
    ],
)
