from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib import auth

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from events.models import UserProfile, Event, Host, Guest, Task, Invitee
#from events.forms import TaskForm, EventForm #, LoginForm, EditProfileForm

from django.contrib.sites.models import Site

import datetime
import random
import re
import hashlib

class brew_access_required(object):
    def __init__(self, f):
        self.f = f
        
    def __call__(self, *args):
        request = args[0]
        if request.method != "POST":
            return HttpResponseRedirect(reverse("events_userhome"))
    
        event_id = request.POST.get("event_id")
    
        user = request.user.get_profile()
        try:
            event_current = Event.objects.get(pk=int(event_id))
        except Event.DoesNotExist:
            print "Trying to save to an event which does not exist."
            return HttpResponseRedirect(reverse("events_userhome"))

        # Check if the user is invited to / host of this event
        try:
            Guest.objects.get(eid=event_current, uid=user)
        except:
            try:
                Host.objects.get(eid=event_current, uid=user)
            except:
                print "Trying to gatecrash."
                return HttpResponseRedirect(reverse("events_userhome"))

        self.f(*args)
        
        return HttpResponseRedirect(reverse("events.views.event",
                                            args=(event_id,)))
        
@login_required
def userhome(request):
    """ This is the default view that a user signing in will see."""
    print 'Inside userhome'
    user = request.user.get_profile()
    #user = RequestContext(request)["user"].get_profile()
    host_list = [b.eid for b in Host.objects.filter(uid = user)]
    guest_list = [g.eid for g in Guest.objects.filter(uid = user)]
    invitee_list = set([g.eid for g in Invitee.objects.filter(uid = user)])
    template_vars = {'user':user,
                     'host_list':host_list,
                     'guest_list':guest_list,
                     'invitee_list':invitee_list,
                     'save_event':reverse("events.views.save_event"),
                     'join_event':reverse("events.views.join_event"),
                     'is_logged_in':True,
                     }
    return render_to_response("events/UserHome.html", template_vars,
                              context_instance=RequestContext(request))

@login_required
def save_event(request):
    """ Create a new event """
    print "In Save Event"
    if request.method != "POST":
        print "Save brew received a non post"
        return HttpResponseRedirect(reverse("events_userhome"))

    name = request.POST.get('event_name')
    description = request.POST.get("event_description")
    
    # On empty POST request, return to user home.
    if(name.strip() == "" and description.strip() == ""):
        print "Empty form received"
        return HttpResponseRedirect(reverse("events_userhome"))

    # Create a new event and save it.
    new_event = Event()
    new_event.name = name
    new_event.description = description
    new_event.save()
    print "New Event Created ", new_event.ident
    print type(new_event.ident), str(new_event.ident)
    # Save the user as the host of the new event
    user = request.user.get_profile()
    admin = Host()
    admin.uid = user
    admin.eid = new_event
    admin.save()
    return HttpResponseRedirect(reverse("events.views.event",
                                        args=(new_event.ident,)))
    
@login_required
def join_event(request):
    """Join making a brew you have been invited to"""
    if request.method != "POST":
        print "Save brew received a non post"
        return HttpResponseRedirect(reverse("events_userhome"))

    yes = True if request.POST.get('join_brew_yes') != None else False
    no = True if request.POST.get('join_brew_no') != None else False
    brew_id = request.POST.get("event_id")
    #user = RequestContext(request)["user"].get_profile()
    user = request.user.get_profile()
    if yes:
        new_guest = Guest()
        new_guest.uid = user
        try:
            new_guest.eid = Event.objects.get(pk=brew_id)
            invitee = Invitee.objects.get(eid=new_guest.eid, uid=user)
        except ObjectDoesNotExist:
            print "Trying to join a brew to which you were not invited."
            return HttpResponseRedirect(reverse("events_userhome"))
        except MultipleObjectsReturned:
            print 'This is not supposed to happen. Problem with insertion'
            return HttpResponseRedirect(reverse("events_userhome"))
        new_guest.save()
        invitee.delete()
        return HttpResponseRedirect(reverse("events.views.event", args=(brew_id,)))
    elif no:
        invitee = Invitee.objects.get(eid=Event.objects.get(pk=brew_id), uid=user)
        invitee.delete()
        return HttpResponseRedirect(reverse("events_userhome"))
    else:
        return HttpResponseRedirect(reverse("events_userhome"))

@login_required
def event(request, event_id):
    """ Display an existing event """
    try:
        event = Event.objects.get(pk=event_id)
    except ObjectDoesNotExist:
        print "Trying to join a event to which you were not invited."
        return HttpResponseRedirect(reverse("events_userhome"))        
    task_list =  Task.objects.filter(eid=event_id)
    guest_list = [g.uid for g in Guest.objects.filter(eid=event_id)]
    template_vars = {"brew": event,
                     "task_list": task_list,
                     "guest_list": guest_list,
                     "homeurl": reverse("events_userhome"),
                     'is_logged_in': True,
                     }
    return render_to_response("events/EventHome.html", template_vars,
                              context_instance=RequestContext(request))

