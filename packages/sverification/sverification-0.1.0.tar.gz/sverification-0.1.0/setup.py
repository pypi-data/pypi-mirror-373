from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sverification",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pdforensic>=0.1.0",
        "pdfplumber>=0.6.0",
    ],
    extras_require={
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black",
            "flake8",
        ],
    },
    entry_points={
        "console_scripts": [
            "verify-statement=sverification.compare_metadata:main",
        ],
    },
    author="Alex Mkwizu @ Black Swan AI",
    author_email="alex@bsa.ai",
    description="A tool for verifying PDF statements from Tanzanian and beyond institutions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Tausi-Africa/statement-verification",
    project_urls={
        "Bug Tracker": "https://github.com/Tausi-Africa/statement-verification/issues",
        "Repository": "https://github.com/Tausi-Africa/statement-verification",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: Other/Proprietary License",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    keywords="pdf verification statements metadata financial",
)