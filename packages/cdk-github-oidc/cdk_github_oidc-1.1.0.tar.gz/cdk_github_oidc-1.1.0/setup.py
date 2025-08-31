import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-github-oidc",
    "version": "1.1.0",
    "description": "AWS CDK construct to create OIDC roles for CircleCI jobs",
    "license": "Apache-2.0",
    "url": "https://github.com/blimmer/cdk-github-oidc.git",
    "long_description_content_type": "text/markdown",
    "author": "Ben Limmer<hello@benlimmer.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/blimmer/cdk-github-oidc.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_github_oidc",
        "cdk_github_oidc._jsii"
    ],
    "package_data": {
        "cdk_github_oidc._jsii": [
            "cdk-github-oidc@1.1.0.jsii.tgz"
        ],
        "cdk_github_oidc": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.73.0, <3.0.0",
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