@login_required
@brew_access_required
def save_task(request):
    brew_id = request.POST.get("event_id")
    brew_obj = Event.objects.get(pk=int(brew_id))

    for i in range(len(request.POST.getlist('name'))):
        name = request.POST.getlist('name')[i]
        description = request.POST.getlist("description")[i]
        print "Form info :", name, description
        if( name.strip() == "" and description.strip() == ""):
            continue
        new_ingre = Task()
        new_ingre.name = name
        new_ingre.description = description
        new_ingre.eid = brew_obj
        new_ingre.save()
                
@login_required
@brew_access_required
def delete_task(request):
    i = request.POST.get('task_id')
    print i
    try:
        task = Task.objects.get(pk=int(i))
    except ObjectDoesNotExist:
        print "Trying to save an task which does not exist."
        return HttpResponseRedirect(reverse("events_userhome"))

    task.delete()

def process_event(request, event_id):
    print 'processing event'
    print event_id, request
    try:
        event = Event.objects.get(pk=int(event_id))
    except ObjectDoesNotExist:
        print 'Trying to delete a non-existant event'
        return HttpResponseRedirect(reverse("events_userhome"))
    event.delete()
    return HttpResponseRedirect(reverse("events_userhome"))
    
@login_required
@brew_access_required
def volunteer_for_task(request):
    i = request.POST.get('task_id')
    print i
    try:
        task = Task.objects.get(pk=int(i))
    except ObjectDoesNotExist:
        print "Trying to save an task which does not exist."
        return HttpResponseRedirect(reverse("events_userhome"))

    # Only save if the task has not already been assigned before
    if(task.assignee == None):
        #task.assignee = RequestContext(request)["user"].get_profile()
        task.assignee = request.user.get_profile()
        task.save()
        print "vol", i, task.name, task.assignee
    return

@login_required
def invite_friends(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("events_userhome"))
    
    if request.POST.get("friend_invite") == None or request.POST.get("event_id") == None:
        print "problem", request.POST
        return HttpResponseRedirect(reverse("events_userhome"))
    
    brew_id = request.POST.get("event_id")
    friend_str = request.POST.get("friend_invite")

    user = request.user.get_profile()
    # Expecting a comma seperated list of usernames
    friend_list = friend_str.split(",")
    for friend in friend_list:
        f = friend.strip()

        try:
            current_brew = Event.objects.get(pk=brew_id)
            invited_user = UserProfile.objects.get(user__username=f)
            
            guest_list = Guest.objects.filter(uid = invited_user, eid = current_brew)
            invitee_list = Invitee.objects.filter(uid = invited_user, eid = current_brew)
            brewmaster_list = Host.objects.filter(uid = invited_user, eid = current_brew)
            
            if( len(guest_list) == 0 and len(invitee_list) == 0 and len(brewmaster_list) == 0):
                print invited_user
                new_invitee = Invitee()
                new_invitee.uid = invited_user
                new_invitee.eid = Event.objects.get(pk=brew_id)
                new_invitee.save()
            else:
                print f, 'is already invited', guest_list, invitee_list, brewmaster_list
        except UserProfile.DoesNotExist:
            if '@' in f:
                send_email_invite(f, user, brew_id)
            else:
                print 'not found ',f
        
    return HttpResponseRedirect(reverse("events.views.event", args=(brew_id,)))
    
            
def send_email_invite(email_str, brewmaster, brew_id):
    ''' Send an invitation to email_str from user. Invite to brew_id '''
    print 'Sending email to ', email_str
    
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from django.conf import settings

    current_site = Site.objects.get_current()
    
    subject = render_to_string('events/accept_invitation_email_subject.txt',
                               { 'brewmaster': brewmaster,
                                 'site': current_site })
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())

    brew_obj = Event.objects.get(pk=int(brew_id))
    
    message = render_to_string('events/accept_invitation_email.txt',
                               { 'host': brewmaster,
                                 'event_name': brew_obj.name,
                                 'event_description': brew_obj.description,
                                 'site': current_site })
    
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email_str])
    return 

def event_edit_profile(request):
    ''' Edits the user profile'''
    
    if request.method == 'POST':
        edit_form = EditProfileForm(user=request.user, data=request.POST)
        if edit_form.is_valid():
            user = edit_form.save()
            try:
                #If there is a profile. notify that we have set the username
                profile = user.get_profile()
                profile.is_valid_username = True
                profile.save()
            except:
                pass
            request.user.message_set.create(message='Your profile has been updated.')
            return HttpResponseRedirect(reverse("events_userhome"))

    if request.method == 'GET':
        edit_form = EditProfileForm(user = request.user)

    payload = {'edit_form':edit_form, 'is_logged_in':True}
    return render_to_response('events/editprofile.html', payload,
                              context_instance=RequestContext(request))
