import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "robhan_cdk_lib.aws_grafana",
    "version": "0.0.99",
    "description": "AWS CDK Construct Library for Amazon Managed Grafana",
    "license": "MIT",
    "url": "https://github.com/robert-hanuschke/cdk-aws_grafana",
    "long_description_content_type": "text/markdown",
    "author": "Robert Hanuschke<robhan-cdk-lib@hanuschke.eu>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/robert-hanuschke/cdk-aws_grafana"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "robhan_cdk_lib.aws_grafana",
        "robhan_cdk_lib.aws_grafana._jsii"
    ],
    "package_data": {
        "robhan_cdk_lib.aws_grafana._jsii": [
            "aws_grafana@0.0.99.jsii.tgz"
        ],
        "robhan_cdk_lib.aws_grafana": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.198.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.113.0, <2.0.0",
        "publication>=0.0.3",
        "robhan_cdk_lib.utils>=0.0.32, <0.0.33",
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
