from setuptools import setup, find_packages

setup(
    name="lukhed_basic_utils",
    version="1.6.5",
    description="A collection of basic utility functions",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="lukhed",
    author_email="lukhed.mail@gmail.com",
    url="https://github.com/lukhed/lukhed_basic_utils",
    packages=find_packages(),
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "python-dateutil>=2.9.0",
        "requests>=2.32.3",
        "beautifulsoup4>=4.12.3",
        "fake-useragent>=2.0.3",
        "tzdata>=2023.3",   
        "PyGithub>= 2.5.0",
        "matplotlib>=3.10.1",
        "numpy>=2.2.4",
        "pandas>=2.2.3",
        "scipy>=1.15.2",
        "mysql-connector-python>=8.0.0",
        "psycopg2-binary>=2.9.10"
    ],
)