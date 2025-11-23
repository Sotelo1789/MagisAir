from .models import Passenger, Flight, Booking, ItineraryItem
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse
from django.utils import timezone
from decimal import Decimal
import random
import json


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

        # mark the session so the success page can only be shown after a real booking
        request.session['booking_created'] = True
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
    # Only show success page immediately after a booking was created.
    if not request.session.pop('booking_created', False):
        return redirect('airline:booking_list')

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


def booking_list_view(request):
    # List all bookings with related passenger and itinerary items
    bookings = Booking.objects.select_related('passenger').all().order_by('date_booked', '-booking_id')

    booking_rows = []
    for b in bookings:
        itinerary_items = ItineraryItem.objects.filter(booking=b).select_related('flight__route', 'flight__schedule')
        flights = []
        for it in itinerary_items:
            f = it.flight
            flights.append(f"{f.route.origin_city} ➝ {f.route.destination_city} | {f.schedule.date} @ {f.departure_time.strftime('%I:%M %p')}")

        booking_rows.append({
            'booking': b,
            'flights': flights,
        })

    return render(
        request,
        'booking_list.html',
        {
            'bookings': booking_rows,
            'page': 'bookings'
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


def page_temp(request):
    raise Http404('Temporarily Unavailable --- To Be Created')
