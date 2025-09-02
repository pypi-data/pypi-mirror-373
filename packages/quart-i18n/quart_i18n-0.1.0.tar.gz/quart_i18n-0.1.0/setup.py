from setuptools import setup, find_packages

setup(
    name="quart-i18n",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "quart",
    ],
    author="1bali1",
    author_email="info@1bali1.hu",
    description="This package helps you with your Quart's app localization!",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/1bali1/quart-i18n",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires=">=3.10",
    license="MIT"
)
