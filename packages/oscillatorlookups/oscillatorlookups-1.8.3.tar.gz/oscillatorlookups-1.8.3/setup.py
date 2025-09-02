
from setuptools import setup, find_packages

VERSION = '1.8.3'
DESCRIPTION = 'Lookup operations for oscillator database'
LONG_DESCRIPTION = 'Lookup operations for oscillator database, hosted on github'

# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="oscillatorlookups",
    version=VERSION,
    author="Matthew Epshtein",
    author_email="<epshteinmatthew@gmail.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        "aiohttp",
        "aiofiles",
        "msgspec"
    ],  # add any additional packages that
    # needs to be installed along with your package. Eg: 'caer'

    keywords=['python', 'first package'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)