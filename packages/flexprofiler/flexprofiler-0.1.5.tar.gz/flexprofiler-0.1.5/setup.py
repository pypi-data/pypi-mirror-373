from setuptools import setup

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='flexprofiler',
    version='0.1.5',
    description='A flexible profiling utility for Python.',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
