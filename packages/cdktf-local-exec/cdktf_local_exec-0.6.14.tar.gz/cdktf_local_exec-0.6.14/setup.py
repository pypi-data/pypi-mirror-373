import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdktf-local-exec",
    "version": "0.6.14",
    "description": "A simple construct that executes a command locally. This is useful to run build steps within your CDKTF Program or to run a post action after a resource is created.",
    "license": "MPL-2.0",
    "url": "https://github.com/cdktf/cdktf-local-exec.git",
    "long_description_content_type": "text/markdown",
    "author": "HashiCorp",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cdktf/cdktf-local-exec.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdktf_local_exec",
        "cdktf_local_exec._jsii"
    ],
    "package_data": {
        "cdktf_local_exec._jsii": [
            "cdktf-local-exec@0.6.14.jsii.tgz"
        ],
        "cdktf_local_exec": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "cdktf-cdktf-provider-null>=11.0.0",
        "cdktf>=0.21.0",
        "constructs>=10.4.2",
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
