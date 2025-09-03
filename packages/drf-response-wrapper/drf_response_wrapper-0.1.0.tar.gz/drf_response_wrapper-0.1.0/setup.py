from setuptools import setup, find_packages

setup(
    name="drf-response-wrapper",   # unique name PyPI এ
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Django>=3.2",
        "djangorestframework>=3.12"
    ],
    license="MIT",
    description="DRF middleware to wrap all API responses and handle exceptions",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Md Harun Or Roshed Riyad",
    author_email="rieadhasan499@gmail.com",
    url="https://github.com/yourusername/drf-response-wrapper",
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
    ],
)
