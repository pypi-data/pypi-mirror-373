from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="drf_response_wrapper",
    version="0.1.5",
    packages=find_packages(),
    include_package_data=True,
    description="DRF middleware to wrap all API responses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Md Harun Or Roshed Riyad",
    author_email="rieadhasan499@gmail.com",
    url="https://github.com/yourusername/drf-response-wrapper",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
)
