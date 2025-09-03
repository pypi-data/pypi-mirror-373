from setuptools import setup, find_packages

setup(
    name='lushalytics',
    version = '1.4.91',
    author='Moran Reznik',
    description = 'tools for quick and convenient data analysis',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'plotly'
    ]
)
