import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-budibase",
    "version": "0.0.751",
    "description": "Use AWS CDK to create budibase server",
    "license": "Apache-2.0",
    "url": "https://github.com/neilkuan/cdk-budibase.git",
    "long_description_content_type": "text/markdown",
    "author": "Neil Kuan<guan840912@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/neilkuan/cdk-budibase.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_budibase",
        "cdk_budibase._jsii"
    ],
    "package_data": {
        "cdk_budibase._jsii": [
            "cdk-budibase@0.0.751.jsii.tgz"
        ],
        "cdk_budibase": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.63.0, <3.0.0",
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
