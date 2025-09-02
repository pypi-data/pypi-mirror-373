from setuptools import setup, find_packages

setup(
    name='gyb-classification-model',                          # Package name (what you'll pip install)
    version='0.1.3',
    author='Hrutik-M',
    author_email='hrutik.m@codearray.tech',
    description='ML classification models package',
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
