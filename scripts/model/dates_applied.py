from pynamodb.attributes import (
    DynamicMapAttribute, ListAttribute, UnicodeAttribute
)

class DatesApplied(DynamicMapAttribute):
    days = ListAttribute(of=UnicodeAttribute)