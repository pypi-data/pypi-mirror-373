from setuptools import setup, find_packages

# Read the README.md file for the long description
try:
    with open('README.md', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ""

setup(
    name='tm_deep_utilities',
    version='0.2.0',
    author='Saadat Mukadam',
    author_email='s0000160.oth@tatamotors.com',
    description='A collection of utility functions for Databricks data operations',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/your-repo/databricks_utils' if False else None,
    packages=['tm_deep_utilities', 'tm_deep_utilities.storage', 'tm_deep_utilities.transformation', 'tm_deep_utilities.pipeline_logging'],
    install_requires=[
        'pyspark>=3.2.0',  # PySpark is a core dependency for Databricks operations
    ],
    package_dir={
        'tm_deep_utilities': '.',
        'tm_deep_utilities.storage': 'storage',
        'tm_deep_utilities.transformation': 'transformation',
        'tm_deep_utilities.pipeline_logging': 'pipeline_logging'
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.7',
)