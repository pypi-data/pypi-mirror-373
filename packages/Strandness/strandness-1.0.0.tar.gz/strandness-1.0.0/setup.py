from setuptools import setup
from setuptools import find_packages

version_py = "Strandness/_version.py"
exec(open(version_py).read())

setup(
    name="Strandness", # Replace with your own username
    version=__version__,
    author="Benxia Hu",
    author_email="hubenxia@gmail.com",
    description="Analyze strandness of RNAs-seq data",
    long_description="Analyze strandness of RNAs-seq data",
    url="https://pypi.org/project/Strandness/",
    entry_points = {
        "console_scripts": ['Strandness = Strandness.Strandness:main',]
        },
    python_requires = '>=3.12',
    packages = ['Strandness'],
    install_requires = [
        'numpy',
        'pandas',
        'argparse',
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    zip_safe = False,
  )