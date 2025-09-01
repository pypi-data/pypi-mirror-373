import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-cloudformation-datadog-integrations-awsaccount",
    "version": "1.0.0.a7",
    "description": "Datadog AWS Account Integration 1.0.0",
    "license": "Apache-2.0",
    "url": "https://github.com/cdklabs/cdk-cloudformation.git",
    "long_description_content_type": "text/markdown",
    "author": "Amazon Web Services",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cdklabs/cdk-cloudformation.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_cloudformation_datadog_integrations_awsaccount",
        "cdk_cloudformation_datadog_integrations_awsaccount._jsii"
    ],
    "package_data": {
        "cdk_cloudformation_datadog_integrations_awsaccount._jsii": [
            "datadog-integrations-awsaccount@1.0.0-alpha.7.jsii.tgz"
        ],
        "cdk_cloudformation_datadog_integrations_awsaccount": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.211.0, <3.0.0",
        "constructs>=10.4.2, <11.0.0",
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
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
