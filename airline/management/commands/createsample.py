# from django.core.management.base import BaseCommand
# from django.utils import timezone
# from airline.models import (AdditionalItem, Booking, BookingItem,
#                             City, Flight, FlightRoute,
#                             FlightSchedule, ItineraryItem, Passenger)
# from datetime import timedelta, date, datetime


# class Command(BaseCommand):
#     help = 'Create sample data for testing purposes'

#     def handle(self, *args, **options):
#         City.objects.all().delete()
#         FlightRoute.objects.all().delete()
#         FlightSchedule.objects.all().delete()
#         Flight.objects.all().delete()
#         Passenger.objects.all().delete()
#         AdditionalItem.objects.all().delete()
#         Booking.objects.all().delete()
#         BookingItem.objects.all().delete()

#         # Cities
#         mnl = City.objects.create(city_name='Manila')
#         ceb = City.objects.create(city_name='Cebu')
#         davao = City.objects.create(city_name='Davao')

#         # Schedules
#         s1 = FlightSchedule.objects.create(date=date.today())
#         s2 = FlightSchedule.objects.create(date=date.today()+timedelta(days=4))

#         # Routes
#         r1 = FlightRoute.objects.create(
#             origin_city=mnl, destination_city=ceb, duration=1.25, schedule=s1)
#         r2 = FlightRoute.objects.create(
#             origin_city=ceb, destination_city=davao, duration=1.5, schedule=s2)

#         dep_time = datetime.combine(date=s1.date, time=timezone.now().time())
#         dep_time2 = datetime.combine(
#             date=s2.date,
#             time=(timezone.now()+timedelta(hours=3, minutes=30)).time())

#         # Flights
#         f1 = Flight.objects.create(
#             departure_time=dep_time,
#             arrival_time=dep_time+timedelta(minutes=r1.duration),
#             schedule=s1,
#             route=r1
#         )

#         f2 = Flight.objects.create(
#             departure_time=dep_time2,
#             arrival_time=dep_time2+timedelta(minutes=r2.duration),
#             schedule=s2,
#             route=r2
#         )

#         # Additional items
#         baggage = AdditionalItem.objects.create(
#             description='Extra Baggage', cost_per_unit=500.00)
#         meal = AdditionalItem.objects.create(
#             description='In-flight Meal', cost_per_unit=200.00)
#         wifi = AdditionalItem.objects.create(
#             description='WiFi Access', cost_per_unit=150.00)

#         # Passengers
#         p1 = Passenger.objects.create(
#             first_name='Alice',
#             last_name='Santos',
#             birthdate='1990-01-01',
#             gender='F')
#         p2 = Passenger.objects.create(
#             first_name='Ben',
#             last_name='Cruz',
#             birthdate='1985-05-12',
#             gender='M')
#         p3 = Passenger.objects.create(
#             first_name='Carla',
#             last_name='Reyes',
#             birthdate='2000-09-03',
#             gender='F')

#         # Create a booking with items and itinerary
#         b1 = Booking.objects.create(
#             date_booked=date.today(),
#             passenger=p1)
#         bi1 = BookingItem.objects.create(
#             booking=b1,
#             item=baggage,
#             quantity=2,
#             subtotal_cost=baggage.cost_per_unit * 2)
#         it1 = ItineraryItem.objects.create(booking=b1, flight=f1, cost=2500.00)
#         b1.total_cost = bi1.subtotal_cost + it1.cost
#         b1.save()

#         b2 = Booking.objects.create(
#             date_booked=date.today(),
#             passenger=p2)
#         bi2 = BookingItem.objects.create(
#             booking=b2,
#             item=meal,
#             quantity=1,
#             subtotal_cost=meal.cost_per_unit * 1)
#         it2 = ItineraryItem.objects.create(booking=b2, flight=f2, cost=3000.00)
#         b2.total_cost = bi2.subtotal_cost + it2.cost
#         b2.save()

#         self.stdout.write(self.style.SUCCESS('Sample data created.'))
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import connection
from airline.models import (
    AdditionalItem, Booking, BookingItem, City, CrewAssignment, CrewMember,
    Flight, FlightRoute, FlightSchedule, ItineraryItem, Passenger
)
from datetime import date, datetime, timedelta
from decimal import Decimal
import re


