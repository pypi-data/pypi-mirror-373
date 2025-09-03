import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dataframe_helpers",
    version="0.0.10",
    author="Richard Peschke",
    author_email="peschke@hawaii.edu",
    description="some helpers for pandas dataframes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RPeschke/dataframe_helpers",
    project_urls={
        "Bug Tracker": "https://github.com/RPeschke/dataframe_helpers/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
          'pandas',
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)