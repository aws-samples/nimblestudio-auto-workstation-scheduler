from aws_cdk import core as cdk
from aws_cdk import aws_events_targets as targets
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_events as events
from aws_cdk import aws_dynamodb as dynamo
from local_bundler import LocalBundler, get_lambda_code_dir

TABLE_NAME = "nimble_studio_auto_workstation_scheduler_config"

class NimbleStudioAutoWorkstationSchedulerStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Dynamo table to store Nimble Studio user configuration for automated workstation launch
        config_table = dynamo.Table(
            self, TABLE_NAME,
            partition_key=dynamo.Attribute(
                name="uuid",
                type=dynamo.AttributeType.STRING
            ),
            billing_mode=dynamo.BillingMode.PAY_PER_REQUEST,
            table_name=TABLE_NAME,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

        lambdaRole = iam.Role(
            self,
            "WorkstationSchedulerFunctionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonNimbleStudio-StudioUser")
            ],
            role_name="NimbleAutoSchedulerRole"
        )

        lambdaFn = lambda_.Function(
            self,
            "WorkstationSchedulerFunction",
            code=lambda_.Code.from_asset(get_lambda_code_dir(),
                bundling=cdk.BundlingOptions(
                    image=lambda_.Runtime.PYTHON_3_7.bundling_image,
                    command=["bash", "-c", "pip install -r requirements.txt -t /asset-output && cp -au . /asset-output"],
                    local=LocalBundler()
                )
            ),
            handler="lambda_handler.handler",
            timeout=cdk.Duration.seconds(600),
            runtime=lambda_.Runtime.PYTHON_3_7,
            role=lambdaRole,
            function_name="NimbleAutoScheduler"
        )

        lambdaFn.add_environment("TABLE_NAME", config_table.table_name)

        # Grant lambda permission to read from table
        config_table.grant_read_data(lambdaFn)

        # Grant lambda permission to Nimble
        # https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonnimblestudio.html#amazonnimblestudio-actions-as-permissions
        nimble_policy_statement = iam.PolicyStatement(
            resources=["*"],
            actions=[
                "nimble:GetLaunchProfile",
                "nimble:GetLaunchProfileInitialization",
                "nimble:CreateStreamingSession",
                "nimble:ListStreamingSessions",
                "nimble:TagResource"
            ],
            effect=iam.Effect.ALLOW
        )

        lambdaFn.add_to_role_policy(nimble_policy_statement)

        # Grant lambda additional permissions for resources needed by Nimble
        # https://docs.aws.amazon.com/nimble-studio/latest/userguide/security-iam-awsmanpol.html#AmazonNimble-StudioUser
        nimble_additional_service_permissions_policy_statement = iam.PolicyStatement(
            resources=["*"],
            actions=[
                # Key permissions are needed if launching workstations with encrypted streaming images
                # https://docs.aws.amazon.com/nimble-studio/latest/userguide/update-win-workstation-ami.html#update-win-workstation-ami-step-8
                "kms:CreateKey",
                "kms:ListKeys",
                "kms:ListAliases",
                "kms:Encrypt",
                "kms:Decrypt"
            ],
            effect=iam.Effect.ALLOW
        )

        lambdaFn.add_to_role_policy(nimble_additional_service_permissions_policy_statement)

        # Run on weekdays every 15 minutes
        # See https://docs.aws.amazon.com/lambda/latest/dg/tutorial-scheduled-events-schedule-expressions.html
        rule = events.Rule(
            self,
            "Rule",
            schedule=events.Schedule.cron(minute="0/15", hour="*", month="*", week_day="MON-FRI", year="*"),
            description="Scheduled event to trigger the Automated Workstation Scheduler lambda"
        )

        rule.add_target(targets.LambdaFunction(lambdaFn))
