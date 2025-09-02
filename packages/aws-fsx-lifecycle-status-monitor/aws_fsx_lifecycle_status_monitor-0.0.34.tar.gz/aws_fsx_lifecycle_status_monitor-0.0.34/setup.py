import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "aws-fsx-lifecycle-status-monitor",
    "version": "0.0.34",
    "description": "aws-fsx-lifecycle-status-monitor",
    "license": "Apache-2.0",
    "url": "https://stefanfreitag.github.io/AWS-FSx-Lifecycle-Status-Monitor",
    "long_description_content_type": "text/markdown",
    "author": "Stefan Freitag<stefan.freitag@udo.edu>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/stefanfreitag/AWS-FSx-Lifecycle-Status-Monitor"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "aws_fsx_lifecycle_status_monitor",
        "aws_fsx_lifecycle_status_monitor._jsii"
    ],
    "package_data": {
        "aws_fsx_lifecycle_status_monitor._jsii": [
            "aws-fsx-lifecycle-status-monitor@0.0.34.jsii.tgz"
        ],
        "aws_fsx_lifecycle_status_monitor": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.165.0, <3.0.0",
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
        "Development Status :: 4 - Beta",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
