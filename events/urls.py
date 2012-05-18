from django.conf.urls import patterns, url

urlpatterns = patterns('events.views',
    url(r"^$"               , 'userhome'           , name='events_userhome'),
    url(r"^(?P<event_id>\d+)$", 'event'              , name='events_eventid'),
    (r"save_task$"          , 'save_task'          ),
    (r"delete_task$"        , 'delete_task'        ),
    (r"volunteer_for_task$" , 'volunteer_for_task' ),
    (r"invite_friends$"     , 'invite_friends'     ),
    (r"save_event$"         , 'save_event'         ),
    (r"join_event$"         , 'join_event'         ),
    (r"process_event/(?P<event_id>\d+)" , 'process_event'      ),
)

