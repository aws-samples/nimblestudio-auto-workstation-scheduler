import datetime
from model.data.weekdays import Weekdays

class TimeManager():

    def __init__(self, today: datetime):
        self.today = today

    @staticmethod
    def format_num_with_leading_zero(num) -> str:
        return f"{num:02d}"

    def get_target_launch_hour(self) -> str:
        minute = self.today.minute
        hour = self.today.hour

        # Round up to nearest 15min interval
        if minute > 52:
            hour = hour + 1
        return TimeManager.format_num_with_leading_zero(hour)

    def get_target_launch_minute(self) -> str:
        minute = self.today.minute
        if minute <= 7 or minute > 52:
            minute = "00"
        elif (minute in range(8, 23)):
            minute = "15"
        elif (minute in range(23, 38)):
            minute = "30"
        else:
            minute = "45"
        return minute

    """
    Handles offset of lambda invocation time and desired launch time in intervals of 15min
    """
    def get_target_launch_time(self) -> str:
        return self.get_target_launch_hour() + self.get_target_launch_minute()

    def get_weekday(self) -> Weekdays:
        return Weekdays.get_weekday_from_int(self.today.weekday())

    def get_date(self) -> str:
        return self.today.strftime("%m/%d/%Y")