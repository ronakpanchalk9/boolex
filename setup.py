from setuptools import setup, find_packages

setup(
    name='boolex',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'regex==2024.9.11',
        'pandas==2.2.3'
    ]
)
