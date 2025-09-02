from setuptools import setup, find_packages
from os import path
working_directory = path.abspath(path.dirname(__file__))

with open(path.join(working_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='example_package_TEST_ABI_SDK',
    version='0.1.0',
    author='test',
    author_email='',
    description='Django REST Framework authentication middleware',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'SQLAlchemy==2.0.36',
        'requests==2.32.4',
        'Logbook==1.8.2'
    ]
)