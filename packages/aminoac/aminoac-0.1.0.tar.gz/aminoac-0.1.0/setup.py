from setuptools import setup, find_packages

setup(
    name="aminoac",
    version="0.1.0",
    description="A module that modifies CTRL-C behavior to play audio",
    author="kennylimz",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pygame",
    ],
    python_requires=">=3.6",
)
