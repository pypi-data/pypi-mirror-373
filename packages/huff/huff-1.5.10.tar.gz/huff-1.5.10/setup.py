from setuptools import setup, find_packages
import os

def read_README():
    with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
        return f.read()
    
setup(
    name='huff',
    version='1.5.10',
    description='huff: Huff Model Market Area Analysis',
    packages=find_packages(include=["huff", "huff.tests"]),
    include_package_data=True,
    long_description=read_README(),
    long_description_content_type='text/markdown',
    author='Thomas Wieland',
    author_email='geowieland@googlemail.com',
    license_files=["LICENSE"],
    package_data={
        'huff': ['tests/data/*'],
    },
    install_requires=[
        'geopandas==1.1.1',
        'pandas==2.3.1',
        'numpy==2.3.0',
        'statsmodels==0.14.2',
        'scipy==1.15.3',
        'shapely==2.1.1',
        'requests==2.32.4',
        'matplotlib==3.10',
        'pillow==10.2.0',
        'contextily==1.6.2',
        'openpyxl==3.1.4'
    ],
    test_suite='tests',
)