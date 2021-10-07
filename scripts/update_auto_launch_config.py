#!/usr/bin/env python3
from argparse import ArgumentParser
from botocore.exceptions import ClientError
from typing import Dict, List
from identity.identity_helper import IdentityHelper
from model.auto_launch_config import AutoLaunchConfig
from model.dates_applied import DatesApplied
from utils.client_utils import get_nimble_client, get_aws_region
from utils.prompter import Prompter
import time
import uuid

class ConfigurationValidator():

    weekdays = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]

    def __init__(
        self, 
        user_name : str, 
        sso_id : str, 
        studio : str, 
        start_time : str, 
        days : str, 
        launch_profile : str, 
        streaming_image : str, 
        instance_type : str, 
        enabled : bool,
        skip_validation : bool):
        
        self.user_name = user_name
        self.sso_id = sso_id
        self.studio = studio
        self.start_time = start_time
        self.days = days
        self.launch_profile = launch_profile
        self.streaming_image = streaming_image
        self.instance_type = instance_type
        self.enabled = enabled
        self.skip_validation = skip_validation
        self.is_validated = False
        self.nimble_client = get_nimble_client()
        self.identity_helper = IdentityHelper()

    @staticmethod
    def is_hh_mm_time(time_string) -> bool:
        try:
            time.strptime(time_string, '%H:%M')
            return True
        except ValueError:
            Prompter.print_red("Time must be in %H:%M format")
            return False

    @staticmethod
    def check_valid_time(time) -> bool:
        time = time.strip()
        
        if not ConfigurationValidator.is_hh_mm_time(time):
            return False

        hour, min = time.split(':', 1)

        if min != "00" and min != "15" and min != "30" and min != "45":
            Prompter.print_red("Minute must be an interval of 15 minutes")
            return False
        
        return True

    def check_valid_days(self, days) -> bool:
        days = days.upper()
        days = days.replace(' ', '')
        day_list = days.split(',')
        day_set = set(day_list)
        for day in day_set:
            if day not in ConfigurationValidator.weekdays:
                Prompter.print_red(f"{day} is not one of: {ConfigurationValidator.weekdays}")
                return False
        self.days = days
        return True

    def validate_studio_id(self) -> None:
        studio_ids = list()
        studio_options_formatted = list()
        paginator = self.nimble_client.get_paginator('list_studios')
        pages = paginator.paginate()
        for page in pages:
            for studio in page['studios']:
                studio_ids.append(studio['studioId'])
                studio_options_formatted.append(f"{studio['studioName']} -> {studio['studioId']}")

        if len(studio_ids) < 1:
            raise Exception(f"No studios found in {get_aws_region()}")
        
        if self.studio == None or not (self.studio in studio_ids):
            self.studio = Prompter.prompt_for_input_from_options("Please select a studio ID", studio_options_formatted, studio_ids)

    def validate_user(self, identity_store_ids: List) -> str:
        
        while True:
            input_user_name = Prompter.prompt_for_input("Please enter the identity store user name (format: UserName@Domain)")
            user_id = self.identity_helper.search_identity_stores_for_user_name(user_name=input_user_name, identity_store_ids=identity_store_ids)
            if user_id != None:
                return user_id
            
            Prompter.print_red(f"UserName \"{input_user_name}\" not found in any of the following identity stores: {identity_store_ids}")


    def validate_sso_id(self) -> None:

        # Gather list of admin users and identityStoreIds        
        studio_member_ids = list()
        identity_store_ids = set()
        paginator = self.nimble_client.get_paginator('list_studio_members')
        pages = paginator.paginate(studioId=self.studio)
        for page in pages:
            for member in page['members']:
                studio_member_ids.append(member['principalId'])
                identity_store_ids.add(member['identityStoreId'])

        # Check if sso_id exists
        if self.sso_id != None:
            if self.sso_id in studio_member_ids:
                return
            else:
                for identity_store_id in identity_store_ids:
                    try:
                        self.identity_helper.describe_identity_user(identity_store_id=identity_store_id, user_id=self.sso_id)
                        return # validated the sso_id
                    except ClientError as e:
                        if e.response['Error']['Code'] != 'ResourceNotFoundException':
                            raise e

        # If sso_id cannot be validated, then prompt for user information and validate
        self.sso_id = self.validate_user(identity_store_ids)

    def validate_streaming_images(self, streaming_images_for_lp: List) -> None:
        if self.streaming_image in streaming_images_for_lp:
            return

        streaming_images_formatted = list()
        for image in streaming_images_for_lp:
            res = self.nimble_client.get_streaming_image(
                streamingImageId=image,
                studioId=self.studio
            )
            streaming_images_formatted.append(f"{res['streamingImage']['name']} -> {res['streamingImage']['streamingImageId']}")

        while self.streaming_image == None or not (self.streaming_image in streaming_images_for_lp):
            self.streaming_image = Prompter.prompt_for_input_from_options("Please select a streaming image component ID", streaming_images_formatted, streaming_images_for_lp)

    def validate_ec2_instance_type(self, instance_types: List) -> None:
        while self.instance_type == None or not (self.instance_type in instance_types):
            self.instance_type = Prompter.prompt_for_input_from_options("Please select a streaming instance type", instance_types, instance_types)

    def validate_launch_profile(self) -> None:
        launch_profiles = list()
        launch_profile_ids = list()
        launch_profile_options_formatted = list()
        paginator = self.nimble_client.get_paginator('list_launch_profiles')
        pages = paginator.paginate(
            studioId=self.studio,
            principalId=self.sso_id
            )
        for page in pages:
            for lp in page['launchProfiles']:
                launch_profiles.append(lp)
                launch_profile_ids.append(lp['launchProfileId'])
                launch_profile_options_formatted.append(f"{lp['name']} -> {lp['launchProfileId']}")

        if len(launch_profile_ids) < 1:
            raise Exception(f"User {self.sso_id} does not have access to any launch profiles")

        if self.launch_profile == None or not (self.launch_profile in launch_profile_ids):
            self.launch_profile = Prompter.prompt_for_input_from_options("Please select a launch profile", launch_profile_options_formatted, launch_profile_ids)

        streaming_image_ids = launch_profiles[launch_profile_ids.index(self.launch_profile)]['streamConfiguration']['streamingImageIds']
        self.validate_streaming_images(streaming_image_ids)

        ec2_instance_types = launch_profiles[launch_profile_ids.index(self.launch_profile)]['streamConfiguration']['ec2InstanceTypes']
        self.validate_ec2_instance_type(ec2_instance_types)

    def validate_start_time(self) -> None:
        time = self.start_time
        while time == None or not ConfigurationValidator.check_valid_time(time):
            time = Prompter.prompt_for_input("Enter a workstation UTC start time in format HH:MM")
        self.start_time = time.replace(':', '')

    def validate_days(self) -> None:
        days = self.days
        while days == None or not self.check_valid_days(days):
            days = Prompter.prompt_for_input("Enter a comma delimited list of weekdays to launch the workstation (ex: Monday,Tuesday)")
        self.days = days.upper()
        self.days = self.days.replace(' ', '')

    def validate_all_update_params_exist(self) -> None:
        missing_params = False
        missing_param_message = "Missing required parameters for update:"
        if self.sso_id == None:
            missing_param_message += "\nUser SSO ID"
            missing_params = True
        if self.studio == None:
            missing_param_message += "\nStudio ID"
            missing_params = True
        if self.start_time == None:
            missing_param_message += "\nStart time"
            missing_params = True
        if self.days == None:
            missing_param_message += "\nDays"
            missing_params = True
        if self.launch_profile == None:
            missing_param_message += "\nLaunch profile ID"
            missing_params = True
        if self.streaming_image == None:
            missing_param_message += "\nStreaming image ID"
            missing_params = True
        if self.instance_type == None:
            missing_param_message += "\nEC2 instance type"
            missing_params = True
        if missing_params:
            raise Exception(missing_param_message)


    def validate_configuration(self) -> None:
        self.validate_start_time()
        self.validate_days()

        # Optionally skip validation requiring service calls
        if not self.skip_validation:
            self.validate_studio_id()
            self.validate_sso_id()
            self.validate_launch_profile()

        self.validate_all_update_params_exist()
        self.is_validated = True

