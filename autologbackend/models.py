from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Vehicle(models.Model):
	license_plate = models.CharField(max_length=8)
	vehicle_make = models.CharField(max_length=32)
	vehicle_model = models.CharField(max_length=32)
	build_year = models.IntegerField(default=0)
	mileage_unit = models.CharField(max_length=2,choices=(('mi','miles'),('km','kilometers')),default='km')

class Driver(models.Model):
	name = models.CharField(max_length=32)

class Trip(models.Model):
	vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE)
	driver = models.ForeignKey('Driver', on_delete=models.CASCADE)
	
	departure_time = models.DateTimeField('time of departure')
	departure_mileage = models.IntegerField(default=0)
	departure_location = models.ForeignKey('Location', on_delete=models.CASCADE,related_name='+')

	arrival_time = models.DateTimeField('time of arrival')
	arrival_mileage = models.IntegerField(default=0)
	arrival_location = models.ForeignKey('Location', on_delete=models.CASCADE,related_name='+')

class Location(models.Model):
	lat = models.FloatField(default=0.0)
	lon = models.FloatField(default=0.0)
	description = models.CharField(max_length=64)

	def __str__(self):
		return "(%.3f,%.3f) %s" % (self.lat,self.lon,self.description)