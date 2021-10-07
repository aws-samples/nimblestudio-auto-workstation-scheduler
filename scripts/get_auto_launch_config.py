#!/usr/bin/env python3
from argparse import ArgumentParser
from botocore.exceptions import ClientError
from identity.identity_helper import IdentityHelper
from model.auto_launch_config import AutoLaunchConfig
from typing import Dict, List
from utils.prompter import Prompter
from utils.client_utils import get_nimble_client

class ConfigurationRetriever():

    def __init__(
        self, 
        user_name : str or None, 
        sso_id : str or None, 
        retrieve_all_users : bool, 
        filter_enabled : bool, 
        filter_disabled : bool):

        self.user_name = user_name
        self.sso_id = sso_id
        self.retrieve_all_users = retrieve_all_users
        self.filter_enabled = filter_enabled
        self.filter_disabled = filter_disabled
        self.identity_helper = IdentityHelper()
        self.nimble_client = get_nimble_client()
        self.studios = dict()
        self.launch_profiles = dict()
        self.identity_store_ids = None
        self.studio_ids = None
        self.streaming_images = dict()
        self.users = dict()

    def get_studio_details(self, studio_id : str):
        if self.studios.get(studio_id) != None:
            return self.studios.get(studio_id)

        try:
            studio = self.nimble_client.get_studio(
                studioId=studio_id
            )
            self.studios.update({studio_id : studio['studio']})
            return studio['studio']
        except Exception:
            return None

    def get_launch_profile_details(self, studio_id : str, launch_profile_id : str):
        if self.launch_profiles.get(launch_profile_id) != None:
            return self.launch_profiles.get(launch_profile_id)

        try:
            launch_profile = self.nimble_client.get_launch_profile(
                launchProfileId=launch_profile_id,
                studioId=studio_id
            )
            self.launch_profiles.update({launch_profile_id : launch_profile['launchProfile']})
            return launch_profile['launchProfile']
        except Exception:
            return None

    def get_streaming_image_details(self, studio_id : str, streaming_image_id : str):
        if self.streaming_images.get(streaming_image_id) != None:
            return self.streaming_images.get(streaming_image_id)

        try:
            streaming_image = self.nimble_client.get_streaming_image(
                streamingImageId=streaming_image_id,
                studioId=studio_id
            )
            self.streaming_images.update({streaming_image_id : streaming_image['streamingImage']})
            return streaming_image['streamingImage']
        except Exception:
            return None

    def get_user_details(self, user_id : str):
        if self.users.get(user_id) != None:
            return self.users.get(user_id)

        for identity_store_id in self.get_identity_store_ids(self.get_studio_ids()):
            try:
                user = self.identity_helper.describe_identity_user(
                    identity_store_id=identity_store_id,
                    user_id=user_id
                )
                self.users.update({user_id : user})
                return user
            except ClientError as e:
                if e.response['Error']['Code'] != 'ResourceNotFoundException':
                    return None
            except Exception:
                return None
        return None

    def format_studio_output(self, studio_id : str,) -> str:
        studio = self.get_studio_details(studio_id=studio_id)
        if studio == None:
            return studio_id
        return f"{studio['studioName']} ({studio_id})"

    def format_launch_profile_output(self, studio_id : str, launch_profile_id : str) -> str:
        launch_profile = self.get_launch_profile_details(studio_id=studio_id, launch_profile_id=launch_profile_id)
        if launch_profile == None:
            return launch_profile_id
        return f"{launch_profile['name']} ({launch_profile_id})"

    def format_streaming_image_output(self, studio_id : str, streaming_image_id : str) -> str:
        streaming_image = self.get_streaming_image_details(studio_id=studio_id, streaming_image_id=streaming_image_id)
        if streaming_image == None:
            return streaming_image_id
        return f"{streaming_image['name']} ({streaming_image_id})"

    def format_user_output(self, user_id : str) -> str:
        user = self.get_user_details(user_id=user_id)
        if user == None:
            return user_id
        return f"{user['UserName']} ({user_id})"

    def format_config_output(self, config : AutoLaunchConfig) -> str:
        user_output = self.format_user_output(user_id=config.user_id)
        studio_output = self.format_studio_output(studio_id=config.studio_id)
        launch_profile_output = self.format_launch_profile_output(studio_id=config.studio_id, launch_profile_id=config.launch_profile)
        streaming_image_output = self.format_streaming_image_output(studio_id=config.studio_id, streaming_image_id=config.streaming_image_id)
        return f"User: {user_output}, Start time: {config.start_time} UTC, Days: {config.dates_applied.days}, Studio: {studio_output}, Launch Profile: {launch_profile_output}, Streaming Image: {streaming_image_output}, Instance: {config.instance_type}, Enabled: {config.enabled}"

    def get_formatted_configs_map(self, configs : List[AutoLaunchConfig]) -> Dict:
        formatted_configs = dict()
        for config in configs:
            formatted_configs.update({str(config.uuid) : self.format_config_output(config=config)})
        return formatted_configs

    def output_configs(self, configs : List[AutoLaunchConfig]) -> None:
        if len(configs) < 1:
            print(f"No configs found")
            return

        formatted_configs = self.get_formatted_configs_map(configs=configs)

        print(f"{len(formatted_configs.values())} Configs:")
        for config in formatted_configs.values():
            print(config)

    def get_studio_ids(self) -> List[str]:
        if self.studio_ids == None:
            self.studio_ids = list()
            paginator = self.nimble_client.get_paginator('list_studios')
            pages = paginator.paginate()
            for page in pages:
                for studio in page['studios']:
                    self.studio_ids.append(studio['studioId'])
                    self.studios.update({studio['studioId'] : studio})
        return self.studio_ids

    def get_identity_store_ids_from_studio(self, studio_id : str) -> List[str]:
        identity_store_ids = set()
        paginator = self.nimble_client.get_paginator('list_studio_members')
        pages = paginator.paginate(studioId=studio_id)
        for page in pages:
            for member in page['members']:
                identity_store_ids.add(member['identityStoreId'])
        return list(identity_store_ids)

    def get_identity_store_ids(self, studio_ids : List) -> List:
        if self.identity_store_ids == None:
            self.identity_store_ids = list()
            for studio_id in studio_ids:
                self.identity_store_ids = self.identity_store_ids + list(set(self.get_identity_store_ids_from_studio(studio_id=studio_id)) - set(self.identity_store_ids))
        return self.identity_store_ids

    def get_user_id_from_user_name(self) -> str or None:

        studio_ids = self.get_studio_ids()
        identity_store_ids = self.get_identity_store_ids(studio_ids=studio_ids)

        while True:
            if self.user_name == None:
                self.user_name = Prompter.prompt_for_input("Please enter the identity store user name (format: UserName@Domain). Or enter 'all' to retrieve config for all users")

            if self.user_name == "all":
                return None

            user_id = self.identity_helper.search_identity_stores_for_user_name(user_name=self.user_name, identity_store_ids=identity_store_ids)
            if user_id != None:
                return user_id
            
            Prompter.print_red(f"UserName \"{self.user_name}\" not found in any of the following identity stores: {identity_store_ids}")
            self.user_name = None

    def get_config(self) -> List[AutoLaunchConfig]:
        # scan_condition makes use of pynamodb's condition expressions
        # https://pynamodb.readthedocs.io/en/latest/conditional.html#condition-expressions
        scan_condition = None
        if self.retrieve_all_users != True:
            if self.sso_id == None:
                self.sso_id = self.get_user_id_from_user_name()
                if self.sso_id != None:
                    scan_condition = (AutoLaunchConfig.user_id == self.sso_id)
            else:
                scan_condition = (AutoLaunchConfig.user_id == self.sso_id)
        if self.filter_enabled:
            if not self.filter_disabled:
                scan_condition = scan_condition & (AutoLaunchConfig.enabled == True)
        else:
            if self.filter_disabled:
                scan_condition = scan_condition & (AutoLaunchConfig.enabled == False)

        configs = None
        if scan_condition != None:
            configs = list(AutoLaunchConfig.scan(scan_condition))
        else:
            configs = list(AutoLaunchConfig.scan())
        return configs

    def retrieve_config(self) -> None:
        configs = self.get_config()
        self.output_configs(configs=configs)

