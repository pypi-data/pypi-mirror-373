import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cdc-automation",
    version="0.0.10",
    author="Wayne Chen",
    author_email="kensmart123@yahoo.com.tw",
    description="only for cdc own study used",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    # project_urls={
    #     "Source": ""
    # },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'requests',
        'python-json-logger',
        'concurrent-log-handler',  # handle issue for RotatingFileHandler under Windows.
        'jsonschema',
        'webcolors',  # jsonschema validating formats
        'rfc3339-validator',  # jsonschema validating formats
        'isoduration',  # jsonschema validating formats
        'fqdn',  # jsonschema validating formats
        'idna',  # jsonschema validating formats
        'rfc3987',  # jsonschema validating formats
        'jsonpointer',  # jsonschema validating formats
        'uri-template',  # jsonschema validating formats
        'pycryptodome',  # handle AES, RSA crypto
    ]
)