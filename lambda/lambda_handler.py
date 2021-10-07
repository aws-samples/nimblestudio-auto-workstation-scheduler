import datetime
from launcher.workstation_launcher import WorkstationLauncher
from model.time_manager import TimeManager

def handler(event, context):

    event_id = event['id']
    today = datetime.datetime.today()
    time_manager = TimeManager(today)
    target_launch_hour = time_manager.get_target_launch_hour()
    target_launch_minute = time_manager.get_target_launch_minute()
    print(f"Automated Workstation Launcher discovering sessions to launch on {time_manager.get_weekday()} {time_manager.get_date()} {target_launch_hour}:{target_launch_minute}")

    workstation_launcher = WorkstationLauncher(time_manager=time_manager, client_token_base=event_id)
    workstation_launcher.launch_workstations()

    
