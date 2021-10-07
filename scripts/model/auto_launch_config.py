from pynamodb.models import Model
from nimble_studio_auto_workstation_scheduler_stack import TABLE_NAME
from pynamodb.attributes import (
    BooleanAttribute, UnicodeAttribute
)
from model.dates_applied import DatesApplied
from utils.client_utils import get_aws_region

class AutoLaunchConfig(Model):
    class Meta:
        table_name = TABLE_NAME
        region = get_aws_region()

    uuid = UnicodeAttribute(hash_key=True)
    user_id = UnicodeAttribute(null=True)
    start_time = UnicodeAttribute(null=True)
    studio_id = UnicodeAttribute(null=True)
    launch_profile = UnicodeAttribute(null=True)
    streaming_image_id = UnicodeAttribute(null=True)
    instance_type = UnicodeAttribute(null=True)
    enabled = BooleanAttribute(default=True)
    dates_applied = DatesApplied()