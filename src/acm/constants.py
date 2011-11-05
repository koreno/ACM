
class Enum(object):
    class __metaclass__(type):
        def __new__(cls, name, bases, dict):
            # convert the enum values to the lower-case form of the string (only if not string already)
            dict.update({k:k.lower() for k,v in dict.iteritems() if isinstance(v,int)})
            # update the 'all' attribute to contain all other values
            dict['all'] = dict.values()
            return type.__new__(cls, name, bases, dict)
    all = ()

class BID_ACTION(Enum):
    (
    PLACED_SUPPORTING,
    PLACED_OPPOSING,
    WITHDRAWN_SUPPORTING,
    WITHDRAWN_OPPOSING,
    ) = xrange(4)

class SYSTEM_TYPE(Enum):
    (
    SYSTEM_FACEBOOK,
    SYSTEM_GOOGLE,
    SYSTEM_TWEETER,
    SYSTEM_ACM,
    ) = xrange(4)

class PAPER_STATUS(Enum):
    (
    DRAFT,
    DEBATE,
    REFERENDUM,
    ACCEPTED,
    REJECTED,
    DROPPED,
    ) = xrange(6)
    
