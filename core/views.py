from django.shortcuts import render, redirect
from .models import Passenger, Flight, Booking, ItineraryItem, FlightSchedule, FlightRoute, City, CrewMember, CrewAssignment
from django.utils import timezone
import random
from .forms import PassengerForm, FlightForm, FlightRouteForm, CityForm, CrewMemberForm, CrewAssignmentForm 
from django.db.models import Sum

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

def flight_schedule_view(request):
    # Fetch all flights, sorted by date and then departure time
    flights = Flight.objects.select_related('schedule', 'route', 'route__origin_city', 'route__destination_city').all().order_by('schedule__date', 'departure_time')
    
    return render(request, 'core/flight_schedule.html', {'flights': flights})

def add_flight_view(request):
    if request.method == 'POST':
        form = FlightForm(request.POST)
        if form.is_valid():
            # 1. Get the date the user picked
            date_picked = form.cleaned_data['schedule_date']
            
            # 2. Check if a Schedule exists for this date, OR create a new one
            #    (This is the magic line that fixes your issue)
            schedule_obj, created = FlightSchedule.objects.get_or_create(
                date=date_picked,
                defaults={'schedule_id': random.randint(10000, 99999)} # Handle PK manual entry
            )

            # 3. Create the flight object but don't save yet
            flight = form.save(commit=False)
            
            # 4. Attach the found/created schedule to the flight
            flight.schedule = schedule_obj
            flight.flight_no = random.randint(100, 999)
            
            flight.save()
            return redirect('flight_schedule')
    else:
        form = FlightForm()

    return render(request, 'core/add_flight.html', {'form': form})



def flight_routes_view(request):
    # Fetch routes with their related city data to avoid lag
    routes = FlightRoute.objects.select_related('origin_city', 'destination_city').all()
    return render(request, 'core/flight_routes.html', {'routes': routes})

def add_route_view(request):
    if request.method == 'POST':
        form = FlightRouteForm(request.POST)
        if form.is_valid():
            route = form.save(commit=False)
            # Generate a random Route ID
            route.route_id = random.randint(100, 999)
            route.save()
            return redirect('flight_routes')
    else:
        form = FlightRouteForm()

    return render(request, 'core/add_route.html', {'form': form})



def city_list_view(request):
    cities = City.objects.all().order_by('city_name')
    return render(request, 'core/city_list.html', {'cities': cities})

def add_city_view(request):
    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            city = form.save(commit=False)
            # Generate random ID for the city
            city.city_id = random.randint(100, 999)
            city.save()
            return redirect('city_list')
    else:
        form = CityForm()

    return render(request, 'core/add_city.html', {'form': form})


# --- CREW MEMBERS (DIRECTORY) ---
def crew_list_view(request):
    crew = CrewMember.objects.all().order_by('last_name')
    return render(request, 'core/crew_list.html', {'crew': crew})

def add_crew_member_view(request):
    if request.method == 'POST':
        form = CrewMemberForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            member.crew_id = random.randint(1000, 9999) # Random Employee ID
            member.save()
            return redirect('crew_list')
    else:
        form = CrewMemberForm()
    return render(request, 'core/add_crew_member.html', {'form': form})

# --- CREW ASSIGNMENTS (ROSTER) ---
def crew_assignment_view(request):
    # Fetch assignments with related data
    assignments = CrewAssignment.objects.select_related('crew', 'flight', 'flight__route', 'flight__schedule').all().order_by('flight__schedule__date')
    return render(request, 'core/crew_assignments.html', {'assignments': assignments})

def add_assignment_view(request):
    if request.method == 'POST':
        form = CrewAssignmentForm(request.POST)
        if form.is_valid():
            assign = form.save(commit=False)
            assign.crew_assignment_id = random.randint(10000, 99999)
            # Map the form date field to the model field
            assign.assignment_date = form.cleaned_data['assignment_date']
            assign.save()
            return redirect('crew_assignments')
    else:
        form = CrewAssignmentForm()
    return render(request, 'core/add_assignment.html', {'form': form})


def dashboard_view(request):
    # 1. Calculate Counts
    total_passengers = Passenger.objects.count()
    total_flights = Flight.objects.count()
    total_bookings = Booking.objects.count()
    
    # 2. Calculate Total Revenue (Sum of all booking costs)
    revenue_data = Booking.objects.aggregate(Sum('total_cost'))
    total_revenue = revenue_data['total_cost__sum'] or 0 # Default to 0 if None

    # 3. Get Recent Bookings (Last 5)
    recent_bookings = Booking.objects.select_related('passenger').order_by('-booking_id')[:5]

    context = {
        'total_passengers': total_passengers,
        'total_flights': total_flights,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'core/dashboard.html', context)