from django.urls import path
from . import views

app_name = 'airline'

urlpatterns = [
    path(
        '',
        views.flight_routes_view,
        name='flight_routes'),
    path(
        'schedules/',
        views.flight_schedules_view,
        name='flight_schedules'),
    path(
        'schedules/new/',
        views.flight_schedule_create_view,
        name='flight_schedule_create'),
    path(
        'passengers/',
        views.passenger_list_view,
        name='passenger_list'),
    path(
        'passengers/new/',
        views.passenger_create_view,
        name='passenger_create'),
    path(
        'routes/new/',
        views.flight_route_create_view,
        name='flight_route_create'),
    path(
        'bookings/',
        views.booking_list_view,
        name='booking_list'),
    path(
        'bookings/create',
        views.booking_create,
        name='booking_create'),
    path(
        'bookings/details',
        views.booking_details,
        name='booking_details'),
    path(
        'bookings/<int:booking_id>/edit',
        views.booking_edit,
        name='booking_edit'),
    path(
        'bookings/<int:booking_id>/delete',
        views.booking_delete,
        name='booking_delete'),
    path(
        'crew/',
        views.crew_assignments_view,
        name='crew_assignments'),
    path(
        'crew/new/',
        views.crew_assignment_create_view,
        name='crew_assignment_create'),
    path(
        'success/',
        views.success_view,
        name='success_view'),
    path(
        'get-arrival-time/',
        views.get_arrival_time,
        name='get_arrival_time'),
]
