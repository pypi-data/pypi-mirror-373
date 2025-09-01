from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="liquidnn",
    version="1.1.2",
    packages=find_packages(),
    install_requires=["torch"],  # dependency
    description="A PyTorch based module for Liquid Networks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Nakshatra Yadav",
    author_email="nakshatrayadav1729@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
