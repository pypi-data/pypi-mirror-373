# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='gedcom-x',
    version='0.5.7',
    packages=find_packages(),
    description="A Python toolkit for working with GEDCOM-X",
    long_description=long_description,
    long_description_content_type="text/markdown",
    #install_requires=[
        # List your project dependencies here, e.g.,
    #    None,
    #],
    entry_points={
        'console_scripts': [
            # Define command-line scripts if needed
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)