import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aias_common",
    version="0.6.41",
    author="Gisaïa",
    description="ARLAS AIAS common library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(where="src"),
    python_requires='>=3.10',
    package_dir={'': 'src'},
    install_requires=['ecs_logging', 'google-cloud-storage==2.5.0', 'pydantic==2.10.6', 'requests==2.32.4',
                      'smart_open==6.2.0', 'boto3==1.24.89', 'fastapi_utilities']
)
