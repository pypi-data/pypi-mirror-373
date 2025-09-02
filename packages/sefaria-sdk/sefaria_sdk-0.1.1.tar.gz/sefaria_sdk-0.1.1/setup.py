from setuptools import setup, find_packages

setup(
    name="sefaria-sdk",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    author="Robert Jones",
    author_email="",
    description="Unofficial Python SDK for the Sefaria API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/rbrtjns90/unofficial_sefaria_python_sdk",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
