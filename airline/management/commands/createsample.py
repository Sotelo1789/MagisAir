from django.core.management.base import BaseCommand
from django.utils import timezone
from airline.models import (AdditionalItem, Booking, BookingItem,
                            City, Flight, FlightRoute,
                            FlightSchedule, ItineraryItem, Passenger)
from datetime import timedelta, date


class Command(BaseCommand):
    help = 'Create sample data for testing purposes'

    def handle(self, *args, **options):
        City.objects.all().delete()
        FlightRoute.objects.all().delete()
        FlightSchedule.objects.all().delete()
        Flight.objects.all().delete()
        Passenger.objects.all().delete()
        AdditionalItem.objects.all().delete()
        Booking.objects.all().delete()
        BookingItem.objects.all().delete()

        # Cities
        mnl = City.objects.create(city_name='Manila')
        ceb = City.objects.create(city_name='Cebu')
        davao = City.objects.create(city_name='Davao')

        # Schedules
        s1 = FlightSchedule.objects.create(date=date.today())
        s2 = FlightSchedule.objects.create(date=date.today())

        # Routes
        r1 = FlightRoute.objects.create(
            origin_city=mnl, destination_city=ceb, duration=1.25, schedule=s1)
        r2 = FlightRoute.objects.create(
            origin_city=ceb, destination_city=davao, duration=1.5, schedule=s2)

        # Flights
        f1 = Flight.objects.create(
            arrival_time=timezone.now()+timedelta(minutes=r1.duration),
            departure_time=timezone.now()+timedelta(minutes=r1.duration),
            schedule=s1,
            route=r1
        )

        f2 = Flight.objects.create(
            arrival_time=timezone.now()+timedelta(minutes=r2.duration),
            departure_time=timezone.now()+timedelta(minutes=r2.duration),
            schedule=s2,
            route=r2
        )

        # Additional items
        baggage = AdditionalItem.objects.create(
            description='Extra Baggage', cost_per_unit=500.00)
        meal = AdditionalItem.objects.create(
            description='In-flight Meal', cost_per_unit=200.00)
        wifi = AdditionalItem.objects.create(
            description='WiFi Access', cost_per_unit=150.00)

        # Passengers
        p1 = Passenger.objects.create(
            first_name='Alice',
            last_name='Santos',
            birthdate='1990-01-01',
            gender='F')
        p2 = Passenger.objects.create(
            first_name='Ben',
            last_name='Cruz',
            birthdate='1985-05-12',
            gender='M')
        p3 = Passenger.objects.create(
            first_name='Carla',
            last_name='Reyes',
            birthdate='2000-09-03',
            gender='F')

        # Create a booking with items and itinerary
        b1 = Booking.objects.create(
            date_booked=date.today(),
            passenger=p1)
        bi1 = BookingItem.objects.create(
            booking=b1,
            item=baggage,
            quantity=2,
            subtotal_cost=baggage.cost_per_unit * 2)
        it1 = ItineraryItem.objects.create(booking=b1, flight=f1, cost=2500.00)
        b1.total_cost = bi1.subtotal_cost + it1.cost
        b1.save()

        b2 = Booking.objects.create(
            date_booked=date.today(),
            passenger=p2)
        bi2 = BookingItem.objects.create(
            booking=b2,
            item=meal,
            quantity=1,
            subtotal_cost=meal.cost_per_unit * 1)
        it2 = ItineraryItem.objects.create(booking=b2, flight=f2, cost=3000.00)
        b2.total_cost = bi2.subtotal_cost + it2.cost
        b2.save()

        self.stdout.write(self.style.SUCCESS('Sample data created.'))
