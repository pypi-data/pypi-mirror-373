import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "shady-island",
    "version": "0.1.68",
    "description": "Utilities and constructs for the AWS CDK",
    "license": "Apache-2.0",
    "url": "https://libreworks.github.io/shady-island/",
    "long_description_content_type": "text/markdown",
    "author": "LibreWorks Contributors",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com:libreworks/shady-island.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "shady_island",
        "shady_island._jsii",
        "shady_island.automation",
        "shady_island.configuration",
        "shady_island.networking"
    ],
    "package_data": {
        "shady_island._jsii": [
            "shady-island@0.1.68.jsii.tgz"
        ],
        "shady_island": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.177.0, <3.0.0",
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
