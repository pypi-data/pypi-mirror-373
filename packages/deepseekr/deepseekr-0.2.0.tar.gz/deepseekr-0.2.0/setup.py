from setuptools import setup, find_packages
import os

def read(fname):
    return open(fname).read() if os.path.exists(fname) else ""

setup(
    name="deepseekr",
    version="0.2.0",
    packages=find_packages(),
    include_package_data=True,
    author="Yusuf YILDIRIM",
    author_email="yusuf@tachion.tech",
    description="Selenium DeepSeek automation, using Google Chrome.",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/MYusufY/deepseekr",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: Proxy Servers",
        "Topic :: System :: Networking",
    ],
    python_requires=">=3.8",
    install_requires=[
        "selenium>=4.0.0",
        "undetected-chromedriver>=3.0.0",
        "markdownify>=0.11.6",
    ],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "flake8",
        ]
    },
)