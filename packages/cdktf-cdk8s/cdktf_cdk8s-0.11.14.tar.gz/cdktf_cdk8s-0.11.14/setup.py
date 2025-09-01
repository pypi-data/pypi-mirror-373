import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdktf-cdk8s",
    "version": "0.11.14",
    "description": "A compatibility layer for using cdk8s constructs within Terraform CDK.",
    "license": "MPL-2.0",
    "url": "https://github.com/cdktf/cdktf-cdk8s.git",
    "long_description_content_type": "text/markdown",
    "author": "HashiCorp",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cdktf/cdktf-cdk8s.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdktf_cdk8s",
        "cdktf_cdk8s._jsii"
    ],
    "package_data": {
        "cdktf_cdk8s._jsii": [
            "cdktf-cdk8s@0.11.14.jsii.tgz"
        ],
        "cdktf_cdk8s": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "cdk8s>=2.8.0",
        "cdktf-cdktf-provider-kubernetes>=12.0.0",
        "cdktf>=0.21.0",
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
