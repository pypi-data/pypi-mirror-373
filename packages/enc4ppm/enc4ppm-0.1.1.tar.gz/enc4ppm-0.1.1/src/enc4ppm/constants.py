from enum import Enum

class LabelingType(Enum):
    NEXT_ACTIVITY = 'next_activity'
    REMAINING_TIME = 'remaining_time'
    OUTCOME = 'outcome'
    CUSTOM = 'custom'


class CategoricalEncoding(Enum):
    STRING = 'string'
    ONE_HOT = 'one_hot'


class PrefixStrategy(Enum):
    UP_TO_SPECIFIED = 'up_to_specified'
    ONLY_SPECIFIED = 'only_specified'