from django.contrib import admin
from apps.commercial.models import *
from django.apps import apps

for model in apps.get_app_config('authentication').models.values():
    admin.site.register(model)