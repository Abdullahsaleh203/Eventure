from django.contrib import admin
from .models import User, Profile, Event, Schedule
# Register your models here.

admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Event)
admin.site.register(Schedule)
