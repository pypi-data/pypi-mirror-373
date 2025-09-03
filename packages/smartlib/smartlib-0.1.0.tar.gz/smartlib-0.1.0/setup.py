from setuptools import setup, find_packages

setup(
    name="smartlib",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "web3",
        "py-solc-x"
    ],
)
