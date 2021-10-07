import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="nimble_studio_auto_workstation_scheduler",
    version="0.0.1",

    description="A CDK Python app to automate launch of Nimble Studio workstations for users",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "nimble_studio_auto_workstation_scheduler"},
    packages=setuptools.find_packages(where="nimble_studio_auto_workstation_scheduler"),

    install_requires=[
        "aws-cdk.core==1.117.0",
        "aws-cdk.aws_lambda",
        "aws-cdk.aws_dynamodb",
        "boto3>=1.18.19",
        "botocore>=1.21.19",
        "pynamodb>=5.1.0",
        "aws-cdk.aws_events",
        "aws-cdk.aws_events_targets"
    ],

    python_requires=">=3.7",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
