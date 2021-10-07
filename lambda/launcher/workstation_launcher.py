import boto3
import hashlib
import uuid
from typing import List, Set
from common.config import AWS_REGION
from model.time_manager import TimeManager
from model.auto_launch_config import AutoLaunchConfig
from model.data.weekdays import Weekdays

"""
    Handles discovery of desired sessions to launch and initiates the launches
"""
class WorkstationLauncher():

    def __init__(self, time_manager: TimeManager, client_token_base: str):
        self.nimble_client = boto3.client('nimble', region_name=AWS_REGION)
        self.time_manager = time_manager
        self.client_token_base = client_token_base

    @staticmethod
    def get_configs_set_to_lauch_at_time(target_launch_time) -> List[AutoLaunchConfig]:
        return list(AutoLaunchConfig.scan(AutoLaunchConfig.start_time == target_launch_time))

    @staticmethod
    def filter_out_disabled_launch_configs(configs: List[AutoLaunchConfig]) -> List[AutoLaunchConfig]:
        return [x for x in configs if x.enabled == True]

    @staticmethod
    def filter_launch_configs_that_match_day(weekday: Weekdays, configs: List[AutoLaunchConfig]) -> List[AutoLaunchConfig]:
        return [x for x in configs if str(weekday) in x.dates_applied.days]

    @staticmethod
    def filter_out_users_with_active_sessions_from_launch_configs(users: List[str], configs: List[AutoLaunchConfig]) -> List[AutoLaunchConfig]:
        return [x for x in configs if not x.user_id in users]

    @staticmethod
    def get_studio_ids_from_launch_configs(configs: List[AutoLaunchConfig]) -> Set:
        studio_ids = set()
        for config in configs:
            studio_ids.add(config.studio_id)
        return studio_ids

    def get_users_with_active_streaming_sessions(self, configs : List[AutoLaunchConfig]) -> List[str]:
        users_with_active_streaming_sessions : List[str] = list()
        paginator = self.nimble_client.get_paginator('list_streaming_sessions')

        studio_ids = WorkstationLauncher.get_studio_ids_from_launch_configs(configs)

        for studio_id in studio_ids:
            page_iterator = paginator.paginate(studioId=studio_id)
            for page in page_iterator:
                for session in page['sessions']:
                    if (session['state'] == 'CREATE_IN_PROGRESS' or session['state'] == 'READY'):
                        users_with_active_streaming_sessions.append(session['ownedBy'])

        return users_with_active_streaming_sessions

    def get_all_configs_to_launch(self) -> List[AutoLaunchConfig]:
        launch_time = self.time_manager.get_target_launch_time()
        weekday = self.time_manager.get_weekday()
        configs = WorkstationLauncher.get_configs_set_to_lauch_at_time(launch_time)
        configs = WorkstationLauncher.filter_out_disabled_launch_configs(configs)
        configs = WorkstationLauncher.filter_launch_configs_that_match_day(weekday, configs)

        if len(configs) == 0:
            return configs

        users_with_active_streaming_sessions = self.get_users_with_active_streaming_sessions(configs)
        return WorkstationLauncher.filter_out_users_with_active_sessions_from_launch_configs(users_with_active_streaming_sessions, configs)

    def generate_client_token_for_create_session(self, owned_by : str) -> str:
        hash_string = self.client_token_base + self.time_manager.get_target_launch_time() + owned_by
        hash = hashlib.md5(hash_string.encode('utf-8'))
        return str(uuid.UUID(hash.hexdigest()))

    def launch_workstations(self) -> None:
        configs = self.get_all_configs_to_launch()

        if len(configs) == 0:
            print("No workstations to launch at this time")
            return

        for config in configs:
            try:
                response = self.nimble_client.create_streaming_session(
                    clientToken=self.generate_client_token_for_create_session(config.user_id),
                    ec2InstanceType=config.instance_type,
                    launchProfileId=config.launch_profile,
                    ownedBy=config.user_id,
                    streamingImageId=config.streaming_image_id,
                    studioId=config.studio_id,
                    tags={
                        'NimbleStudioAutoWorkstationSchedulerLaunched': 'true',
                        'WorkstationOwnedBy': config.user_id,
                        'WorkstationTargetLaunchTimeUTC': self.time_manager.get_target_launch_time()
                    }
                )
                print(f"Launched session for user {config.user_id} with session ID {response['session']['sessionId']}")
            except Exception as e:
                print(f"Error launching session for user {config.user_id}: {e}")
