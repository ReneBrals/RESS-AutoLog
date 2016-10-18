from __future__ import unicode_literals
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.utils.dateparse import *
from django.shortcuts import render
from django.template import RequestContext
from django.db.models import F
from django.template import loader
from django.db.models.functions import Concat
from django.db.models import Value as V
from django.db.models import Max
from django.views.decorators.csrf import csrf_exempt



from .models import Vehicle, Driver, Trip
import geo

# Create your views here.
def index(request):
	latest_trips_list = Trip.objects.order_by('-arrival_time').annotate(distance=F('arrival_mileage')-F('departure_mileage'))[:15]
	vehicles = Vehicle.objects.order_by('license_plate')

	template = loader.get_template('autologbackend/index.html')
	context = {
		'latest_trips_list': latest_trips_list,
		'vehicles': vehicles,
	}

	return HttpResponse(template.render(context,request))

def vehicle_detail(request,vehicle_id):
	vehicle = Vehicle.objects.get(pk=vehicle_id)
	latest_vehicle_trips = Trip.objects.filter(vehicle=vehicle).order_by('-arrival_time').annotate(distance=F('arrival_mileage')-F('departure_mileage'))[:15]

	last_trip = latest_vehicle_trips[0]


	context = {
		'vehicle': vehicle,
		'latest_vehicle_trips': latest_vehicle_trips,
		'last_trip' : last_trip,
	}

	template = loader.get_template('autologbackend/vehicle_detail.html')

	return HttpResponse(template.render(context,request))

def log_trip(request, trip_id=-1, errors=""):
	vehicles = Vehicle.objects.order_by('license_plate')
	drivers = Driver.objects.order_by('name')

	context = {
		'vehicles' : vehicles,
		'drivers' : drivers,
	}

	if trip_id != -1:
		trip = Trip.objects.get(pk=trip_id)
		context['trip'] = trip

	if errors !="":
		context['errors'] = errors

	template = loader.get_template('autologbackend/log_trip.html')
	return HttpResponse(template.render(context,request))

@csrf_exempt
def submit_log_trip(request, trip_id=-1):
	errors = []

	if 'vehicle' in request.POST and request.POST['vehicle'] != '':
		try:
			selected_vehicle = Vehicle.objects.get(pk=request.POST['vehicle'])
		except IndexError:
			errors.append("Invalid vehicle ID.")
	else:
		errors.append("No vehicle selected.")

	if 'driver' in request.POST and request.POST['driver'] != '':
		try:
			selected_driver = Driver.objects.get(pk=request.POST['driver'])
		except IndexError:
			errors.append("Invalid driver ID.")
	else:
		errors.append("No driver selected.")


	if 'departure_mileage' in request.POST and request.POST['departure_mileage'] != '':
		try:
			departure_mileage = int(request.POST['departure_mileage'])
			if departure_mileage < 0:
				errors.append("Departure mileage is negative.")
		except ValueError:
			errors.append("Departure mileage is not a number.")
	else:
		errors.append("No departure mileage specified.")

	if 'arrival_mileage' in request.POST and request.POST['arrival_mileage'] != '':
		try:
			arrival_mileage = int(request.POST['arrival_mileage'])
			if arrival_mileage < 0:
				errors.append("Arrival mileage is negative.")
		except ValueError:
			errors.append("Arrival mileage is not a number.")
	else:
		errors.append("No arrival mileage specified.")

	if 'departure_date' in request.POST and 'departure_time' in request.POST:
		try:
			departure_time = datetime.datetime.combine(
				parse_date(request.POST["departure_date"]),
				parse_time(request.POST["departure_time"])
			)
		except:
			errors.append("Departure date/time is not a valid date/time.")
	elif 'departure_datetime' in request.POST and request.POST['departure_datetime'] != '':
		departure_time = parse_datetime(request.POST["departure_datetime"])
		if departure_time == None:
			errors.append("Departure date/time is not a valid date/time.")
	else:
		errors.append("No departure date/time specified.")

	if 'arrival_date' in request.POST and 'arrival_time' in request.POST:
		try:
			arrival_time = datetime.datetime.combine(
				parse_date(request.POST["arrival_date"]),
				parse_time(request.POST["arrival_time"])
			)
		except:
			errors.append("Arrival date/time is not a valid date/time.")
	elif 'arrival_datetime' in request.POST and request.POST['arrival_datetime'] != '':
		arrival_time = parse_datetime(request.POST["arrival_datetime"])
		if arrival_time == None:
			errors.append("Arrival date/time is not a valid date/time.")
	else:
		errors.append("No arrival date/time specified.")

	if 'departure_location' in request.POST and request.POST['departure_location'] != '':
		departure_location = geo.location_from_name(request.POST["departure_location"])
		if departure_location == None:
			departure_location = Location(lat = 0, lon = 0, description = request.POST['departure_location'])
	elif 'departure_location_lat' in request.POST and 'departure_location_lon' in request.POST:
		departure_location = geo.location_from_coords(float(request.POST["departure_location_lat"]),float(request.POST["departure_location_lon"]))
		if departure_location == None:
			errors.append("No results for geolocation at departure coordinates.")



	if 'arrival_location' in request.POST and request.POST['arrival_location'] != '':
		arrival_location = geo.location_from_name(request.POST["arrival_location"])
		if arrival_location == None:
			arrival_location = Location(lat = 0, lon = 0, description = request.POST['arrival_location'])
	elif 'arrival_location_lat' in request.POST and 'arrival_location_lon' in request.POST:
		arrival_location = geo.location_from_coords(float(request.POST["arrival_location_lat"]),float(request.POST["arrival_location_lon"]))
		if arrival_location == None:
			errors.append("No results for geolocation at arrival coordinates.")
	else:
		errors.append("No arrival location specified.")

	if not errors:
		if trip_id == -1:
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
		else:
			trip = Trip.objects.get(pk=trip_id)

			trip.vehicle=selected_vehicle
			trip.driver=selected_driver
			trip.departure_time = departure_time
			trip.departure_mileage = departure_mileage
			trip.departure_location = departure_location
			trip.arrival_time = arrival_time
			trip.arrival_mileage = arrival_mileage
			trip.arrival_location = arrival_location
			trip.save()

		if 'm' in request.POST and request.POST['m'] == 'm':
			return HttpResponseRedirect(reverse('mobile'))
		else:
			return HttpResponseRedirect(reverse('trips'))
	else:
		if 'm' in request.POST and request.POST['m'] == 'm':
			return HttpResponseRedirect(reverse('mobile'))
		else:
			return log_trip(request, errors)


