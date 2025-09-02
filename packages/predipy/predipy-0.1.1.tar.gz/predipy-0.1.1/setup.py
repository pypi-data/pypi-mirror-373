from setuptools import setup, find_packages

setup(
    name="predipy",
    version="0.1.1",
    author="Iyazkasep",
    author_email="Iyaz.kasep2009@gmail.com",
    description="Lightweight Python library for prediction & regression",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://example.com/",  # placeholder valid
    packages=find_packages(),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

