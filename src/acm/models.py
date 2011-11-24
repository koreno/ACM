import sys
import inspect


import google.appengine.ext.db as db
from google.appengine.ext.db import Model
from google.appengine.ext.db.polymodel import PolyModel

import acm.constants as constants




class System(Model):
    name = db.CategoryProperty(choices=(constants.SYSTEM_TYPE.all))



class Authentication(Model):

    PARENT = "System"

    # the screen name of the user
    user_id = db.StringProperty()



class Region(Model):

    region_name = db.StringProperty()



class Domain(Model):
    regions = db.ListProperty(db.Key)



class User(Model):

    #The last notification this user has seen (notificationID should be an ascending number)
    last_notification_id = db.IntegerProperty()

    #PropID/OArgID/SArgID/RebID/UserID
    subscriptions = db.ListProperty(db.Key)



class UserDomainData(Model):

    PARENT = "Domain"

    # balance is specific for each domain
    balance = db.IntegerProperty()

    # in case the user is blocked - he is blocked in the domain
    block_expiration = db.DateTimeProperty(auto_now=True, auto_now_add=30.0) # 30 days?



#To be used, for now, only in root propositions
class Paper(Model):

    PARENT = "Domain"

    title       = db.StringProperty()
    community   = db.BooleanProperty()  # indicates if this is a community paper
    total_bids  = db.IntegerProperty()  # aggregated data
    last_bid_time    = db.DateTimeProperty()
    votes_to_accept  = db.IntegerProperty()
    votes_to_reject  = db.IntegerProperty()
    votes_to_abstain = db.IntegerProperty()
    certainty   = db.FloatProperty()    # (redundant) statistical certainty of the results
    status      = db.CategoryProperty(choices = (constants.PAPER_STATUS.all))



class Bid(Model):

    PARENT = "Paper"

    #bidID = UserID
    amount = db.IntegerProperty()



class Proposition(Model):
    PARENT = "(Paper,Proposition,ArgumentBase)"

    submitted_by = db.ReferenceProperty(User)

    # in a sub-proposition, this is the selected text from the parent proposition
    body         = db.TextProperty()
    version      = db.IntegerProperty()
    # can only be edited by the submitter
    last_edited  = db.DateTimeProperty(auto_now=True)



class Comment(Model):
    PARENT = "(Proposition,ArgumentBase)"
    submitted_by = db.ReferenceProperty(User)

    #comments on user id means writing on his wall
    time         = db.DateTimeProperty(auto_now=True)
    body         = db.TextProperty()
    liked_by     = db.ListProperty(db.Key)
    deleted      = db.BooleanProperty()



class ArgumentBase(PolyModel):

    submitted_by = db.ReferenceProperty(User)
    body         = db.TextProperty()
    version      = db.IntegerProperty()

    # if the counter argument/rebuttal was edited - this is the deadline for editing
    edit_by      = db.DateTimeProperty()
    # users who moderated up/down the argument/rebuttal
    mod_up       = db.ListProperty(db.Key)
    mod_down     = db.ListProperty(db.Key)
    # calculated with every new moderation/new bid
    mod_rank     = db.FloatProperty()
    # calculated with every new moderation/new bid
    mod_position = db.IntegerProperty()

    deleted      = db.BooleanProperty()



class SupportingArgument(ArgumentBase):
    PARENT = "Proposition"

class OpposingArgument(ArgumentBase):
    PARENT = "Proposition"

class RebuttalArgument(ArgumentBase):
    PARENT = "(SupportingArgument,OpposingArgument)"



class OldObject(Model):
    # e.g. DomainID/PropID/OArgID/VersionID
    PARENT = "(Proposition, ArgumentBase)"
    body      = db.TextProperty()



class EventBase(PolyModel):

    # Derived event classes will describe here what actions initiate the event
    # as well which fields should be filled by what information
    INITIATING_ACTIONS = ()

    action      = db.CategoryProperty()
    time        = db.DateTimeProperty(auto_now=True)

    by_user     = db.ReferenceProperty(User)

    # Other users related to the event from a community perspective (showing up on their profile)
    related_to  = db.ListProperty(db.Key)



class PaperEvent(EventBase):
    PARENT = "Paper"
    INITIATING_ACTIONS = (
              ("created",    dict(by_user="submitter")),
              ("edited",     dict(by_user="submitter")),
              ("finalized",  dict(by_user="submitter", related_to="bidders")),
              ("dropped",    dict(by_user="submitter", related_to="bidders")),
              ("referendum", dict(by_user="submitter", related_to="bidders")),
              ("accepted",   dict(by_user="submitter", related_to="bidders")),
              ("rejected",   dict(by_user="submitter", related_to="bidders")),
            )



class PaperBidEvent(PaperEvent):
    INITIATING_ACTIONS = (
              ("bid",         dict(by_user="bidder", related_to="submitter")),
              )
    bid_amount    = db.IntegerProperty()

    # New Supporting/Opposing bid | Supporting/Opposing bid withdrawn
    bid_type      = db.CategoryProperty(choices = (constants.BID_ACTION.all))


class ArgumentEvent(EventBase):
    PARENT = "ArgumentBase"
    INITIATING_ACTIONS = (
              ("created",    dict(by_user="submitter", related_to="bidders, prop_submitter")),
              ("edited",     dict(by_user="submitter", related_to="dueler")),
              ("dropped",    dict(by_user="submitter", related_to="dueler")),
            )



class ArgumentModeratedEvent(ArgumentEvent):
    INITIATING_ACTIONS = (
              ("moderated",  dict(by_user="moderator", related_to="argument_submitter")),
              )
    old_rank        = db.FloatProperty()
    old_position    = db.IntegerProperty()
    previous_lead   = db.ReferenceProperty(ArgumentBase)



class CommentEvent(EventBase):
    PARENT = "Comment"
    INITIATING_ACTIONS = (
              ("created",    dict(by_user="submitter")),
              ("liked",      dict(by_user="liker", related_to="submitter")),
              ("dropped",    dict(by_user="submitter")),
              ("mention",    dict(by_user="submitter", related_to="mentioned_user")),
            )

class Notification(Model):
    PARENT = "User"
    event = db.ReferenceProperty(EventBase)




def _fixParentDefinitions():
    _this_module = sys.modules[__name__]
    for name, cls in inspect.getmembers(_this_module, lambda m: inspect.isclass(m) and issubclass(m, Model)):
        if hasattr(cls, "PARENT") and isinstance(cls.PARENT, basestring):
            parent = eval(cls.PARENT, globals())
            if not isinstance(parent, (tuple,list)):
                parent = (parent,)
            cls.PARENT = parent

_fixParentDefinitions()