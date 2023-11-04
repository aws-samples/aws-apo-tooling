# EC2 Instance Type and Pricing Lookup API

This repo contains an example of an API interface to the AWS Pricing (Price List) data. AWS Lambda and Amazon API Gateway are used in combination with the Python Boto3 package to lookup EC instance types that match specific OS, vCPU and memory, as well as the monthly recurring AWS price for the match instances. The current filters apply to 3 Year, No-Upfront, Reserved (3YNUR) instances, though can be changed in the *.py files provided. This API was built to integrate with scripts used for Partner/Customer pursuits in order to quickly parse large asset files in order to produce a Rough Order of Magnitude (ROM) estimate of recurring spend and Total Contract Value (TCV) during initial engagement. Examples are given for various filter types that may be applied, as well as sample responses from the Price List. The code within can be modified for other filters and/or AWS products/services using the same format as provided. Code for CDK deployment, as well as command-line script is provided. 

## Content

- [EC2 Instance Type and Pricing Lookup API](#ec2-instance-type-and-pricing-lookup-api)
  - [Content](#content)
- [Code Walk-through](#code-walk-through)
  - [Repository Structure](#repository-structure)
    - [Scripts in this directory](#scripts-in-this-directory)
    - [EC2 Lookup Example CDK](#ec2-lookup-example-cdk)
    - [EC2 Pricing Output Example](#ec2-pricing-output-example)
- [Usage](#usage)
  - [Requirements and Configuration](#requirements-and-configuration)
  - [Running the Python Scripts](#running-the-python-scripts)
  - [Deploying the CDK Stack](#deploying-the-cdk_stack)

# Code Walk-through

## Repository Structure

```sh
.
├── ec2-lookup-cdk                      # <-- the main directory for all CDK components required for deployment
    ├── cdk-generated-baseline-files    # <-- various required files for use of CDK (requirements.txt, virtual env, tests, etc.)
    ├── ec2_lookup_example              # <-- the directory containing the stack definition
        ├── ec2_lookup_example_stack.py # <-- the cdk stack construct
    ├── lambda                          # <-- the directory containing the lambda function code used for cdk deployment
        ├── poc-v1-ec2-lookup.py        # <-- the lambda code
    ├── app.py                          # <-- the cdk app definition
├── python-scripts                      # <-- the directory for stand-alone python scripts
    ├── ec2-lookup.py                   # <-- part one of the lambda functionality; returns EC2 instance types based on OS, vCPU and memory
    ├── pricing-lookup.py               # <-- part two of the lambda functionality; returns the pricing for a specific EC2 type
├── ec2-pricing-output-example.json     # <-- a sample file that shows the JSON structure of the pricing API outputs
└── README.md                           # <-- this file
```

### Scripts in this directory

1. **_`python-scripts/ec2-lookup.py`_** - this scripts contains the logic that returns all 3YNUR EC2 instances for specific region, os, vcpu and memory 
2. **_`python-scripts/pricing-lookup.py`_** - this script contains the logic that returns the AWS monthly price for a specific os and instance type

### EC2 Lookup Example CDK

- this directory contains all the components necessary to run a 'cdk deploy' from within the directory in order to create Lambda-API Gateway functionality within a VPC

### EC2 Pricing Output Example

- this file shows the JSON output of an EC2 Pricing query with minial fliters for us-east-1 in order to show possible filter options


# Usage

## Requirements and Configuration

**Requirements.** Versions are shown that were used during the development of this package, other versions may work, but have not been tested.

1.  Python 3.10 or higher
2.  AWS CLI and Boto3 installation
3.  Node.js version 18 or higher
4.  npm version 10 or higher
5.  pip 23 or higher
6.  Installation of the aws-ckd-lib Python module ($> pip install aws-cdk-lib)
7.  Other required modules have been included in the CDK requirements.txt and requirements-dev.txt

**Configuration.** 

1.  Modify the ec2-lookup-cdk/app.py for the specific VPC account and AWS region where the CDK will deploy

##  Running the Python Scripts

1.  Clone the GitLb repo git@ssh.gitlab.aws.dev:sthaws/ec2-lookup-and-pricing-example-api.git
2.  From a command-line, navigate to the python-scripts directory
3.  At the command line run the following:
        - python ec2-lookup.py <region> <os> <vcpu> <memory> | example: python ec2-lookup.py us-east-1 RHEL 4 16
        - python pricing-lookup.py <region> <os> <instance-type> | example: python pricing-lookup.py us-east-1 RHEL t3.large

## Deploying the CDK Stack

1. Clone the GitLab repo git@ssh.gitlab.aws.dev:sthaws/ec2-lookup-and-pricing-example-api.git
2. From a command-line, navigate to the ec2-lookup-example
3. Run the deploy command ($ cdk deploy)
4. When done with the stack, destroy the stack ($ cdk destroy)
