from django.urls import path
from . import views

app_name = 'airline'

urlpatterns = [
    path('bookings/', views.booking_view, name='booking_view'),
    path('passengers/', views.passenger_list_view, name='passenger_list'),
    path('success/', views.success_view, name='success_view'),
    path('get-flight-price/', views.get_flight_price, name='get_flight_price'),
]
