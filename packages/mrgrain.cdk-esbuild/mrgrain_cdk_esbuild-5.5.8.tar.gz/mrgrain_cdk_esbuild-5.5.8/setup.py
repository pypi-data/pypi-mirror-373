import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "mrgrain.cdk-esbuild",
    "version": "5.5.8",
    "description": "CDK constructs for esbuild, an extremely fast JavaScript bundler",
    "license": "MIT",
    "url": "https://github.com/mrgrain/cdk-esbuild",
    "long_description_content_type": "text/markdown",
    "author": "Moritz Kornher<mail@moritzkornher.de>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/mrgrain/cdk-esbuild"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "mrgrain.cdk_esbuild",
        "mrgrain.cdk_esbuild._jsii"
    ],
    "package_data": {
        "mrgrain.cdk_esbuild._jsii": [
            "cdk-esbuild@5.5.8.jsii.tgz"
        ],
        "mrgrain.cdk_esbuild": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.51.0, <3.0.0",
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
