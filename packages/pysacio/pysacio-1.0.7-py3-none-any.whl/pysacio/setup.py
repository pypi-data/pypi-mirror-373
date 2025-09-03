from setuptools import setup
from os import environ

version = "1.0.0"
if "VERSION" in environ.keys():
    version = environ["VERSION"]

setup(
    name="pysacio",
    version=version,
    packages=["pysacio"],
    url="",
    long_description_content_type="text/markdown",
    long_description="Updated Fork really close to the original project pysacio"
    " [https://github.com/emolch/pysacio](https://github.com/emolch/pysacio).",
    description="Python module to read and write binary SAC (Seismic Analysis Code) files.",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    install_requires=["numpy>=2"],
    license="2-clause BSD",
    package_data={"pysacio": ["README", "COPYING"]},
)
