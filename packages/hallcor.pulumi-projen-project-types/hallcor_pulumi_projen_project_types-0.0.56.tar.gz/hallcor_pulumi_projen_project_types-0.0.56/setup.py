import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "hallcor.pulumi-projen-project-types",
    "version": "0.0.56",
    "description": "@hallcor/pulumi-projen-project-types",
    "license": "Apache-2.0",
    "url": "https://github.com/corymhall/pulumi-projen-project-types.git",
    "long_description_content_type": "text/markdown",
    "author": "corymhall<43035978+corymhall@users.noreply.github.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/corymhall/pulumi-projen-project-types.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "hallcor.pulumi_projen_project_types",
        "hallcor.pulumi_projen_project_types._jsii"
    ],
    "package_data": {
        "hallcor.pulumi_projen_project_types._jsii": [
            "pulumi-projen-project-types@0.0.56.jsii.tgz"
        ],
        "hallcor.pulumi_projen_project_types": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "constructs>=10.4.2, <11.0.0",
        "jsii>=1.113.0, <2.0.0",
        "projen>=0.95.4, <0.96.0",
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
