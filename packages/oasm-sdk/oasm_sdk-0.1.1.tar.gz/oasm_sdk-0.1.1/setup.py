from setuptools import setup, find_packages

setup(
    name="oasm_sdk",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
         "requests",
    ],
    description="Python SDK for OASM platform",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="OASM",
    author_email="tuanthanh2kk4@gmail.com",
    url="https://github.com/oasm/oasm-sdk-python",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)