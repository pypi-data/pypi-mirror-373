from setuptools import setup, find_packages

setup(
    name="pycalgo",
    version="0.1.1",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['calculator.dll']
    },
    description="A Python calculator library using Go-based DLL implementation",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="Pranesh",
    author_email="praneshmadhan646@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.6",
)