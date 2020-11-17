import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="packageName",
    version="0.1.000",
    author="Author Name",
    author_email="Author Mail",
    description="Description",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="Git link",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
