#!/usr/bin/env python3
import os

from aws_cdk import core as cdk

from nimble_studio_auto_workstation_scheduler.nimble_studio_auto_workstation_scheduler_stack import NimbleStudioAutoWorkstationSchedulerStack


app = cdk.App()

# If you don't specify 'env', this stack will be environment-agnostic.
# Account/Region-dependent features and context lookups will not work,
# but a single synthesized template can be deployed anywhere.

# Uncomment the next line to specialize this stack for the AWS Account
# and Region that are implied by the current CLI configuration.
environment = cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION'))

NimbleStudioAutoWorkstationSchedulerStack(app, "NimbleStudioAutoWorkstationSchedulerStack", env=environment)

app.synth()
