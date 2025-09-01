from setuptools import setup, find_packages

setup(
    name='mypkg',
    version='0.1.0',
    author='om',
    description='A package for calculating area of shapes',
    packages=find_packages(include=["mypkg", "mypkg.*"]),
        python_requires='>=3.6',
)

