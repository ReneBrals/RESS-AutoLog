import urllib2, json
from math import sqrt, cos, sin, asin, pi, radians, pow
from .models import Location, Trip
import time

NOMINATIM_URL = "https://nominatim.openstreetmap.org/"

def rate_limited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)
    def decorate(func):
        lastTimeCalled = [0.0]
        def rateLimitedFunction(*args,**kargs):
            elapsed = time.clock() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait>0:
                time.sleep(leftToWait)
            ret = func(*args,**kargs)
            lastTimeCalled[0] = time.clock()
            return ret
        return rateLimitedFunction
    return decorate


def hav(theta):
	#returns hav(theta) where hav is the haversine function and theta is an angle in radians
	
	return (1-cos(theta))/2.0

def dist(lat1, lat2, long1, long2, r=6370):
	#returns the haversine great-circle distance between two points described by their coordinates in degrees
	#where r is the radius of the sphere (default being 6370km, a decent approximation of the radius of Earth)
	lat1 = radians(lat1)
	lat2 = radians(lat2)
	long1 = radians(long1)
	long2 = radians(long2)

	return 2*r*asin(sqrt(hav(lat2-lat1) + cos(lat1) * cos(lat2) * hav(long2-long1)))

@rate_limited(1)
def coords_from_name(name):
	#returns a tuple (lat,long) representing the coordinates on Earth of the searched name
	#returns None if no results are found

	url = NOMINATIM_URL + "search?format=json&addressdetails=1&q="+name.replace(" ","%20")
	raw = urllib2.urlopen(url).read()
	j = json.loads(raw)
	try:
		res = (float(j[0]['lat']), float(j[0]['lon']))
		return res
	except:
		return None

@rate_limited(1)
def name_from_coords(lat, lon):
	#returns the name of the street and town at the location described by the input coordinates
	#returns the town name if the street is not available
	#returns None if there are no results

	url = NOMINATIM_URL + "/reverse?format=json&namedetails=1&lat=%f&lon=%f" % (lat, lon)
	print url
	raw = urllib2.urlopen(url).read()
	j = json.loads(raw)

	road = ""
	try:
		road = j['address']['road']
	except KeyError:
		pass

	town = ""
	try:
		town = j['address']['suburb']
	except KeyError:
		pass
	

	if road and town:
		return "%s, %s" %(town, road)
	elif town:
		return town
	else:
		return None

def location_from_coords(lat, lon, epsilon=0.001):
	#returns the name of the street and town at the location described by the input coordinates
	#for caching purposes, coordinates within epsilon distance of each other are considered equal

	#First, look at locations if there are equal locations in the cache
	cached_locs = Location.objects.filter(lat__gte=lat-epsilon, lat__lte=lat+epsilon)
	cached_locs = Location.objects.filter(lon__gte=lon-epsilon, lon__lte=lon+epsilon)

	if cached_locs.count() >= 1:
		return cached_locs[0]
	else:
		name = name_from_coord(lat,lon)
		if name:
			loc = Location(lat, lon, name)
			loc.save()
			return loc
		else:
			return None

def location_from_name(name):
	#returns the coordinates on Earth of the searched location 
	#with caching to avoid hitting Nominatim too much

	#First, look if we have a location with the same name in the cache
	cached_locs = Location.objects.filter(description__icontains=name)

	if cached_locs.count() >= 1:
		return cached_locs[0]
	else:
		coords = coords_from_name(name)
		if coords:
			loc = Location(lat = coords[0], lon = coords[1], description = name)
			loc.save()
			return loc
		else:
			return None

def filter_trips_in_range_from(loc, range, trips):
	#returns a list of trips that arrived or departed within a certain range of a certain location
	#note that it returns a list: we're outside Django's ORM now

	return [t for t in trips if dist(t.departure_location.lat, loc.lat,t.departure_location.lon,loc.lon) < range]

def filter_trips_in_range_to(loc, range, trips):
	#returns a list of trips that arrived or departed within a certain range of a certain location
	#note that it returns a list: we're outside Django's ORM now

	return [t for t in trips if dist(t.arrival_location.lat, loc.lat,t.arrival_location.lon,loc.lon) < range]