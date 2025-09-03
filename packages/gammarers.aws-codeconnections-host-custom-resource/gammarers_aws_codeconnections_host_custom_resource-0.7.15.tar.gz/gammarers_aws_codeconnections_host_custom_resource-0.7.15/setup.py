import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "gammarers.aws-codeconnections-host-custom-resource",
    "version": "0.7.15",
    "description": "This AWS CDK Construct provides a custom resource (Lambda Function) to create a connection host for Self-Managed GitLab, which is not yet supported by CloudFormation. Additionally, even after creating the Host and the connection, authentication must be done via a browser.",
    "license": "Apache-2.0",
    "url": "https://github.com/gammarers/aws-codeconnections-host-custom-resource.git",
    "long_description_content_type": "text/markdown",
    "author": "yicr<yicr@users.noreply.github.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/gammarers/aws-codeconnections-host-custom-resource.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "gammarers.aws_codeconnections_host_custom_resource",
        "gammarers.aws_codeconnections_host_custom_resource._jsii"
    ],
    "package_data": {
        "gammarers.aws_codeconnections_host_custom_resource._jsii": [
            "aws-codeconnections-host-custom-resource@0.7.15.jsii.tgz"
        ],
        "gammarers.aws_codeconnections_host_custom_resource": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.189.1, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "gammarers.aws-resource-naming>=0.10.1, <0.11.0",
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
