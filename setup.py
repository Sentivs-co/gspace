from setuptools import find_packages, setup

with open("README.md") as fh:
    long_description = fh.read()

with open("LICENSE") as fh:
    license = fh.read()

setup(
    name="gspace",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "google-api-python-client>=2.179.0,<3.0.0",
        "google-auth-httplib2>=0.2.0,<0.3.0",
        "google-auth-oauthlib>=1.2.2,<2.0.0",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    license=license,
    author="Prasant Poudel",
    author_email="dev@sentivs.com",
    url="https://github.com/Sentivs-co/gspace",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
