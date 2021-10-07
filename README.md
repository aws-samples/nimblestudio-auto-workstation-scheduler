## Nimble Studio Automated Workstation Scheduler

### Summary
This example deploys a complete stack which automates the launch of Nimble Studio streaming sessions on behalf of users.

* The [AWS CDK](https://aws.amazon.com/cdk/) is used for infrastructure-as-code and deployment.  
* Streaming sessions will be launched for users within an [AWS Nimble Studio](https://docs.aws.amazon.com/nimble-studio/latest/userguide/what-is-nimble-studio.html)

### Prerequisites

#### Nimble Studio
This project requires that you have already have an [AWS Nimble Studio](https://docs.aws.amazon.com/nimble-studio/latest/userguide/getting-started.html) created. The studio should have users and launch profiles active. Sessions for users and associated launch profiles will be configured to be launched automatically through deployment of this project.

#### Git
* Install [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
 
#### Python 3.x
* Install [Python](https://www.python.org/downloads/)

#### AWS
* An AWS account
* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
* AWS CLI [configured](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html#cli-configure-quickstart-config)
* [AWS CDK](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html)

### Setup

First, clone the repository to a local working directory:

```bash
git clone https://github.com/aws-samples/nimblestudio-auto-workstation-scheduler.git
```

Navigate into the project directory:

```bash
cd nimblestudio-auto-workstation-scheduler
```

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

### Deploy

#### Terminal
All deployment commands must be executed inside the *nimblestudio-auto-workstation-scheduler* folder, navigate there if you haven't already done so.

```bash
cd nimblestudio-auto-workstation-scheduler
```

Set the environment variables for the app: `CDK_DEFAULT_ACCOUNT`, `CDK_DEFAULT_REGION`.

Example:
```bash
CDK_DEFAULT_ACCOUNT=123456789012
CDK_DEFAULT_REGION=us-west-2
```

#### CDK Bootstrap Environment

This sample uses features of the AWS CDK that require you to [Bootstrap](https://docs.aws.amazon.com/cdk/latest/guide/bootstrapping.html) your environment (a combination of an AWS account and region). The sample is configured to use us-west-2 (Oregon), so you will just need to replace the placeholder in the below command with your AWS account number.

```bash
cdk bootstrap aws://ACCOUNT-NUMBER-1/us-west-2
```

#### NimbleStudioAutomatedWorkstation Stack
1. Deploy the project using the following command in the root of the NimbleStudioAutomatedWorkstation folder 

```bash
cdk deploy NimbleStudioAutoWorkstationSchedulerStack
```

### Update Configuration

To update the Automated Workstation Launch Configuration, see the README located at `scripts/README.md` and utilize the included helper scripts.

### Development

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

#### Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

### Dependencies

* [pynamodb](https://github.com/pynamodb/PynamoDB/blob/master/LICENSE): The MIT License (MIT)
