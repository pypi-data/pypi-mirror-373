from enum import IntFlag

class MemberFilter(IntFlag):
    MODULES = 1
    CLASSES = 2
    FUNCTIONS_AND_METHODS = 4
    PROPERTIES = 8
    FIELDS_AND_VARIABLES = 16
    DELEGATES = 32
    PROTECTED = 64
    PRIVATE = 192 # private 128 + protected 64 = 192
    SPECIAL = 256
    DEFAULT = 511