def edit_trip(request, trip_id):
	trip = Trip.objects.get(pk=trip_id)
	vehicles = Vehicle.objects.order_by('license_plate')
	drivers = Driver.objects.order_by('name')

	context = {
		'trip' : trip,
		'vehicles' : vehicles,
		'drivers' : drivers,
	}

	template = loader.get_template('autologbackend/edit_trip.html')
	return HttpResponse(template.render(context,request))

def submit_edit_trip(request, trip_id):
	trip = Trip.objects.get(pk=trip_id)

	trip.vehicle= Vehicle.objects.get(pk=request.POST['vehicle']) 
	trip.driver = Driver.objects.get(pk=request.POST['driver']) 
	
	if 'arrival_location' in request.POST:
		arrival_location = geo.location_from_name(request.POST["arrival_location"])
	elif 'arrival_location_lat' in request.POST and 'arrival_location_lon' in request.POST:
		arrival_location = geo.location_from_coords(float(request.POST["arrival_location_lat"]),float(request.POST["arrival_location_lon"]))
	
	if 'departure_location' in request.POST:
		trip.departure_location = geo.location_from_name(request.POST["departure_location"])
	elif 'departure_location_lat' in request.POST and 'departure_location_lon' in request.POST:
		trip.departure_location = geo.location_from_coords(float(request.POST["departure_location_lat"]),float(request.POST["departure_location_lon"]))
	
	trip.departure_mileage = int(request.POST['departure_mileage'])
	trip.arrival_mileage = int(request.POST['arrival_mileage'])

	trip.departure_time = datetime.datetime.combine(
			parse_date(request.POST["departure_date"]),
			parse_time(request.POST["departure_time"])
	)

	trip.arrival_time = datetime.datetime.combine(
			parse_date(request.POST["arrival_date"]),
			parse_time(request.POST["arrival_time"])
	)

	trip.save()

	return HttpResponseRedirect(reverse('trips', kwargs={'page_nr': 0}))



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
			mileage_unit = mileage_unit
		)

		vehicle.save()
		return HttpResponseRedirect(reverse('index'))

def trips(request):
	RESULTS_PER_PAGE = 20

	trips_list = Trip.objects.order_by('-arrival_time')
	trips_list = trips_list.annotate(distance=F('arrival_mileage')-F('departure_mileage'))
	trips_list = trips_list.annotate(veh=Concat('vehicle__license_plate', V(' '), 'vehicle__vehicle_make', V(' '), 'vehicle__vehicle_model'))

	context = {}

	try:
		trips_list = trips_list.filter(veh__icontains=request.GET['vehicle'])
	except:
		pass

	try:
		trips_list = trips_list.filter(driver__name__icontains=request.GET['driver'])
	except:
		pass

	try:
		trips_list = trips_list.filter(distance__gte=request.GET['min_dist'])
	except:
		pass

	try:
		trips_list = trips_list.filter(distance__lte=request.GET['max_dist'])
	except:
		pass

	try:
		trips_list = trips_list.filter(arrival_time__gte= parse_date(request.GET['begin_date']))
	except:
		pass

	try:
		trips_list = trips_list.filter(arrival_time__lte= parse_date(request.GET['end_date'])+ datetime.timedelta(days=1))
	except:
		pass

	if 'arrival_location' in request.GET and request.GET['arrival_location']!='':
		
		if 'torange' in request.GET and request.GET['torange'] == '':
			rng = 0
		elif 'torange' in request.GET:
			rng = float(request.GET['torange'])
		else:
			rng = 0

		if rng == 0:
			
			trips_list = trips_list.filter(arrival_location__description__icontains=request.GET['arrival_location'])

	if 'departure_location' in request.GET and request.GET['departure_location']!='':
		if 'fromrange' in request.GET and request.GET['fromrange'] == '':
			rng = 0
		elif 'fromrange' in request.GET:
			rng = float(request.GET['fromrange'])
		else:
			rng = 0

		if rng == 0:
			trips_list = trips_list.filter(departure_location__description__icontains=request.GET['departure_location'])
		else:
			loc = geo.location_from_name(request.GET['departure_location'])
			trips_list = geo.filter_trips_in_range_from(loc, float(rng), trips_list)

	if 'arrival_location' in request.GET and request.GET['arrival_location']!='':
		if 'torange' in request.GET and request.GET['torange'] == '':
			rng = 0
		elif 'torange' in request.GET:
			rng = float(request.GET['torange'])
		else:
			rng = 0
		
		if rng >0:
			loc = geo.location_from_name(request.GET['arrival_location'])
			trips_list = geo.filter_trips_in_range_to(loc, rng, trips_list)

	context['trips_list'] = trips_list


	template = loader.get_template('autologbackend/trips.html')
	return HttpResponse(template.render(context,request))

