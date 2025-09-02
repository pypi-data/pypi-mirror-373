from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="atlasrun",
    version="0.1.0",
    description="A lightweight local task queue and execution manager for batch command-line jobs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Haopeng Yu",
    author_email="atlasbioin4@gmail.com",
    url="https://github.com/atlasbioinfo/atlasrun", 
    packages=find_packages(),
    install_requires=[
        "tabulate>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "arun=atlasrun.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    keywords="task queue, command line, batch jobs, process management",
    project_urls={
        "Bug Reports": "https://github.com/atlasbioinfo/atlasrunissues",
        "Source": "https://github.com/atlasbioinfo/atlasrun",
    },
)
