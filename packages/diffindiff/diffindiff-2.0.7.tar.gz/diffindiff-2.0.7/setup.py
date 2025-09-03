from setuptools import setup, find_packages
import os

def read_README():
    with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
        return f.read()
    
setup(
    name='diffindiff',
    version='2.0.7',
    description='diffindiff: Python library for convenient Difference-in-Differences Analyses',
    packages=find_packages(include=["diffindiff", "diffindiff.tests"]),
    include_package_data=True,
    long_description=read_README(),
    long_description_content_type='text/markdown',
    author='Thomas Wieland',
    author_email='geowieland@googlemail.com',
    license_files=["LICENSE"],
    package_data={
        'diffindiff': ['tests/data/*'],
    },
    install_requires=[
        'numpy',
        'pandas',
        'statsmodels==0.14.2',
        'scipy==1.15.3',
        'matplotlib',
        'datetime',
        'scikit-learn',
        'xgboost',
        'lightgbm'
    ],
    test_suite='tests',
)