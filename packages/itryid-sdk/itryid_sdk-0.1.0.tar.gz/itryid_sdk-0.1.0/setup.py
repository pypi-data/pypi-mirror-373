from setuptools import setup, find_packages

setup(
    name="itryid-sdk",
    version="0.1.0",
    author="Itry",
    author_email="support@ut.itrypro.ru",
    description="ItryID SDK for Python apps (registration, login, progress save)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/IGBerko/itryid-sdk",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.28.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ]
)
