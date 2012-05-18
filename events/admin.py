from events.models import Event, Task, Host, Guest, Invitee, UserProfile
from django.contrib import admin

class TaskInline(admin.TabularInline):
    model = Task
    extra = 3

class EventAdmin(admin.ModelAdmin):
    fieldssets = [
        (None,               {'fields': ['name']}),
        ('Date information', {'fields': ['description']}),
    ]
    inlines = [TaskInline]
    list_display = ('name', 'description')
    search_fields = ['name', 'description']
    
admin.site.register(UserProfile)
admin.site.register(Event)
admin.site.register(Task)
admin.site.register(Host)
admin.site.register(Guest)
admin.site.register(Invitee)

