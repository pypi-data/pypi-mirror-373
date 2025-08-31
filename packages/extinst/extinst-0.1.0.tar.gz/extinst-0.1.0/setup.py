from setuptools import setup, find_packages

# 尝试读取README.md或README.rst作为长描述
long_description = ""
long_description_content_type = "text/plain"

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
    long_description_content_type = "text/markdown"
except FileNotFoundError:
    try:
        with open("README.rst", "r", encoding="utf-8") as fh:
            long_description = fh.read()
        long_description_content_type = "text/x-rst"
    except FileNotFoundError:
        pass

setup(
    name="extinst",
    version="0.1.0",
    author="CodeTea",
    author_email="codeteamail@gmail.com",
    description="A Python module to automatically install Chrome extensions on Windows/Mac/Linux",
    long_description=long_description,
    long_description_content_type=long_description_content_type,
    url="https://github.com/codete2/",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
    ],
    python_requires='>=3.6',
    install_requires=[
        "requests"
    ],
)