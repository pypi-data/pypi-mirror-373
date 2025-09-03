from setuptools import setup, find_packages

setup(
    name='zeonegraph',
    version='2.1.0',
    description='Psycopg2 type extension module for ZeoneGraph',
    install_requires=['psycopg2-binary>=2.7.4'],

    packages=find_packages(exclude=['tests']),
    test_suite = "tests",

    author='zhangjianuxe',
    author_email='zhangjianxue@zeonedb.com',
    maintainer='zeone',
    maintainer_email='zeone@zeonedb.com',
)
