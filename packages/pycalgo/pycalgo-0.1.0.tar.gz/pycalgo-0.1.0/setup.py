from setuptools import setup

setup(
    name="pycalgo",
    version="0.1.0",
    py_modules=["pycal"],
    include_package_data=True,
    package_data={"": ["calculator.dll"]},
)
