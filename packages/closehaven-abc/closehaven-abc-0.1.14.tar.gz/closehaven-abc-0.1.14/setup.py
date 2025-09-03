from setuptools import setup, find_packages

setup(
    name="closehaven-abc",
    version="0.1.14",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.115.0",
        "pydantic==2.9.2",
        "azure-storage-blob==12.23.0",
        "certifi==2024.8.30",
        "beanie==1.26.0",
        "motor==3.6.0",
        "aio-pika==9.4.3",
        "async-timeout==4.0.3",
        "pyjwt==2.9.0",
        "uvloop==0.20.0",
        "redis==5.0.8",
    ],
)
