from pathlib import Path
from setuptools import setup

# read the contents of your README file

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='em-map-utils',
    version='0.0.1',
    packages=['em-map-utils', 'em-map-utils.demos'],
    url='https://github.com/ardanpat/em-map-utils.git',
    license='Apache License 2.0',
    author='Ardan Patwardhan',
    author_email='ardan@ebi.ac.uk',
    description='Python package for creating and manipulating cryoEM maps in EMDB (mrc) map format.',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
