#!/usr/bin/env python3
from argparse import ArgumentParser
from enum import Enum
from nimble_studio_auto_workstation_scheduler_stack import RULE_NAME
from utils.client_utils import get_cloudwatch_event_client

class AutoLauncherToggler():

    class State(Enum):
        DISABLED = 0
        ENABLED = 1

    def __init__(self, should_enable : bool):
        self.desired_state = self.State(should_enable)
        self.events_client = get_cloudwatch_event_client()

    def get_auto_launcher_event_state(self) -> State:
        response = self.events_client.describe_rule(
            Name=RULE_NAME
        )
        if response['State'] == 'ENABLED':
            return self.State.ENABLED
        else:
            return self.State.DISABLED

    def update_auto_launcher_state(self) -> State:
        if self.desired_state == self.State.ENABLED:
            self.events_client.enable_rule(
                Name=RULE_NAME
            )
            return self.State.ENABLED
        else:
            self.events_client.disable_rule(
                Name=RULE_NAME
            )
            return self.State.DISABLED

    def toggle_auto_launcher(self):
        launcher_state = self.get_auto_launcher_event_state()
        if launcher_state != self.desired_state:
            launcher_state = self.update_auto_launcher_state()
        print(f"Nimble Studio Auto Workstation Launcher is {launcher_state.name}")
        

def get_script_params(cli_args=None):
    parser = ArgumentParser(description="Helper script to toggle the Nimble Studio Auto Workstation Scheduler on or off.")

    parser.add_argument("-e", "--enable", dest='should_enable', action='store_true', help="Enable auto launch for this config")
    parser.add_argument("-d", "--disable", dest='should_enable', action='store_false', help="Disable auto launch for this config")
    parser.set_defaults(should_enable=True)

    if not cli_args:
        return parser.parse_args()
    else:
        return parser.parse_args(cli_args.split())

def main(cli_args=None):
    script_args = get_script_params(cli_args)
    auto_launch_toggler = AutoLauncherToggler(script_args.should_enable)
    auto_launch_toggler.toggle_auto_launcher()


if __name__ == "__main__":
    main()