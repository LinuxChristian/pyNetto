from setuptools import setup

setup(
    name='pyNetto',
    version='1.0',
    description='A useful library to process reciepts from the Danish supermarket Netto',
    author='Christian Juncker Brædstrup',
    author_email='christian@junckerbraedstrup.dk',
    packages=['pyNetto'],
    install_requires=['bs4', 'html5lib', 'pandas', 'lxml'],
)
