#!/usr/bin/env python3
from argparse import ArgumentParser
from get_auto_launch_config import ConfigurationRetriever
from model.auto_launch_config import AutoLaunchConfig
from typing import Dict, List
from utils.prompter import Prompter

class ConfigurationDeleter():

    def __init__(
        self, 
        config_retriever : ConfigurationRetriever):
        self.config_retriever = config_retriever
        self.configs_to_delete_map = dict()

    def prompt_for_configuration_ids(self, response : str, retrieved_configs_to_delete_map : Dict) -> str:
        while True:
            if response == "quit":
                return response
            if response == "done":
                print("Configs to delete:")
                for key, value in self.configs_to_delete_map.items():
                    print(f"{key} -> {value}")
                response = Prompter.prompt_for_input("Please confirm that the configuration should be deleted.\nEnter 'yes' to confirm deletion for selected configurations. Enter any other input to quit")
                return response
            if response in retrieved_configs_to_delete_map.keys():
                self.configs_to_delete_map.update({response : retrieved_configs_to_delete_map.get(response)})
            else:
                print(f"{response} is not one of: {retrieved_configs_to_delete_map.keys()}")
            response = Prompter.prompt_for_input("Enter specific configuration IDs one at a time to select only those for deletion. Enter 'done' to finish selection. Enter 'quit' to exit")

    def confirm_delete(self, retrieved_configs_to_delete_map : Dict) -> bool:
        for key, value in retrieved_configs_to_delete_map.items():
            print(f"{key} -> {value}")
        response = None
        while True:
            if response == None:
                response = Prompter.prompt_for_input("Please confirm that the configuration should be deleted.\nEnter 'yes' to confirm deletion for all configurations shown.\nEnter specific configuration IDs one at a time to select only those for deletion.\nEnter any other input to quit")

            if response in retrieved_configs_to_delete_map.keys():
                response = self.prompt_for_configuration_ids(response=response, retrieved_configs_to_delete_map=retrieved_configs_to_delete_map)

            if response == "yes":
                # If no config entries were selectively picked, then select all retrieved entries
                if len(self.configs_to_delete_map.keys()) < 1:
                    self.configs_to_delete_map = retrieved_configs_to_delete_map
                return True
            else:
                if response != None:
                    return False

    def execute_config_deletion(self) -> None:
        failed_to_delete_configs = list()
        for key, value in self.configs_to_delete_map.items():
            try:
                item = AutoLaunchConfig(uuid=key)
                item.delete()
                print(f"Deleted config - {value}")
            except Exception as e:
                print(e)
                failed_to_delete_configs.append(value)

        if len(failed_to_delete_configs) > 0:
            print("Failed to delete the following configuration entries:")
            for config in failed_to_delete_configs:
                print(config)

    def delete_configs(self):
        configs_to_delete = self.config_retriever.get_config()
        retrieved_configs_to_delete_map = self.config_retriever.get_formatted_configs_map(configs=configs_to_delete)
        if self.confirm_delete(retrieved_configs_to_delete_map=retrieved_configs_to_delete_map):
            self.execute_config_deletion()
        else:
            print("No configuration entries deleted")

def get_script_params(cli_args=None):
    parser = ArgumentParser(description="Helper script to delete Nimble Studio Auto Workstation Scheduler config entries.")

    parser.add_argument("-u", "--user-name", dest="user_name", help="The user name of the studio user to delete configuration entries for",
                        required=False)
    parser.add_argument("-o", "--sso-id", dest="sso_id", help="The SSO ID of the user to delete configuration entries for. This takes precedence over user name",
                        required=False)
    parser.add_argument("-a", "--all-users", dest="all_users", action='store_true', help="Set flag to delete config for all users", default=False)
    parser.add_argument("-e", "--filter-enabled", dest='enabled', action='store_true', help="Delete only config that is enabled", default=False)
    parser.add_argument("-d", "--filter-disabled", dest='disabled', action='store_false', help="Delete only config that is disabled", default=False)

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
    config_deleter = ConfigurationDeleter(config_retriever=config_retriever)
    config_deleter.delete_configs()


if __name__ == "__main__":
    main()