class Command(BaseCommand):
    help = 'Create sample data for testing purposes'

    def parse_date(self, date_str):
        """Parse date from DD/MM/YYYY format"""
        try:
            day, month, year = date_str.split('/')
            return date(int(year), int(month), int(day))
        except (Exception):
            return date.today()

    def parse_duration(self, duration_str):
        """Convert duration string like '3 hr 30 min' to minutes"""
        try:
            hours = 0
            minutes = 0
            if 'hr' in duration_str:
                hours_match = re.search(r'(\d+)\s*hr', duration_str)
                if hours_match:
                    hours = int(hours_match.group(1))
            if 'min' in duration_str:
                min_match = re.search(r'(\d+)\s*min', duration_str)
                if min_match:
                    minutes = int(min_match.group(1))
            return hours * 60 + minutes
        except (Exception):
            return 0

    def parse_time(self, time_str):
        """Parse time from HH:MM format"""
        try:
            hour, minute = time_str.split(':')
            return datetime.strptime(time_str, '%H:%M').time()
        except (Exception):
            return datetime.now().time()

    def handle(self, *args, **options):
        CrewAssignment.objects.all().delete()
        CrewMember.objects.all().delete()
        BookingItem.objects.all().delete()
        ItineraryItem.objects.all().delete()
        Booking.objects.all().delete()
        Flight.objects.all().delete()
        FlightSchedule.objects.all().delete()
        FlightRoute.objects.all().delete()
        AdditionalItem.objects.all().delete()
        Passenger.objects.all().delete()
        City.objects.all().delete()

        cities_map = {}
        cities_data = [
            {'City_ID': 'C001', 'CityName': 'Manila'},
            {'City_ID': 'C002', 'CityName': 'Singapore'},
            {'City_ID': 'C003', 'CityName': 'Tokyo'},
            {'City_ID': 'C004', 'CityName': 'Beijing'},
            {'City_ID': 'C005', 'CityName': 'Shanghai'},
            {'City_ID': 'C006', 'CityName': 'Rome'},
            {'City_ID': 'C007', 'CityName': 'Milan'},
            {'City_ID': 'C008', 'CityName': 'Zurich'},
            {'City_ID': 'C009', 'CityName': 'Istanbul'},
            {'City_ID': 'C010', 'CityName': 'Barcelona'},
        ]

        for city_data in cities_data:
            city = City.objects.create(city_name=city_data['CityName'])
            cities_map[city_data['City_ID']] = city
            self.stdout.write(f'Created city: {city.city_name}')

        routes_map = {}
        routes_data = [
            {'Route_ID': 'R001', 'OriginCity_ID': 'C001', 'DestinationCity_ID': 'C002', 'Duration': '3 hr 30 min'},
            {'Route_ID': 'R002', 'OriginCity_ID': 'C002', 'DestinationCity_ID': 'C001', 'Duration': '3 hr 15 min'},
            {'Route_ID': 'R003', 'OriginCity_ID': 'C001', 'DestinationCity_ID': 'C003', 'Duration': '4 hr 45 min'},
            {'Route_ID': 'R004', 'OriginCity_ID': 'C003', 'DestinationCity_ID': 'C001', 'Duration': '4 hr 30 min'},
            {'Route_ID': 'R005', 'OriginCity_ID': 'C004', 'DestinationCity_ID': 'C001', 'Duration': '5 hr 20 min'},
            {'Route_ID': 'R006', 'OriginCity_ID': 'C001', 'DestinationCity_ID': 'C006', 'Duration': '14 hr 15 min'},
        ]

        for route_data in routes_data:
            route = FlightRoute.objects.create(
                origin_city=cities_map[route_data['OriginCity_ID']],
                destination_city=cities_map[route_data['DestinationCity_ID']],
                duration=self.parse_duration(route_data['Duration']),
            )
            routes_map[route_data['Route_ID']] = route
            self.stdout.write(f'Created route: {route.origin_city.city_name} -> {route.destination_city.city_name}')

        schedules_map = {}
        schedules_data = [
            {'Schedule_ID': 'S001', 'Flight_No': 'MA800', 'Date': '21/12/2025'},
            {'Schedule_ID': 'S002', 'Flight_No': 'MA801', 'Date': '23/12/2025'},
            {'Schedule_ID': 'S003', 'Flight_No': 'MA800', 'Date': '24/12/2025'},
            {'Schedule_ID': 'S004', 'Flight_No': 'MA443', 'Date': '21/12/2025'},
            {'Schedule_ID': 'S005', 'Flight_No': 'MA444', 'Date': '22/12/2025'},
            {'Schedule_ID': 'S006', 'Flight_No': 'MA652', 'Date': '22/12/2025'},
            {'Schedule_ID': 'S007', 'Flight_No': 'MA234', 'Date': '21/12/2025'},
            {'Schedule_ID': 'S008', 'Flight_No': 'MA800', 'Date': '22/12/2025'},
            {'Schedule_ID': 'S009', 'Flight_No': 'MA801', 'Date': '24/12/2025'},
        ]

        for schedule_data in schedules_data:
            schedule = FlightSchedule.objects.create(
                date=self.parse_date(schedule_data['Date'])
            )
            schedules_map[schedule_data['Schedule_ID']] = schedule
            self.stdout.write(f'Created schedule: {schedule.date}')

        flights_map = {}
        flights_data = [
            {'Flight_No': 'MA800', 'Route_ID': 'R001', 'DepartureTime': '20:25' """ , 'ArrivalTime': '23:55' """},
            {'Flight_No': 'MA801', 'Route_ID': 'R002', 'DepartureTime': '00:45' """ , 'ArrivalTime': '04:00' """},
            {'Flight_No': 'MA443', 'Route_ID': 'R003', 'DepartureTime': '14:30' """ , 'ArrivalTime': '19:15' """},
            {'Flight_No': 'MA444', 'Route_ID': 'R004', 'DepartureTime': '08:30' """ , 'ArrivalTime': '13:00' """},
            {'Flight_No': 'MA652', 'Route_ID': 'R005', 'DepartureTime': '10:00' """ , 'ArrivalTime': '15:20' """},
            {'Flight_No': 'MA234', 'Route_ID': 'R006', 'DepartureTime': '09:15' """ , 'ArrivalTime': '23:30' """},
        ]

        flight_to_schedule = {}
        for schedule_data in schedules_data:
            flight_no = schedule_data['Flight_No']
            schedule_id = schedule_data['Schedule_ID']
            if flight_no not in flight_to_schedule:
                flight_to_schedule[flight_no] = schedule_id

        for flight_data in flights_data:
            route = routes_map[flight_data['Route_ID']]
            schedule_id = flight_to_schedule.get(flight_data['Flight_No'])
            schedule = schedules_map[schedule_id] if schedule_id else None
            departure_time = self.parse_time(flight_data['DepartureTime'])

            flight = Flight.objects.create(
                departure_time=departure_time,
                arrival_time=datetime.combine(schedule.date, departure_time) + timedelta(minutes=route.duration),
                schedule=schedule,
                route=route
            )
            flights_map[flight_data['Flight_No']] = flight
            self.stdout.write(f'Created flight: {flight.flight_no}')

        passengers_map = {}
        passengers_data = [
            {'Passenger_ID': 'P001', 'Name': 'Francisco, Carlito P.', 'Birthdate': '01/01/1960', 'Gender': 'Male'},
            {'Passenger_ID': 'P002', 'Name': 'Santos, Maria Elena', 'Birthdate': '15/03/1985', 'Gender': 'Female'},
            {'Passenger_ID': 'P003', 'Name': 'Lee, Benjamin', 'Birthdate': '22/07/1992', 'Gender': 'Male'},
            {'Passenger_ID': 'P004', 'Name': 'Reyes, Anna Marie', 'Birthdate': '10/05/1978', 'Gender': 'Female'},
        ]

        for passenger_data in passengers_data:
            name_parts = passenger_data['Name'].split(',')
            last_name = name_parts[0].strip()
            first_middle = name_parts[1].strip().split() if len(name_parts) > 1 else ['']
            first_name = first_middle[0] if first_middle else ''

            gender_map = {'Male': 'M', 'Female': 'F', 'Other': 'O'}
            gender = gender_map.get(passenger_data['Gender'], 'O')

            passenger = Passenger.objects.create(
                first_name=first_name,
                last_name=last_name,
                birthdate=self.parse_date(passenger_data['Birthdate']),
                gender=gender
            )
            passengers_map[passenger_data['Passenger_ID']] = passenger
            self.stdout.write(f'Created passenger: {passenger.last_name}, {passenger.first_name}')

        additional_items_map = {}
        additional_items_data = [
            {'Item_ID': 'AI001', 'Description': 'Additional baggage allowance (5 kg)', 'CostPerUnit': 237.00},
            {'Item_ID': 'AI002', 'Description': 'Terminal Fees', 'CostPerUnit': 273.00},
            {'Item_ID': 'AI003', 'Description': 'Travel Insurance', 'CostPerUnit': 208.00},
            {'Item_ID': 'AI004', 'Description': 'Priority Boarding', 'CostPerUnit': 150.00},
            {'Item_ID': 'AI005', 'Description': 'Lounge Access', 'CostPerUnit': 200.00},
        ]

        for item_data in additional_items_data:
            item = AdditionalItem.objects.create(
                description=item_data['Description'],
                cost_per_unit=Decimal(str(item_data['CostPerUnit']))
            )
            additional_items_map[item_data['Item_ID']] = item
            self.stdout.write(f'Created additional item: {item.description}')

        bookings_map = {}
        bookings_data = [
            {'Booking_ID': 'BK-2025-00123', 'Passenger_ID': 'P001', 'DateBooked': '15/12/2025', 'TotalCost': 7319.00},
            {'Booking_ID': 'BK-2025-00456', 'Passenger_ID': 'P002', 'DateBooked': '18/12/2025', 'TotalCost': 9850.00},
            {'Booking_ID': 'BK-2025-00789', 'Passenger_ID': 'P003', 'DateBooked': '20/12/2025', 'TotalCost': 5890.00},
        ]

        itinerary_items_data = [
            {'ItineraryItem_ID': 'IT001', 'Booking_ID': 'BK-2025-00123', 'Schedule_ID': 'S002', 'Cost': 2088.00},
            {'ItineraryItem_ID': 'IT002', 'Booking_ID': 'BK-2025-00123', 'Schedule_ID': 'S003', 'Cost': 4276.00},
            {'ItineraryItem_ID': 'IT003', 'Booking_ID': 'BK-2025-00456', 'Schedule_ID': 'S004', 'Cost': 5800.00},
            {'ItineraryItem_ID': 'IT004', 'Booking_ID': 'BK-2025-00456', 'Schedule_ID': 'S005', 'Cost': 3850.00},
            {'ItineraryItem_ID': 'IT005', 'Booking_ID': 'BK-2025-00789', 'Schedule_ID': 'S007', 'Cost': 5890.00},
        ]

        for booking_data in bookings_data:
            booking = Booking.objects.create(
                date_booked=self.parse_date(booking_data['DateBooked']),
                total_cost=Decimal(str(booking_data['TotalCost'])),
                passenger=passengers_map[booking_data['Passenger_ID']]
            )
            bookings_map[booking_data['Booking_ID']] = booking
            self.stdout.write(f'Created booking: {booking.booking_id}')

        schedule_to_flight = {}
        for schedule_data in schedules_data:
            schedule_id = schedule_data['Schedule_ID']
            flight_no = schedule_data['Flight_No']
            if flight_no in flights_map:
                schedule_to_flight[schedule_id] = flights_map[flight_no]

        for itinerary_data in itinerary_items_data:
            schedule_id = itinerary_data['Schedule_ID']
            flight = schedule_to_flight.get(schedule_id)
            if flight:
                ItineraryItem.objects.create(
                    booking=bookings_map[itinerary_data['Booking_ID']],
                    flight=flight,
                    cost=Decimal(str(itinerary_data['Cost']))
                )
                self.stdout.write(f'Created itinerary item for booking {itinerary_data["Booking_ID"]}')

        booking_items_data = [
            {'BookingItem_ID': 'BI001', 'Booking_ID': 'BK-2025-00123', 'Item_ID': 'AI001', 'Quantity': 2, 'SubtotalCost': 474.00},
            {'BookingItem_ID': 'BI002', 'Booking_ID': 'BK-2025-00123', 'Item_ID': 'AI002', 'Quantity': 1, 'SubtotalCost': 273.00},
            {'BookingItem_ID': 'BI003', 'Booking_ID': 'BK-2025-00123', 'Item_ID': 'AI003', 'Quantity': 1, 'SubtotalCost': 208.00},
            {'BookingItem_ID': 'BI004', 'Booking_ID': 'BK-2025-00456', 'Item_ID': 'AI004', 'Quantity': 1, 'SubtotalCost': 150.00},
            {'BookingItem_ID': 'BI005', 'Booking_ID': 'BK-2025-00456', 'Item_ID': 'AI005', 'Quantity': 1, 'SubtotalCost': 200.00},
        ]

        for booking_item_data in booking_items_data:
            BookingItem.objects.create(
                booking=bookings_map[booking_item_data['Booking_ID']],
                item=additional_items_map[booking_item_data['Item_ID']],
                quantity=booking_item_data['Quantity'],
                subtotal_cost=Decimal(str(booking_item_data['SubtotalCost']))
            )
            self.stdout.write(f'Created booking item for booking {booking_item_data["Booking_ID"]}')

        crew_members_map = {}
        crew_members_data = [
            {'Crew_ID': 'CR001', 'CrewName': 'Reyes, Peter', 'Role': 'Pilot'},
            {'Crew_ID': 'CR002', 'CrewName': 'Cruz, Jose', 'Role': 'First Officer'},
            {'Crew_ID': 'CR003', 'CrewName': 'Ramos, Maria', 'Role': 'Flight Attendant'},
            {'Crew_ID': 'CR004', 'CrewName': 'Santos, Ana', 'Role': 'Flight Attendant'},
            {'Crew_ID': 'CR005', 'CrewName': 'Garcia, Miguel', 'Role': 'Pilot'},
            {'Crew_ID': 'CR006', 'CrewName': 'Fernandez, Lisa', 'Role': 'First Officer'},
            {'Crew_ID': 'CR007', 'CrewName': 'Torres, Juan', 'Role': 'Flight Attendant'},
            {'Crew_ID': 'CR008', 'CrewName': 'Diaz, Carmen', 'Role': 'Flight Attendant'},
        ]

        for crew_data in crew_members_data:
            name_parts = crew_data['CrewName'].split(',')
            last_name = name_parts[0].strip()
            first_name = name_parts[1].strip() if len(name_parts) > 1 else ''

            crew = CrewMember.objects.create(
                first_name=first_name,
                last_name=last_name,
                role=crew_data['Role']
            )
            crew_members_map[crew_data['Crew_ID']] = crew
            self.stdout.write(f'Created crew member: {crew.first_name} {crew.last_name}')

        crew_assignments_data = [
            {'CrewAssignment_ID': 'CA001', 'Schedule_ID': 'S001', 'Crew_ID': 'CR001', 'AssignmentDate': '21/12/2025'},
            {'CrewAssignment_ID': 'CA002', 'Schedule_ID': 'S001', 'Crew_ID': 'CR002', 'AssignmentDate': '21/12/2025'},
            {'CrewAssignment_ID': 'CA003', 'Schedule_ID': 'S001', 'Crew_ID': 'CR003', 'AssignmentDate': '21/12/2025'},
            {'CrewAssignment_ID': 'CA004', 'Schedule_ID': 'S001', 'Crew_ID': 'CR004', 'AssignmentDate': '21/12/2025'},
            {'CrewAssignment_ID': 'CA005', 'Schedule_ID': 'S002', 'Crew_ID': 'CR001', 'AssignmentDate': '23/12/2025'},
            {'CrewAssignment_ID': 'CA006', 'Schedule_ID': 'S002', 'Crew_ID': 'CR002', 'AssignmentDate': '23/12/2025'},
            {'CrewAssignment_ID': 'CA007', 'Schedule_ID': 'S002', 'Crew_ID': 'CR003', 'AssignmentDate': '23/12/2025'},
            {'CrewAssignment_ID': 'CA008', 'Schedule_ID': 'S003', 'Crew_ID': 'CR005', 'AssignmentDate': '24/12/2025'},
            {'CrewAssignment_ID': 'CA009', 'Schedule_ID': 'S003', 'Crew_ID': 'CR006', 'AssignmentDate': '24/12/2025'},
            {'CrewAssignment_ID': 'CA010', 'Schedule_ID': 'S004', 'Crew_ID': 'CR001', 'AssignmentDate': '21/12/2025'},
        ]

        for assignment_data in crew_assignments_data:
            schedule_id = assignment_data['Schedule_ID']
            flight = schedule_to_flight.get(schedule_id)
            if flight:
                CrewAssignment.objects.create(
                    crew=crew_members_map[assignment_data['Crew_ID']],
                    flight=flight,
                    assignment_date=self.parse_date(assignment_data['AssignmentDate'])
                )
                self.stdout.write(f'Created crew assignment for flight {flight.flight_no}')

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence")
            cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('airline_city', 10)")
            cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('airline_flightroute', 6)")
            cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('airline_flightschedule', 9)")
            cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('airline_flight', 6)")
            cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('airline_passenger', 4)")
            cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('airline_additionalitem', 5)")
            cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('airline_booking', 3)")
            cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('airline_itineraryitem', 5)")
            cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('airline_bookingitem', 5)")
            cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('airline_crewmember', 8)")
            cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('airline_crewassignment', 10)")

        self.stdout.write(self.style.SUCCESS('\n✅ All mock data created successfully!'))
        self.stdout.write(self.style.SUCCESS('✅ Auto-increment sequences reset - IDs will start from 1 (R001, MA001, etc.)'))


