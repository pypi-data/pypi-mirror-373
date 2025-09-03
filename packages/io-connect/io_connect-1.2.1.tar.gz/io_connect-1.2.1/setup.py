from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="io_connect",
    version="1.2.1",
    author="Faclon-Labs",
    author_email="datascience@faclon.com",
    description="io connect library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "wheel",
        "pandas",
        "numpy",
        "pytz",
        "python_dateutil",
        "requests",
        "typing_extensions",
        "typeguard",
        "urllib3",
        "pymongo",
        "paho_mqtt==1.6.1",
    ],
    extras_require={
        "all": [
            "aiohttp",
            "asyncio",
            "polars",
            "aiofiles",
            "motor",

        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
