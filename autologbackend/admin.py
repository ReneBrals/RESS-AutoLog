from django.contrib import admin

# Register your models here.

from .models import Vehicle, Driver, Trip

admin.site.register(Vehicle)
admin.site.register(Driver)
admin.site.register(Trip)