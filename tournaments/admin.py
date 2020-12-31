'''
Admin python file for registering the tournament models in the admin interface
'''
from django.contrib import admin
from .models import Tournament

admin.site.register(Tournament)