def delete_trip(request,trip_id):
	Trip.objects.get(pk=trip_id).delete()

	return HttpResponseRedirect(reverse('trips'))

def vehicles(request, page_nr):
	RESULTS_PER_PAGE = 20

	context= {}
	

	vehs = Vehicle.objects.order_by('license_plate').annotate(last_date=Max("license_plate"))
	num_pages = vehs.count()/RESULTS_PER_PAGE
	if vehs.count()%RESULTS_PER_PAGE:
		num_pages += 1
	for e in vehs:
		try:
		    e.last_trip = Trip.objects.filter(vehicle=e).order_by('-arrival_time')[0]
		except:
			pass


	context['vehicle_list'] = vehs
	context['page_nr'] = page_nr
	context['num_pages'] = num_pages
	context['prev_page_nr'] = 0 if int(page_nr) == 0 else int(page_nr) - 1
	context['next_page_nr'] = int(page_nr) + 1 if int(page_nr) < (num_pages - 1) else int(page_nr)

	template = loader.get_template('autologbackend/vehicles.html')
	return HttpResponse(template.render(context,request))

def drivers(request, page_nr):
	RESULTS_PER_PAGE = 20

	context= {}
	

	dris = Driver.objects.order_by('name')
	num_pages = dris.count()/RESULTS_PER_PAGE
	if dris.count()%RESULTS_PER_PAGE:
		num_pages += 1
	for e in dris:
		try:
		    e.last_trip = Trip.objects.filter(driver=e).order_by('-arrival_time')[0]
		except:
			pass


	context['driver_list'] = dris
	context['page_nr'] = page_nr
	context['num_pages'] = num_pages
	context['prev_page_nr'] = 0 if int(page_nr) == 0 else int(page_nr) - 1
	context['next_page_nr'] = int(page_nr) + 1 if int(page_nr) < (num_pages - 1) else int(page_nr)

	template = loader.get_template('autologbackend/drivers.html')
	return HttpResponse(template.render(context,request))


def vehicles_bare(request):
	context= {}
	vehs = Vehicle.objects.all()
	context['vehicle_list'] = vehs

	template = loader.get_template('autologbackend/vehicles_bare.html')
	return HttpResponse(template.render(context,request))

def drivers_bare(request):
	dri = Driver.objects.all()
	context = {}
	context['drivers'] = dri

	template = loader.get_template('autologbackend/drivers_bare.html')
	return HttpResponse(template.render(context,request))

def delete_vehicle(request, vehicle_id):
	vehicle = Vehicle.objects.get(pk=vehicle_id)
	vehicle.delete()
	return HttpResponseRedirect(reverse('vehicles', kwargs={'page_nr': 0}))

def delete_driver(request, driver_id):
	vehicle = Vehicle.objects.get(pk=vehicle_id)
	vehicle.delete()

	return HttpResponseRedirect(reverse('drivers', kwargs={'page_nr': 0}))

def mobile_log(request):
	vehicles = Vehicle.objects.order_by('license_plate')
	drivers = Driver.objects.order_by('name')

	context = {
		'vehicles' : vehicles,
		'drivers' : drivers,
	}
	template = loader.get_template('autologbackend/mobile_log.html')
	return HttpResponse(template.render(context,request))

def mobile(request):
	context = {}
	template = loader.get_template('autologbackend/mobile.html')
	return HttpResponse(template.render(context,request))

def driver_detail(request, driver_id):
	driver = Driver.objects.get(pk=driver_id)
	latest_vehicle_trips = Trip.objects.filter(driver=driver).order_by('-arrival_time').annotate(distance=F('arrival_mileage')-F('departure_mileage'))[:15]

	last_trip = latest_vehicle_trips[0]


	context = {
		'driver': driver,
		'latest_vehicle_trips': latest_vehicle_trips,
		'last_trip' : last_trip,
	}

	template = loader.get_template('autologbackend/driver_detail.html')

	return HttpResponse(template.render(context,request))