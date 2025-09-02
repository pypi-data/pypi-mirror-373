import os.path
import pathlib
from os.path import exists
from setuptools import setup, find_packages

CURRENT_DIR = pathlib.Path(__file__).parent
long_description = ""
readme_md_file = os.path.join(CURRENT_DIR, "README.md")
if exists(readme_md_file):
    long_description = pathlib.Path(readme_md_file).read_text()


def get_dependencies():
    return ["requests", "setuptools", "peewee", "mysql-connector-python", "portalocker"]


setup(
    name='exsited',
    version='1.0.27',
    description='Exsited SDK',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Ashiq Rahman',
    author_email='ashiq@webalive.com.au',
    url='https://github.com/exsited/exsited-python',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=get_dependencies(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    project_urls={
        'Documentation': 'https://developer.exsited.com/exsited-sdk-introduction',
    },
)