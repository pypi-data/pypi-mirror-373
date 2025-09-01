import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdktf-tf-module-stack",
    "version": "7.0.13",
    "description": "A drop-in replacement for cdktf.TerraformStack that lets you define Terraform modules as constructs",
    "license": "MPL-2.0",
    "url": "https://github.com/cdktf/cdktf-tf-module-stack.git",
    "long_description_content_type": "text/markdown",
    "author": "HashiCorp",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cdktf/cdktf-tf-module-stack.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdktf_tf_module_stack",
        "cdktf_tf_module_stack._jsii"
    ],
    "package_data": {
        "cdktf_tf_module_stack._jsii": [
            "tf-module-stack@7.0.13.jsii.tgz"
        ],
        "cdktf_tf_module_stack": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
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
