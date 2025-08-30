import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-s3-vectors",
    "version": "0.1.4",
    "description": "cdk-s3-vectors",
    "license": "Apache-2.0",
    "url": "https://github.com/bimnett/cdk-s3-vectors.git",
    "long_description_content_type": "text/markdown",
    "author": "Bimnet Tesfamariam<bimnett@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/bimnett/cdk-s3-vectors.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_s3_vectors",
        "cdk_s3_vectors._jsii"
    ],
    "package_data": {
        "cdk_s3_vectors._jsii": [
            "cdk-s3-vectors@0.1.4.jsii.tgz"
        ],
        "cdk_s3_vectors": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.205.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.113.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
