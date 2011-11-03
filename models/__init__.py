

from google.appengine.ext import db

class ACMModel(db.Model):
    ANCESTORS = []


class System(ACMModel):
    # systemID = facebook/google/tweeter/internal etc
    name = db.StringProperty() 



class Authentication(ACMModel):

    ANCESTORS = [System]

    # the screen name of the user
    user_id = db.StringProperty()



class RegionID(ACMModel):

    region_name = db.StringProperty()



class Domain(ACMModel):
    regions = db.ListProperty(db.Key)



class User(ACMModel):

    #The last notification this user has seen (notificationID should be an ascending number)                            
    last_notification_id = db.ReferenceProperty(db.Key)
    
    #PropID/OArgID/SArgID/RebID/UserID
    subscriptions = db.ListProperty(db.Key)



class UserDomainData(ACMModel):

    ANCESTORS = [Domain]

    # balance is specific for each domain
    balance = db.IntegerProperty()
    
    # in case the user is blocked - he is blocked in the domain
    block_expiration = db.DateTimeProperty(auto_now=True, auto_now_add=30.0) # 30 days?                    


#To be used, for now, only in root propositions
class Paper(ACMModel):
    
    ANCESTORS = [Domain]

    title       = db.StringProperty()                    
    community   = db.BooleanProperty()  # indicates if this is a community paper
    total_bids  = db.IntegerProperty()  # aggregated data
    last_bid_time    = db.DateTimeProperty()
    votes_to_accept  = db.IntegerProperty()
    votes_to_reject  = db.IntegerProperty()
    votes_to_abstain = db.IntegerProperty()
    status      = db.CategoryProperty() # draft/debate/referendum/accepted/rejected/dropped        
    certainty   = db.FloatProperty()    # (redundant) statistical certainty of the results            

class Bid(ACMModel): pass
class Proposition(ACMModel): pass
class ArgumentBase(ACMModel, db.polymodel.PolyModel): pass
class Comment(ACMModel): pass
"""
Kind:Bid (DomainID/PaperID/SBidID | OBidID)                    bidID = UserID        
    Amount    Integer                    
    Free    Yes/No            Extra Free bid of 1 point for for users that posted arguments/rebuttal        
Kind:Proposition (DomainID/PaperID/PropID) (*/PropID | OArgID | SArgID | RebID/PropID)                    Also as a sub proposition: e.g. UserID/DomainID/PropID/UserID/OArgID/UserID/PropID        
    Submitter    UserID                    
    Body    Text            In a sub-proposition, this is the selected text from the parent proposition        
    Version    Integer                    
    Last Edited    Date & Time            can only be edited by the submitter        
                            
Kind:Supporting, Opposing Arguments (*/PropID/SArgID | OArgID) & Rebuttals (*/SArgID | OArgID/RebID)                            
    Submitter    UserID                    
    Body    Text                    
    Version    Integer                    
    Edit by    Date & Time            If the counter argument/rebuttal was edited - this is the deadline for editing        
    Mod Down    Array of User IDs            users who moderated down the argument/rebuttal        
    Mod Up    Array of User IDs            users who moderated up the argument/rebuttal        
    Mod Rank    Float            Calculated with every new moderation/new bid        
    Position    Integer            Calculated with every new moderation/new bid        
    Deleted    Yes/No                    
Kind:Old Versions (*/PropID | OArgID | SArgID | RebID/VersionID)                    e.g. DomainID/PropID/OArgID/VersionID        
    Body    Text                    
                            
Kind:Comments (*/PropID | OArgID | SArgID | RebID/CommentID)                            
    Submitter    UserID                    
    Timestamp    Date & Time            Comments on User ID means writing on his wall        
    Body    Text                    
    Likes    Array of user IDs                    
    Deleted    Yes/No                    
"""

class Event(ACMModel):

    ANCESTORS = [(Paper, ArgumentBase, Comment)]

    type        = db.CategoryProperty()
    time        = db.DateTimeProperty()
    by_user     = db.ReferenceProperty(User)
    
    # Other users related to the event from a community perspective (showing up on their profile)
    related_to  = db.ListProperty(db.Key)                 
    """
    Object:PaperID                        
        Event    "Created"    By = Submitter    Created/Finalized/Dropped/Referendum/Accepted/Rejected        
        Event    "Edited"    By = Submitter            
        Event    "Finalized"    By = Submitter, Related = Bidders            
        Event    "Dropped"    By = Submitter, Related = Bidders            
        Event    "Referendum"    By = Submitter, Related = Bidders            
        Event    "Accepted"    By = Submitter, Related = Bidders            
        Event    "Rejected"    By = Submitter, Related = Bidders            
        Event    "Bid"    By = Bidder, Related = Submitter            
            bid_amount    integer            
            type          Value List    New Supporting/Oppsing bid | Supporting/Opposing bid withdrawn        
                            
    Object:SArg/OArg/Reb                        
        Event    "Created"    By = Submitter, Related = Dueler+Prop Submitter            
        Event    "Edited"    By = Submitter, Related = Dueler            
        Event    "Deleted"    By = Submitter, Related = Dueler            
        Event    "Moderated"    By = Moderator, Related = Moderated            
            old_rank        Float            
            old_position    Integer            
            previous_lead   RebID            
    Object:Comment                        
        Event    "New Comment"    By = Submitter            
        Event    "Like Comment"    By = Liker, Related = Submitter            
        Event    "Delete Comment"    By = Submitter            
        Event    "Mentioned"    By = Submitter, Related = Mentioned
    """

class Notification(ACMModel):
    ANCESTORS = [User]
    event = db.ReferenceProperty(Event)
