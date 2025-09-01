from setuptools import setup, find_packages

setup(
    name="tamil_niral",
    version="1.0.1",
    description="Tamil programming language ",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Nithesh M",
    url="https://github.com/yourusername/tamil_niral",
    packages=find_packages(include=["tamil_niral", "tamil_niral.*"]),
    entry_points={'console_scripts': ['tamil_niral=tamil_niral.interpreter:main']},
    python_requires='>=3.7',
)

entry_points={
    'console_scripts': [
        'tamil_niral=tamil_niral.interpreter:main'
    ],
},

# pypi-AgEIcHlwaS5vcmcCJDEzZDUwYjkxLTE5MzMtNDUwNC1iMGNhLTdlN2I3OTVjMzQxYQACKlszLCI3OGRjM2M5My1iMzJjLTRmMjUtYWRjNC0yMTE1ZWMyZDcwYmEiXQAABiBXX3jfN9uRMPjlBVmJBCZK1Fc8uZylHfgQS6JM84hucA