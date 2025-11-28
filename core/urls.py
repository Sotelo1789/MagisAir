from django.urls import path
from . import views

urlpatterns = [
    path('', views.booking_view, name='booking_view'),
    path('success/', views.success_view, name='success_view'),
    path('passengers/', views.passenger_list_view, name='passenger_list'),
    path('passengers/add/', views.add_passenger_view, name='add_passenger'),
    path('schedule/', views.flight_schedule_view, name='flight_schedule'), 
    path('schedule/add/', views.add_flight_view, name='add_flight'), 
    path('routes/', views.flight_routes_view, name='flight_routes'),      
    path('routes/add/', views.add_route_view, name='add_route'),  
    path('cities/', views.city_list_view, name='city_list'), 
    path('cities/add/', views.add_city_view, name='add_city'), 
    path('crew/', views.crew_list_view, name='crew_list'),
    path('crew/add/', views.add_crew_member_view, name='add_crew_member'),
    path('assignments/', views.crew_assignment_view, name='crew_assignments'),
    path('assignments/add/', views.add_assignment_view, name='add_assignment'),
]