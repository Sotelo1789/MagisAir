from django.contrib import admin

from .models import (
    City, FlightRoute, FlightSchedule, Flight,
    Passenger, Booking, ItineraryItem,
    AdditionalItem, BookingItem, CrewMember, CrewAssignment
)

# Register your models here.
admin.site.register(City)
admin.site.register(FlightRoute)
admin.site.register(FlightSchedule)
admin.site.register(Flight)
admin.site.register(Passenger)
admin.site.register(Booking)
admin.site.register(ItineraryItem)
admin.site.register(AdditionalItem)
admin.site.register(BookingItem)
admin.site.register(CrewMember)
admin.site.register(CrewAssignment)