from django.db import models
from django.contrib import auth

class UserProfile(models.Model):
    """A User of the system"""
    user    = models.ForeignKey(auth.models.User, unique=True)
    address = models.CharField(max_length=50, blank=True)
    picture = models.ImageField(upload_to="events/images", blank=True)

    def getname(self):
        if self.user.first_name != None:
            name = self.user.first_name
        else:
            name = self.user.username
        return name

    def __unicode__(self):
        """What do we want to see in this model"""
        name = ""
        if self.user.first_name != None:
            name += self.user.first_name
        if self.user.last_name != None:
            name += " "+self.user.last_name
        if name.strip() == "":
            name += self.user.username
        return name

class Event(models.Model):
    """An event that a user is brewing up"""
    ident = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=500, blank=True)
    duedate = models.DateTimeField(null=True)
    def __unicode__(self):
        """What do we want to see in this model"""
        return self.name

class Task(models.Model):
    """ Tasks that are needed in a particular event"""
    ident = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=500, blank=True)
    assignee = models.ForeignKey("UserProfile", null=True)
    eid = models.ForeignKey("Event")
    def __unicode__(self):
        """What do we want to see in this model"""
        return self.name
    
class Host(models.Model):
    """A table of all the administrators and the events which they
    administrate"""
    uid = models.ForeignKey("UserProfile")
    eid = models.ForeignKey("Event", related_name="event_host")
    unique_together = ("uid","eid")
    def __unicode__(self):
        """What do we want to see in this model"""
        return self.uid.user.username + " : " + self.eid.name

class Guest(models.Model):
    """A table which consists of (events, guest) pairs that represents
    guests who have accepted invitations to events and are attending
    the event"""
    uid = models.ForeignKey("UserProfile")
    eid = models.ForeignKey("Event", related_name="event_guest")
    unique_together = ("uid","eid")
    def __unicode__(self):
        """What do we want to see in this model"""
        return self.uid.user.username + " : " + self.eid.name

class Invitee(models.Model):
    """A table which of consists (events, guest) pairs that represent
    users who have been invited to events"""
    uid = models.ForeignKey("UserProfile")
    eid = models.ForeignKey("Event", related_name="event_invitee")
    unique_together = ("uid","eid")
    def __unicode__(self):
        """What do we want to see in this model"""
        return self.uid.user.username + " : " + self.eid.name
    
# Create a callback for storing userprofiles    
def callback_create_user_profile(sender, **kwargs):
    print kwargs
    user = kwargs['instance']
    # We are looking at this user for the first time. Create a
    # UserProfile for the user.
    if kwargs['created']==True:
        new_profile = UserProfile()
        new_profile.user = user
        new_profile.save()
        print 'saved a new profile'            
    print 'In the callback'
    return

# Register the callback to create a user profile
from django.db.models.signals import post_save
post_save.connect(callback_create_user_profile, sender=auth.models.User)
