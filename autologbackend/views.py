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

from .models import Vehicle, Driver, Trip

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
		pass
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

		return HttpResponseRedirect(reverse('trips', kwargs={'page_nr': 0}))

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
	trip.arrival_location = request.POST['arrival_location']
	trip.departure_location = request.POST['departure_location']
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
			mileage= mileage,
			mileage_unit = mileage_unit
		)

		vehicle.save()
		return HttpResponseRedirect(reverse('index'))

def trips(request, page_nr):
	RESULTS_PER_PAGE = 20

	trips_list = Trip.objects.order_by('-arrival_time')
	trips_list = trips_list.annotate(distance=F('arrival_mileage')-F('departure_mileage'))
	trips_list = trips_list.annotate(veh=Concat('vehicle__license_plate', V(' '), 'vehicle__vehicle_make', V(' '), 'vehicle__vehicle_model'))

	context = {}

	try:
		trips_list = trips_list.filter(veh__icontains=request.GET['vehicle'])
		context['vehicle_fill'] = request.GET['vehicle']
	except:
		pass

	try:
		trips_list = trips_list.filter(driver__name__icontains=request.GET['driver'])
		context['driver_fill'] = request.GET['driver']
	except:
		pass

	try:
		trips_list = trips_list.filter(departure_location__icontains=request.GET['departure_location'])
		context['dep_fill'] = request.GET['departure_location']
	except:
		pass

	try:
		trips_list = trips_list.filter(arrival_location__icontains=request.GET['arrival_location'])
		context['arr_fill'] = request.GET['arrival_location']
	except:
		pass

	try:
		trips_list = trips_list.filter(distance__gte=request.GET['min_dist'])
		context['mindist_fill'] = request.GET['min_dist']
	except:
		pass

	try:
		trips_list = trips_list.filter(distance__lte=request.GET['max_dist'])
		context['maxdist_fill'] = request.GET['max_dist']
	except:
		pass

	try:
		trips_list = trips_list.filter(arrival_time__gte= parse_date(request.GET['begin_date']))
		context['bdate_fill'] = request.GET['begin_date']
	except:
		pass

	try:
		trips_list = trips_list.filter(arrival_time__lte= parse_date(request.GET['end_date']))
		context['edate_fill'] = request.GET['end_date']
	except:
		pass

	num_pages = trips_list.count()/RESULTS_PER_PAGE
	if trips_list.count()%RESULTS_PER_PAGE:
		num_pages += 1



	context['num_pages'] = num_pages
	context['page_nr'] = page_nr
	context['prev_page_nr'] = 0 if int(page_nr) == 0 else int(page_nr) - 1
	context['next_page_nr'] = int(page_nr) + 1 if int(page_nr) < (num_pages - 1) else int(page_nr)

	if int(page_nr) < num_pages:
		trips_list = trips_list[int(page_nr)*RESULTS_PER_PAGE:(int(page_nr)+1)*RESULTS_PER_PAGE]

	context['trips_list'] = trips_list


	template = loader.get_template('autologbackend/trips.html')
	return HttpResponse(template.render(context,request))

def delete_trip(request,trip_id):
	Trip.objects.get(pk=trip_id).delete()

	return HttpResponseRedirect(reverse('trips', kwargs={'page_nr': 0}))

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

def delete_vehicle(request, vehicle_id):
	vehicle = Vehicle.objects.get(pk=vehicle_id)
	vehicle.delete()

	return HttpResponseRedirect(reverse('vehicles', kwargs={'page_nr': 0}))