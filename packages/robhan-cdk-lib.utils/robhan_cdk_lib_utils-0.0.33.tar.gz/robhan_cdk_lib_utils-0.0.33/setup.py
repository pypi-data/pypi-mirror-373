import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "robhan_cdk_lib.utils",
    "version": "0.0.33",
    "description": "@robhan-cdk-lib/utils",
    "license": "MIT",
    "url": "https://github.com/robert-hanuschke/cdk-utils",
    "long_description_content_type": "text/markdown",
    "author": "Robert Hanuschke<robhan-cdk-lib@hanuschke.eu>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/robert-hanuschke/cdk-utils"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "robhan_cdk_lib.utils._jsii"
    ],
    "package_data": {
        "robhan_cdk_lib.utils._jsii": [
            "utils@0.0.33.jsii.tgz"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
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
