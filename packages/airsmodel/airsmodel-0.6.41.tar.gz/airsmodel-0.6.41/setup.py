
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="airsmodel",
    version="0.6.41",
    author="Gisaïa",
    description="ARLAS Item Registration Service Model",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    python_requires='>=3.10',
    py_modules=["airs.core.models.model", "airs.core.models.mapper"],
    package_dir={'': 'src'},
    install_requires=[]
)
