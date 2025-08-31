import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-ecs-service-extensions",
    "version": "2.0.1.a739",
    "description": "The CDK Construct Library that helps you build ECS services using simple extensions",
    "license": "Apache-2.0",
    "url": "https://github.com/cdklabs/cdk-ecs-service-extensions.git",
    "long_description_content_type": "text/markdown",
    "author": "Amazon Web Services",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cdklabs/cdk-ecs-service-extensions.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_ecs_service_extensions",
        "cdk_ecs_service_extensions._jsii"
    ],
    "package_data": {
        "cdk_ecs_service_extensions._jsii": [
            "ecs-service-extensions@2.0.1-alpha.739.jsii.tgz"
        ],
        "cdk_ecs_service_extensions": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.52.0, <3.0.0",
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
