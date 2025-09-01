import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "low-cost-ecs",
    "version": "0.0.169",
    "description": "Easy and low-cost ECS on EC2 server without a load balancer",
    "license": "MIT",
    "url": "https://github.com/rajyan/low-cost-ecs.git",
    "long_description_content_type": "text/markdown",
    "author": "Yohta Kimura<kitakita7617@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/rajyan/low-cost-ecs.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "low_cost_ecs",
        "low_cost_ecs._jsii"
    ],
    "package_data": {
        "low_cost_ecs._jsii": [
            "low-cost-ecs@0.0.169.jsii.tgz"
        ],
        "low_cost_ecs": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.37.0, <3.0.0",
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
