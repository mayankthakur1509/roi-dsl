"""
ROI-DSL Compiler v2.1
Setup configuration
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="roi-dsl-compiler",
    version="2.1.0",
    author="HyperAIMarketing",
    author_email="dev@hyperaimarketing.com",
    description="ROI-DSL Compiler - Value-First Domain-Specific Language for marketing automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hyperaimarketing/roi-dsl",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Compilers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        # Pure Python - no external dependencies required for v2.1
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "flake8>=4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "roi=roi_compile:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.ebnf", "*.md"],
    },
)
