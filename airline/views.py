import json
from .models import Passenger, Flight, Booking, ItineraryItem
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from decimal import Decimal
import random


def booking_view(request):
    if request.method == 'POST':

        # Get data from the form
        passenger_id = request.POST.get('passenger_id')
        flight_id = request.POST.get('flight_id')
        price = request.POST.get('price')

        try:
            # Ensure price is Decimal
            price = Decimal(price)
        except Exception:
            price = Decimal('0.00')

        passenger = Passenger.objects.get(passenger_id=passenger_id)
        flight = Flight.objects.get(flight_no=flight_id)

        # Create the Booking Record
        booking = Booking.objects.create(
            date_booked=timezone.now().date(),

            # Current prototype does not include additional items
            total_cost=price,
            passenger=passenger
        )

        # Create the Itinerary Item Record
        ItineraryItem.objects.create(
            itinerary_item_id=random.randint(1000, 99999),
            booking=booking,
            flight=flight,
            cost=price
        )

        return redirect('airline:success_view')

    # Fetch data to populate the dropdowns
    passengers = Passenger.objects.all()
    flights = Flight.objects.all()

    for f in flights:
        try:
            item = ItineraryItem.objects.filter(flight=f).first()
            if item and item.cost is not None:
                f.price = Decimal(item.cost)
            else:
                f.price = Decimal('0.00')
        except Exception:
            f.price = Decimal('0.00')

    return render(
        request,
        'booking.html',
        {
            'passengers': passengers,
            'flights': flights,
            'page': 'bookings'
        }
    )


def success_view(request):
    return render(request, 'success.html')


def passenger_list_view(request):
    passengers = Passenger.objects.all()
    return render(
        request,
        'passenger_list.html',
        {
            'passengers': passengers,
            'page': 'passengers'
        }
    )


@require_POST
def get_flight_price(request):
    body = json.loads(request.body)
    selected_option = body.get('flight_no')

    if not selected_option:
        return JsonResponse({'error': 'Missing flight number'}, status=400)

    flight = ItineraryItem.objects.filter(flight__flight_no=selected_option).first()

    if not flight:
        return JsonResponse({'error': 'Invalid flight number'}, status=404)

    return JsonResponse({'message': f'{flight.cost}'})
