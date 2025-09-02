from setuptools import setup, find_packages

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aminoac",
    version="0.1.0",
    description="A module that modifies CTRL-C behavior to play audio",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="kennylimz",
    author_email="",  # Add your email if you want
    url="https://github.com/kennylimz/aminoac",  # Add your GitHub repo URL
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pygame",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",  # Change this if you have a different license
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="audio, signal, ctrl-c, pygame, mp3",
    project_urls={
        "Bug Reports": "https://github.com/kennylimz/aminoac/issues",
        "Source": "https://github.com/kennylimz/aminoac",
    },
)
