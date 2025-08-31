from setuptools import setup, find_packages

setup(
    name="gadapt",
    version="0.4.23",
    author="Zoran Jankovic",
    author_email="bpzoran@yahoo.com",
    url="https://github.com/bpzoran/gadapt",
    packages=find_packages(),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    description="GAdapt: A Python Library for\
        Self-Adaptive Genetic Algorithm.",
    install_requires=["numpy==1.26.4"],
)