class ConfigurationUpdater():

    def __init__(self, configuration_validator : ConfigurationValidator):
        self.auto_launch_config : AutoLaunchConfig = self.generate_config_to_update(configuration_validator)
        self.should_update_config = True

    @staticmethod
    def generate_key() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def generate_config_to_update(configuration_validator : ConfigurationValidator) -> AutoLaunchConfig:
        if configuration_validator.is_validated == False:
            configuration_validator.validate_configuration()
        
        days = configuration_validator.days.split(',')
        auto_launch_config : AutoLaunchConfig = AutoLaunchConfig(
            ConfigurationUpdater.generate_key(),
            user_id=configuration_validator.sso_id,
            start_time=configuration_validator.start_time,
            studio_id=configuration_validator.studio,
            launch_profile=configuration_validator.launch_profile,
            streaming_image_id=configuration_validator.streaming_image,
            instance_type=configuration_validator.instance_type,
            enabled=configuration_validator.enabled,
            dates_applied=DatesApplied(days=days)
        )
        return auto_launch_config

    @staticmethod
    def prompt_if_should_override_config(map_config_to_overlapping_days : Dict[AutoLaunchConfig, set]) -> bool:
        prompt = "This update will override the following existing config: \n"
        config : AutoLaunchConfig = None
        for config in map_config_to_overlapping_days.keys():
            prompt += f"Start time: {config.start_time}, Launch Profile: {config.launch_profile} for days: {map_config_to_overlapping_days.get(config)}\n"

        prompt += "Should the config be overriden? (y or n)"
        res = Prompter.prompt_for_input(prompt)
        res = Prompter.wait_for_y_n_response(res)
        if Prompter.check_if_response_is_y(res):
            return True
        return False

    def get_current_user_config(self) -> List[AutoLaunchConfig]:
        return list(AutoLaunchConfig.scan(AutoLaunchConfig.user_id == self.auto_launch_config.user_id))

    def override_existing_config(self, map_config_to_overlapping_days : Dict[AutoLaunchConfig, set]):
        config : AutoLaunchConfig
        for config in map_config_to_overlapping_days.keys():
            days = config.dates_applied.days
            overlapping_days = map_config_to_overlapping_days.get(config)
            maintain_days = set()
            for day in days:
                day_string = str(day)
                if day_string not in overlapping_days:
                    maintain_days.add(day)
            if len(maintain_days) < 1:
                config.enabled = False
            config.dates_applied.days = maintain_days
            config.save()

    def handle_existing_config_updates(self) -> None:
        days_to_update : List = self.auto_launch_config.dates_applied.days
        map_config_to_overlapping_days = {}
        existing_config : List[AutoLaunchConfig] = self.get_current_user_config()
        for config in existing_config:
            for day in config.dates_applied.days:
                if day in days_to_update:
                    if config in map_config_to_overlapping_days:
                        days : set(str) = map_config_to_overlapping_days.get(config)
                        days.add(day)
                        map_config_to_overlapping_days[config] = days
                    else:
                        days : set = {day}
                        map_config_to_overlapping_days[config] = days

        if any(map_config_to_overlapping_days):
            should_override = self.prompt_if_should_override_config(map_config_to_overlapping_days)
            if should_override:
                self.override_existing_config(map_config_to_overlapping_days)
            else:
                self.should_update_config = False

    def get_current_configs_matching_time(self) -> List[AutoLaunchConfig] or None:
        configs : List[AutoLaunchConfig] = list()
        for config in AutoLaunchConfig.scan((AutoLaunchConfig.user_id == self.auto_launch_config.user_id) & (AutoLaunchConfig.start_time == self.auto_launch_config.start_time)):
            configs.append(config)
        if len(configs) > 0:
            return configs
        return None

    def perform_config_update(self) -> None:
        self.handle_existing_config_updates()
        if self.should_update_config:
            existing_configs_matching_start_time : AutoLaunchConfig = self.get_current_configs_matching_time()
            if existing_configs_matching_start_time != None:
                for config in existing_configs_matching_start_time:
                    if (config.launch_profile == self.auto_launch_config.launch_profile and 
                        config.streaming_image_id == self.auto_launch_config.streaming_image_id and 
                        config.instance_type == self.auto_launch_config.instance_type and 
                        config.studio_id == self.auto_launch_config.studio_id):

                        self.auto_launch_config.uuid = config.uuid
                        self.auto_launch_config.dates_applied.days = self.auto_launch_config.dates_applied.days + list(set(config.dates_applied.days) - set(self.auto_launch_config.dates_applied.days))
            self.auto_launch_config.save()
            print("Configuration has been updated.")
        else:
            print("No config will be updated at this time.")



