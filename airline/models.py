from django.db import models


# 1. CITY
class City(models.Model):
    city_id = models.AutoField(primary_key=True)
    city_name = models.CharField(max_length=100)

    def __str__(self):
        return self.city_name


# 2. FLIGHT SCHEDULE
class FlightSchedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    date = models.DateField()

    def __str__(self):
        return str(self.date)


# 3. FLIGHT ROUTE
class FlightRoute(models.Model):
    route_id = models.AutoField(primary_key=True)
    origin_city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name='departures')
    destination_city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name='arrivals')
    duration = models.IntegerField(help_text="Duration in minutes")
    schedule = models.ForeignKey(
        FlightSchedule, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return f"Route {self.route_id}: {self.origin_city} to {self.destination_city}"


# 4. FLIGHT
class Flight(models.Model):
    flight_no = models.AutoField(primary_key=True)
    arrival_time = models.TimeField()
    departure_time = models.TimeField()
    schedule = models.ForeignKey(FlightSchedule, on_delete=models.CASCADE)
    route = models.ForeignKey(FlightRoute, on_delete=models.CASCADE)

    def __str__(self):
        return f"Flight {self.flight_no} ({self.schedule.date})"


# 5. PASSENGER
class Passenger(models.Model):
    passenger_id = models.AutoField(primary_key=True)
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    birthdate = models.DateField()
    gender_choices = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = models.CharField(max_length=1, choices=gender_choices)

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"


# 6. BOOKING
class Booking(models.Model):
    booking_id = models.AutoField(primary_key=True)
    date_booked = models.DateField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)

    def __str__(self):
        return f"Booking {self.booking_id} - {self.passenger}"


# 7. ITINERARY ITEM
class ItineraryItem(models.Model):
    itinerary_item_id = models.AutoField(primary_key=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    cost = models.DecimalField(max_digits=10, decimal_places=2)


# 8. ADDITIONAL ITEM (The Catalog)
class AdditionalItem(models.Model):
    item_id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=200)
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.description


# 9. BOOKING ITEM (The Purchase)
class BookingItem(models.Model):
    booking_item_id = models.AutoField(primary_key=True)
    item = models.ForeignKey(AdditionalItem, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    subtotal_cost = models.DecimalField(max_digits=10, decimal_places=2)


# 10. CREW MEMBER
class CrewMember(models.Model):
    crew_id = models.AutoField(primary_key=True)
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    role = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"


# 11. CREW ASSIGNMENT
class CrewAssignment(models.Model):
    crew_assignment_id = models.AutoField(primary_key=True)
    crew = models.ForeignKey(CrewMember, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    assignment_date = models.DateField()
