import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="treefiles",
    version="0.1.047",
    author="Gaetan Desrues",
    author_email="gdesrues@gmail.com",
    description="Description",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GaetanDesrues/TreeFiles",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
