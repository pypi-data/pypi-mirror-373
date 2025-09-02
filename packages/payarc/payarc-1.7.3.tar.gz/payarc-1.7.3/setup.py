from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="payarc",
    version="1.7.3",
    description="Payarc Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Payarc/payarc-sdk-python",
    author="Payarc",
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8"
    ],
    package_dir={"": "src"},
    python_requires=">=3.7, <4",
    install_requires=['httpx', 'asyncio'],
)