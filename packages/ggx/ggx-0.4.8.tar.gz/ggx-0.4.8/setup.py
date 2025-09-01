from setuptools import setup, find_packages

setup(
    name="ggx",
    version="0.4.8",
    description="API for GoodGame Empire",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="mst4ck",
    author_email="mst4ck@mailfence.com",
    license="MIT",
    packages=find_packages(),      
    install_requires=[
        "websockets>=15.0.1",
        "loguru>=0.7.3",
        "aiohttp>=3.12.13",
    ],
    python_requires=">=3.12",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
