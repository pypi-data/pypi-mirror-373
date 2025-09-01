from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="itryid-sdk",
    version="2.0.0",
    author="Itry",
    author_email="support@ut.itrypro.ru",
    description="Modern ItryID SDK for Python apps with improved architecture, type safety, and error handling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IGBerko/itryid-sdk",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.28.0",
        "typing-extensions>=4.0.0; python_version<'3.8'"
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "mypy>=1.0.0",
            "flake8>=5.0.0"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Games/Entertainment",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ],
    keywords="authentication, gaming, progress, sdk, api"
)
