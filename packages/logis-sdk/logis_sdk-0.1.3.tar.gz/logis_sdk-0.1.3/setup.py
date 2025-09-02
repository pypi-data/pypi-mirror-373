from setuptools import find_packages, setup

from logis import __version__

setup(
    name="logis-sdk",
    version=__version__,
    description="络捷斯特 Python 模块合集",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="leoking",
    author_email="present150608@sina.com",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.12",
)
