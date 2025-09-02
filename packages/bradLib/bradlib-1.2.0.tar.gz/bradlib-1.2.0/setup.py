from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="bradLib",
    version="1.2.0",
    license="MIT",
    description="""Bradley Day's personal library""",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Bradley Day",
    packages=find_packages(include=["bradLib"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=required,
    url="https://github.com/BradADDay/bradLib",
)
