from setuptools import setup, find_packages


with open('README.md', 'r') as f:
    description = f.read()

setup(
    name="cliface",
    version="1.0.2",
    description="A CLI toolkit library.",
    packages=find_packages(where="."),
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/iamtwobe/cliface",
    author="iamtwobe",
    author_email="contato.iamtwobe@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "prompt_toolkit>=3.0.50",
        "wcwidth>=0.2.13"
        ],
    include_package_data=True,
    package_data={
        "cliface": ["themes/*.json"],
    },
    python_requires=">=3.12",
)