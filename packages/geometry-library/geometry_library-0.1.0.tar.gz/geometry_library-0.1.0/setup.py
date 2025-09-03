
from setuptools import setup, find_packages
from os import path

# Get the absolute path to the directory containing this file
here = path.abspath(path.dirname(__file__))

# Read the README.md file
try:
    with open(path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ""

setup(
    name='geometry_library',
    version='0.1.0',
    packages=find_packages(),
    description='A simple Python library for 2D geometry.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Dada09898/Ankit_kumar_singh-geometry-library',  # Replace with your GitHub URL
    author='Ankit kumar singh',
    author_email='singhkumar50866@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[],  # List any dependencies here
)
