from setuptools import find_packages
from setuptools import setup
from setuptools.command.install import install

setup(
    name="eagle-test-graphs",
    version="0.1.21",
    packages=find_packages(where="eagle_test_graphs"),
    package_dir={"": "eagle_test_graphs"},
    package_data={"": ["*.graph", "*.pkl", "*.json", "*.spec"]},
)
