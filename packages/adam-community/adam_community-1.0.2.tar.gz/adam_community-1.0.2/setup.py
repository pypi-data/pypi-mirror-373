from setuptools import setup, find_packages
import os

setup(
    name="adam_community",
    version="1.0.2",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "click>=8.0.0",
        "docstring-parser>=0.15",
        "rich>=13.0.0",
    ],
    entry_points={
        'console_scripts': [
            'adam-cli=adam_community.cli.cli:cli',
        ],
    },
    author="Adam Community",
    author_email="admin@sidereus-ai.com",
    description="Adam Community Tools and Utilities",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/adam-community",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
) 