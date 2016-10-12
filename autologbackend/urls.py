from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^vehicle/(?P<vehicle_id>[0-9]+)/$', views.vehicle_detail, name='vehicle_detail'),
    url(r'^log_trip/$', views.log_trip, name='log_trip'),
    url(r'^submit_log_trip/$', views.submit_log_trip, name='submit_log_trip'),
    url(r'^register_driver/$', views.register_driver, name='register_driver'),
    url(r'^submit_register_driver/$', views.submit_register_driver, name='submit_register_driver'),
    url(r'^register_vehicle/$', views.register_vehicle, name='register_vehicle'),
    url(r'^submit_register_vehicle/$', views.submit_register_vehicle, name='submit_register_vehicle'),
    #url(r'^trips/$', views.trips, name='trips'),
    url(r'^trips/(?P<page_nr>[0-9]+)/$', views.trips, name='trips'),
    url(r'^trips/delete_trip/(?P<trip_id>[0-9]+)/$', views.delete_trip, name='delete_trip'),
    url(r'^trips/edit_trip/(?P<trip_id>[0-9]+)/$', views.edit_trip, name='edit_trip'),
    url(r'^trips/submit_edit_trip/(?P<trip_id>[0-9]+)/$', views.submit_edit_trip, name='submit_edit_trip'),
    url(r'^vehicles/(?P<page_nr>[0-9]+)/$', views.vehicles, name='vehicles'),
    url(r'^vehicles_bare/$', views.vehicles_bare, name='vehicles_bare'),
    url(r'^drivers_bare/$', views.drivers_bare, name='drivers_bare'),
    url(r'^delete_vehicle/(?P<vehicle_id>[0-9]+)/$', views.delete_vehicle, name='delete_vehicle'),
    url(r'^mobile/$', views.mobile, name='mobile'),
    url(r'^mobile_log/$', views.mobile_log, name='mobile_log'),

]