def get_script_params(cli_args=None):
    parser = ArgumentParser(description="Helper script to update Nimble Studio Auto Workstation Scheduler config for a studio user at a certain start time.")

    parser.add_argument("-u", "--user-name", dest="user_name", help="The user name of the studio user to update configuration for",
                        required=False)
    parser.add_argument("-o", "--sso-id", dest="sso_id", help="The SSO ID of the user to update configuration for. This takes precedence over user name",
                        required=False)
    parser.add_argument("-s", "--studio-id", dest="studio_id", help="The studio ID to set configuration for",
                        required=False)
    parser.add_argument("-t", "--start-time", dest="start_time", help="The time (UTC) to start the launch of the workstation formatted as HH:MM",
                        required=False)
    parser.add_argument("-d", "--days", dest="days", help="The weekdays to launch the workstation at this time, comma delimited (ex: Monday,Tuesday)",
                        required=False)
    parser.add_argument("-l", "--launch-profile", dest="launch_profile", help="The ID of the launch profile to launch for the workstation",
                        required=False)
    parser.add_argument("-i", "--streaming-image", dest="streaming_image", help="The streaming image component ID to use for the launch profile",
                        required=False)
    parser.add_argument("-n", "--instance-type", dest="instance_type", help="The instance type and size to use for the workstation (ex: g4dn.2xlarge)",
                        required=False)
    parser.add_argument("-e", "--enable", dest='enabled', action='store_true', help="Enable auto launch for this config")
    parser.add_argument("-D", "--disable", dest='enabled', action='store_false', help="Disable auto launch for this config")
    parser.set_defaults(enabled=True)
    parser.add_argument("-x", "--skip-validation", dest="skip_validation", action='store_true', help="Skip input validation and prompts")
    parser.set_defaults(skip_validation=False)

    if not cli_args:
        return parser.parse_args()
    else:
        return parser.parse_args(cli_args.split())

def main(cli_args=None):
    script_args = get_script_params(cli_args)
    config_validator = ConfigurationValidator(
        user_name=script_args.user_name,
        sso_id=script_args.sso_id,
        studio=script_args.studio_id, 
        start_time=script_args.start_time, 
        days=script_args.days,
        launch_profile=script_args.launch_profile,
        streaming_image=script_args.streaming_image,
        instance_type=script_args.instance_type,
        enabled=script_args.enabled,
        skip_validation=script_args.skip_validation)

    config_validator.validate_configuration()
    config_updater = ConfigurationUpdater(config_validator)
    config_updater.perform_config_update()


if __name__ == "__main__":
    main()