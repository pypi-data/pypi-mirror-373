import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="logos-sdk",
    version=os.getenv("VERSION"),
    author="Databy.io",
    author_email="admin@proficio.cz",
    description="SDK for Logos platform",
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/databy/logos-sdk-pip/src/master/",
    packages=["logos_sdk", "logos_sdk.services", "logos_sdk.logging", "logos_sdk.big_query"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    # List of already included dependencies https://cloud.google.com/functions/docs/writing/specifying-dependencies-python
    # FOR DEBUG: List of packages installed in CF will be in /layers/google.python.pip/pip/lib/python3.9/site-packages
    install_requires=[
        "requests",
        "google-auth",
        "google-cloud-logging",
        "google-cloud-bigquery",
        "python-dotenv",
        "google-api-python-client",
        "httplib2",
        "pandas",
        "db-dtypes",
        "numpy",
    ],
)
