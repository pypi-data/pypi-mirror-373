from setuptools import setup, find_packages
from pathlib import Path

curr_directory = Path(__file__).parent
long_description = (curr_directory / "README.md").read_text()

setup(
    name='gyb-classification-model',                          # Package name (what you'll pip install)
    version='0.1.6',
    author='Hrutik-M',
    author_email='hrutik.m@codearray.tech',
    description='ML classification models package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GreenBills/GYB-Classification-Model",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['../models/*.pkl'],               # Include model files
    },
    install_requires=[
        'pandas==2.2.3',
        'scikit-learn==1.6.1',
        'seaborn==0.13.2',
        'nltk==3.9.1',
        'xgboost==3.0.0'
    ],
    python_requires='>=3.10',
)
