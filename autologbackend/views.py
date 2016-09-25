from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.utils.dateparse import *
from django.shortcuts import render
from django.template import RequestContext

from django.template import loader

from .models import Vehicle, Driver, Trip

# Create your views here.
def index(request):
	latest_trips_list = Trip.objects.order_by('-arrival_time')[:15]
	vehicles = Vehicle.objects.order_by('license_plate')

	template = loader.get_template('autologbackend/index.html')
	context = {
		'latest_trips_list': latest_trips_list,
		'vehicles': vehicles,
	}

	return HttpResponse(template.render(context,request))

def vehicle_detail(request,vehicle_id):
	vehicle = Vehicle.objects.get(pk=vehicle_id)
	latest_vehicle_trips = Trip.objects.filter(vehicle=vehicle).order_by('-arrival_time')[:15]

	last_trip = latest_vehicle_trips[0]


	context = {
		'vehicle': vehicle,
		'latest_vehicle_trips': latest_vehicle_trips,
		'last_trip' : last_trip,
	}

	template = loader.get_template('autologbackend/vehicle_detail.html')

	return HttpResponse(template.render(context,request))

def log_trip(request):
	vehicles = Vehicle.objects.order_by('license_plate')
	drivers = Driver.objects.order_by('name')

	context = {
		'vehicles' : vehicles,
		'drivers' : drivers,
	}

	template = loader.get_template('autologbackend/log_trip.html')
	return HttpResponse(template.render(context,request))

def submit_log_trip(request):
	try:
		selected_vehicle = Vehicle.objects.get(pk=request.POST['vehicle'])
		selected_driver = Driver.objects.get(pk=request.POST['driver'])

		departure_mileage = int(request.POST['departure_mileage'])
		arrival_mileage = int(request.POST['arrival_mileage'])

		departure_time = datetime.datetime.combine(
			parse_date(request.POST["departure_date"]),
			parse_time(request.POST["departure_time"])
			)

		arrival_time = datetime.datetime.combine(
			parse_date(request.POST["arrival_date"]),
			parse_time(request.POST["arrival_time"])
			)

		departure_location = request.POST["departure_location"]

		arrival_location = request.POST["arrival_location"]
	except KeyError as e:
		return HttpResponse('Something went wrong. <br />' + e.toString())
	else:
		trip = Trip(
			vehicle=selected_vehicle,
			driver=selected_driver,
			departure_time = departure_time,
			departure_mileage = departure_mileage,
			departure_location = departure_location,
			arrival_time = arrival_time,
			arrival_mileage = arrival_mileage,
			arrival_location = arrival_location
		)
		trip.save()

		return HttpResponseRedirect(reverse('index'))

def register_driver(request):
	return render(request,'autologbackend/register_driver.html')
	
def submit_register_driver(request):
	try:
		name = request.POST['name']
	except KeyError as e:
		return HttpResponse('Something went wrong. <br />' + e.toString())
	else:
		driver = Driver(name = name)
		driver.save()
		return HttpResponseRedirect(reverse('index'))

def register_vehicle(request):
	return render(request,'autologbackend/register_vehicle.html')

def submit_register_vehicle(request):
	request_context = RequestContext(request)

	try:
		license_plate = request.POST['license_plate']
		build_year = request.POST['build_year']
		make = request.POST['make']
		model = request.POST['model']
		mileage = int(request.POST['mileage'])
		mileage_unit = request.POST['mileage_unit']
	except KeyError as e:
		return HttpResponse('Something went wrong. <br />' + e.toString())
	else:
		vehicle = Vehicle(
			license_plate=license_plate,
			build_year = build_year,
			vehicle_make = make,
			vehicle_model = model,
			mileage= mileage,
			mileage_unit = mileage_unit
		)

		vehicle.save()
		return HttpResponseRedirect(reverse('index'))