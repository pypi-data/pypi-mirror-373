import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-vscode-server",
    "version": "0.0.51",
    "description": "Running VS Code Server on AWS",
    "license": "Apache-2.0",
    "url": "https://github.com/MV-Consulting/cdk-vscode-server.git",
    "long_description_content_type": "text/markdown",
    "author": "Manuel Vogel<info@manuel-vogel.de>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/MV-Consulting/cdk-vscode-server.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk-vscode-server",
        "cdk-vscode-server._jsii"
    ],
    "package_data": {
        "cdk-vscode-server._jsii": [
            "cdk-vscode-server@0.0.51.jsii.tgz"
        ],
        "cdk-vscode-server": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.190.0, <3.0.0",
        "cdk-nag>=2.35.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.113.0, <2.0.0",
        "mvc-projen>=0.0.7, <0.0.8",
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
