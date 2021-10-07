from pynamodb.models import Model
from pynamodb.attributes import (
    BooleanAttribute, UnicodeAttribute
)
from common.config import AWS_REGION, NIMBLE_STUDIO_AUTO_WORKSTATION_SCHEDULER_CONFIG_TABLE_NAME
from model.data.dates_applied import DatesApplied

"""
    Configuration data for a desired automated session launch at a certain time and date/day
"""
class AutoLaunchConfig(Model):
    class Meta:
        table_name = NIMBLE_STUDIO_AUTO_WORKSTATION_SCHEDULER_CONFIG_TABLE_NAME
        region = AWS_REGION

    uuid = UnicodeAttribute(hash_key=True)
    user_id = UnicodeAttribute(null=True)
    start_time = UnicodeAttribute(null=True)
    studio_id = UnicodeAttribute(null=True)
    launch_profile = UnicodeAttribute(null=True)
    streaming_image_id = UnicodeAttribute(null=True)
    instance_type = UnicodeAttribute(null=True)
    enabled = BooleanAttribute(default=True)
    dates_applied = DatesApplied()

