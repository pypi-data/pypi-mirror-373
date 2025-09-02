from enum import Enum


class CarRelationTypeEnum(str, Enum):
    OWNER = "owner"
    DRIVER = "driver"
    BUYER = "buyer"
    CLIENT = "client"
