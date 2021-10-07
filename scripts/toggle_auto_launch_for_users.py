#!/usr/bin/env python3
from argparse import ArgumentParser
from typing import List
from model.auto_launch_config import AutoLaunchConfig
from utils.prompter import Prompter

class AutoLaunchConfigToggler():

    def __init__(self, enabled : bool, studio : str, users : List[str]):
        self.enabled = enabled
        self.studio = studio
        if users == None:
            self.users = list()
        else:
            self.users = users
    
    @staticmethod
    def get_auto_launch_configuration(studio_id : str) -> List[AutoLaunchConfig]:
        if studio_id:
            return list(AutoLaunchConfig.scan(studio_id=studio_id))
        return list(AutoLaunchConfig.scan())

    @staticmethod
    def update_auto_launch_config_enabled_status(enabled : bool, config : AutoLaunchConfig) -> None:

        if config.enabled != enabled:
            config.enabled = enabled
            config.save()
            print(f"Updated user {config.user_id} auto launch config entry for {config.start_time} UTC - enabled: {enabled}")

    def check_whether_to_update_all_users(self) -> bool:
        if len(self.users) > 0:
            return False
        else:
            specify_studio = "" if (self.studio == None) else f" in studio {self.studio}"
            response = Prompter.prompt_for_input(f"This operation will set auto launch config for all users{specify_studio} to enabled: {self.enabled}. Proceed? ('y' or 'n')")
            response = Prompter.wait_for_y_n_response(response)
            return Prompter.check_if_response_is_y(response)

    def toggle_user_auto_launch_config(self) -> None:

        should_update_all_users = self.check_whether_to_update_all_users()

        if (not should_update_all_users) and (len(self.users) < 1):
            print("No config to update.")
            return

        configs : List[AutoLaunchConfig] = self.get_auto_launch_configuration(studio_id=self.studio)
        for config in configs:
            if should_update_all_users or (config.user_id in self.users):
                self.update_auto_launch_config_enabled_status(self.enabled, config)


def get_script_params(cli_args=None):
    parser = ArgumentParser()

    parser.add_argument("-u", "--user-ids", dest="users", help="Comma delimited list of studio user IDs to update configuration for",
                        required=False)
    parser.add_argument("-s", "--studio", dest="studio", help="The studio ID to set configuration for",
                        required=False)
    parser.add_argument("-e", "--enable", dest='enabled', action='store_true')
    parser.add_argument("-d", "--disable", dest='enabled', action='store_false')
    parser.set_defaults(enabled=True)

    if not cli_args:
        return parser.parse_args()
    else:
        return parser.parse_args(cli_args.split())

def get_users_list_from_input(input_users : str) -> List[str] or None:
    if input_users == None:
        return None
    user_list = input_users.strip()
    return user_list.split(',')

def main(cli_args=None):
    script_args = get_script_params(cli_args)
    user_list = get_users_list_from_input(script_args.users)
    auto_launch_config_toggler = AutoLaunchConfigToggler(enabled=script_args.enabled, studio=script_args.studio, users=user_list)
    auto_launch_config_toggler.toggle_user_auto_launch_config()


if __name__ == "__main__":
    main()