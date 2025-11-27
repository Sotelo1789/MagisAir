from django.shortcuts import render, redirect
from .models import Passenger, Flight, Booking, ItineraryItem
from django.utils import timezone
import random
from .forms import PassengerForm

def booking_view(request):
    # 1. Handle Form Submission (POST request)
    if request.method == 'POST':
        # Get data from the form
        passenger_id = request.POST.get('passenger_id')
        flight_id = request.POST.get('flight_id')
        price = request.POST.get('price')

        # Get the actual objects from DB
        passenger = Passenger.objects.get(passenger_id=passenger_id)
        flight = Flight.objects.get(flight_no=flight_id)

        # Generate a random Booking ID (since we aren't using AutoField)
        new_booking_id = random.randint(1000, 99999)
        
        # Create the Booking Record
        booking = Booking.objects.create(
            booking_id=new_booking_id,
            date_booked=timezone.now().date(),
            total_cost=price, # For prototype, assuming 1 flight = total cost
            passenger=passenger
        )

        # Create the Itinerary Item Record
        ItineraryItem.objects.create(
            itinerary_item_id=random.randint(1000, 99999),
            booking=booking,
            flight=flight,
            cost=price
        )

        return redirect('success_view')

    # 2. Handle Page Load (GET request)
    # Fetch data to populate the dropdowns
    passengers = Passenger.objects.all()
    flights = Flight.objects.all()

    return render(request, 'core/booking.html', {
        'passengers': passengers,
        'flights': flights
    })

def success_view(request):
    return render(request, 'core/success.html')

def passenger_list_view(request):
    passengers = Passenger.objects.all()
    return render(request, 'core/passenger_list.html', {'passengers': passengers})



def add_passenger_view(request):
    if request.method == 'POST':
        form = PassengerForm(request.POST)
        if form.is_valid():
            # Don't save to DB yet, we need to generate an ID
            passenger = form.save(commit=False)
            # Generate a random 5-digit ID
            passenger.passenger_id = random.randint(10000, 99999)
            passenger.save()
            # Go back to the booking page so they can book the flight!
            return redirect('booking_view')
    else:
        form = PassengerForm()

    return render(request, 'core/add_passenger.html', {'form': form})