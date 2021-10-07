from pynamodb.attributes import ListAttribute, DynamicMapAttribute, UnicodeAttribute

class DatesApplied(DynamicMapAttribute):
    days = ListAttribute(of=UnicodeAttribute)