def get_script_params(cli_args=None):
    parser = ArgumentParser(description="Helper script to get Nimble Studio Auto Workstation Scheduler config entries.")

    parser.add_argument("-u", "--user-name", dest="user_name", help="The user name of the studio user to get configuration for",
                        required=False)
    parser.add_argument("-o", "--sso-id", dest="sso_id", help="The SSO ID of the user to get configuration for. This takes precedence over user name",
                        required=False)
    parser.add_argument("-a", "--all-users", dest="all_users", action='store_true', help="Set flag to retrieve config for all users", default=False)
    parser.add_argument("-e", "--filter-enabled", dest='enabled', action='store_true', help="Retrieve only config that is enabled", default=False)
    parser.add_argument("-d", "--filter-disabled", dest='disabled', action='store_false', help="Retrieve only config that is disabled", default=False)

    if not cli_args:
        return parser.parse_args()
    else:
        return parser.parse_args(cli_args.split())

def main(cli_args=None):
    script_args = get_script_params(cli_args)
    config_retriever = ConfigurationRetriever(
        user_name=script_args.user_name, 
        sso_id=script_args.sso_id, 
        retrieve_all_users=script_args.all_users, 
        filter_enabled=script_args.enabled, 
        filter_disabled=script_args.disabled)
    config_retriever.retrieve_config()


if __name__ == "__main__":
    main()