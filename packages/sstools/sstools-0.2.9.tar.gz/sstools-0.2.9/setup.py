import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="sstools",  # Replace with your own username
    version="0.2.9",
    author="Roman Arnet",
    author_email="arnet@dlab.ch",
    description="swimstats tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://swimstats.net",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
    ],
)