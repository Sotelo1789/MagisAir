from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.db.models import Avg, Count, Q, Sum
from django.http import Http404, HttpRequest, JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse

from .forms import (
    CrewAssignmentForm,
    FlightCreationForm,
    FlightRouteForm,
    PassengerForm
)

from .models import (
    AdditionalItem,
    Booking,
    BookingItem,
    City,
    CrewAssignment,
    Flight,
    FlightRoute,
    FlightSchedule,
    ItineraryItem,
    Passenger,
)

from datetime import datetime, timedelta
from decimal import Decimal
import json


def _format_duration(minutes):
    if not minutes:
        return "0m"

    hours, mins = divmod(int(minutes), 60)
    if hours:
        return f"{hours}h {mins:02}m"
    return f"{mins}m"


def _parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def _serialize_itinerary(items):
    payload = []
    for item in items:
        flight = item.flight
        route = flight.route
        schedule = flight.schedule
        payload.append(
            {
                "id": item.itinerary_item_id,
                "flight_no": flight.flight_no,
                "flight_no_formatted": f"MA{flight.flight_no:03d}",
                "origin": route.origin_city.city_name,
                "destination": route.destination_city.city_name,
                "date": schedule.date if schedule else None,
                "departure": flight.departure_time,
                "arrival": flight.arrival_time,
                "duration": _format_duration(route.duration),
                "cost": item.cost,
            }
        )
    return payload


def _get_flight_price(flight):
    item = (
        ItineraryItem.objects.filter(flight=flight).order_by(
            "-itinerary_item_id").first()
    )
    if item and item.cost is not None:
        return item.cost
    return Decimal("0.00")


def flight_routes_view(request: HttpRequest):
    search = request.GET.get("search", "").strip()

    base_queryset = (
        FlightRoute.objects.select_related("origin_city", "destination_city")
        .annotate(flight_total=Count("flight"))
        .order_by("route_id")
    )

    if search:
        route_id_match = None
        if search.upper().startswith('R'):
            try:
                route_num = int(search[1:])
                route_id_match = route_num
            except ValueError:
                pass

        if route_id_match:
            base_queryset = base_queryset.filter(route_id=route_id_match)
        else:
            base_queryset = base_queryset.filter(
                Q(origin_city__city_name__icontains=search)
                | Q(destination_city__city_name__icontains=search)
                | Q(route_id__icontains=search)
            )

    routes = [
        {
            "id": route.route_id,
            "id_formatted": f"R{route.route_id:03d}",
            "origin": route.origin_city.city_name,
            "destination": route.destination_city.city_name,
            "duration": _format_duration(route.duration),
            "raw_duration": route.duration,
            "flight_total": route.flight_total,
        }
        for route in base_queryset
    ]

    all_routes = FlightRoute.objects.all()
    avg_duration = all_routes.aggregate(
        value=Avg("duration")).get("value") or 0
    busiest_origin = (
        all_routes.values("origin_city__city_name")
        .annotate(total=Count("route_id"))
        .order_by("-total")
        .first()
    )

    context = {
        "page": "routes",
        "filters": {"search": search},
        "routes": routes,
        "stats": {
            "total_routes": all_routes.count(),
            "visible_routes": len(routes),
            "avg_duration": _format_duration(avg_duration),
            "busiest_origin": busiest_origin["origin_city__city_name"]
            if busiest_origin
            else "—",
        },
    }
    return render(request, "flight_routes.html", context)


def flight_route_create_view(request: HttpRequest):
    if request.method == "POST":
        form = FlightRouteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("airline:flight_routes")
    else:
        form = FlightRouteForm()

    context = {
        "page": "routes",
        "form": form,
        "cities": City.objects.order_by("city_name"),
    }
    return render(request, "flight_route_create.html", context)


def flight_schedules_view(request: HttpRequest):
    origin_id = request.GET.get("origin")
    destination_id = request.GET.get("destination")
    date_filter = _parse_date(request.GET.get("date"))

    flights = Flight.objects.select_related(
        "route__origin_city",
        "route__destination_city",
        "schedule",
    ).order_by("flight_no")

    if origin_id:
        flights = flights.filter(route__origin_city_id=origin_id)

    if destination_id:
        flights = flights.filter(route__destination_city_id=destination_id)

    if date_filter:
        flights = flights.filter(schedule__date=date_filter)

    schedules = [
        {
            "flight_no": flight.flight_no,
            "flight_no_formatted": f"MA{flight.flight_no:03d}",
            "origin": flight.route.origin_city.city_name,
            "destination": flight.route.destination_city.city_name,
            "date": flight.schedule.date if flight.schedule else None,
            "departure": flight.departure_time,
            "arrival": flight.arrival_time,
            "duration": _format_duration(flight.route.duration),
        }
        for flight in flights
    ]

    upcoming = flights.filter(
        schedule__date__gte=timezone.now().date()).count()

    cities = City.objects.order_by("city_name")

    context = {
        "page": "schedules",
        "filters": {
            "origin": origin_id or "",
            "destination": destination_id or "",
            "date": date_filter.isoformat() if date_filter else "",
        },
        "cities": cities,
        "schedules": schedules,
        "stats": {
            "total_flights": flights.count(),
            "upcoming": upcoming,
        },
    }
    return render(request, "flight_schedules.html", context)


def flight_schedule_create_view(request: HttpRequest):
    if request.method == "POST":
        form = FlightCreationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            schedule, _ = FlightSchedule.objects.get_or_create(
                date=data["schedule_date"])
            Flight.objects.create(
                arrival_time=data["arrival_time"],
                departure_time=data["departure_time"],
                schedule=schedule,
                route=data["route"],
            )
            return redirect("airline:flight_schedules")
    else:
        form = FlightCreationForm()

    context = {
        "page": "schedules",
        "form": form,
    }
    return render(request, "flight_schedule_create.html", context)


def booking_create(request: HttpRequest):
    # Creating a new Booking
    if request.method == "POST" and "select_flight" in request.POST:
        flight_id = request.POST.get("flight_id")
        flight_type = request.POST.get("flight_type", "outbound")

        if flight_id:
            flight = get_object_or_404(Flight, flight_no=flight_id)
            price = _get_flight_price(flight)

            if "booking_session" not in request.session:
                request.session["booking_session"] = {
                    "flights": [],
                    "search_data": {}
                }

            if "trip_type" in request.POST:
                request.session["booking_session"]["search_data"] = {
                    "trip_type": request.POST.get("trip_type"),
                    "origin": request.POST.get("origin"),
                    "destination": request.POST.get("destination"),
                    "departure_date": request.POST.get("departure_date"),
                    "return_date": request.POST.get("return_date"),
                }

            flight_data = {
                "flight_id": flight.flight_no,
                "flight_type": flight_type,
                "price": float(price),
                "route_id": flight.route.route_id,
                "schedule_id": flight.schedule.schedule_id if flight.schedule else None,
            }

            print(request.GET.get('trip_type'))
            request.session["booking_session"]["flights"].append(flight_data)
            request.session.modified = True

            return redirect("airline:booking_details")

    # `GET` request - show flight search form
    trip_type = request.GET.get("trip_type", "one_way")
    origin_id = request.GET.get("origin")
    destination_id = request.GET.get("destination")
    passenger_count = request.GET.get("passengers", "1")
    departure_date = _parse_date(request.GET.get("departure_date"))
    return_date = _parse_date(request.GET.get("return_date"))

    try:
        passenger_count = max(1, int(passenger_count))
    except (TypeError, ValueError):
        passenger_count = 1

    base_queryset = Flight.objects.select_related(
        "route__origin_city", "route__destination_city", "schedule"
    ).order_by("schedule__date", "departure_time")

    def _build_results(queryset):
        return [
            {
                "id": flight.flight_no,
                "id_formatted": f"MA{flight.flight_no:03d}",
                "origin": flight.route.origin_city.city_name,
                "destination": flight.route.destination_city.city_name,
                "date": flight.schedule.date if flight.schedule else None,
                "departure": flight.departure_time,
                "arrival": flight.arrival_time,
                "duration": _format_duration(flight.route.duration),
                "price": _get_flight_price(flight),
            }
            for flight in queryset
        ]

    outbound_results = []
    return_results = []

    if request.GET:
        outbound_queryset = base_queryset
        if origin_id:
            outbound_queryset = outbound_queryset.filter(
                route__origin_city_id=origin_id)
        if destination_id:
            outbound_queryset = outbound_queryset.filter(
                route__destination_city_id=destination_id
            )
        if departure_date:
            outbound_queryset = outbound_queryset.filter(
                schedule__date=departure_date)

        outbound_results = _build_results(outbound_queryset)

        if trip_type == "round_trip" and origin_id and destination_id:
            return_queryset = base_queryset.filter(
                route__origin_city_id=destination_id,
                route__destination_city_id=origin_id,
            )
            if return_date:
                return_queryset = return_queryset.filter(
                    schedule__date=return_date)
            return_results = _build_results(return_queryset)

    search_performed = bool(request.GET)

    context = {
        "page": "bookings",
        "passengers": Passenger.objects.order_by("last_name", "first_name"),
        "cities": City.objects.order_by("city_name"),
        "outbound_results": outbound_results,
        "return_results": return_results,
        "search_performed": search_performed,
        "filters": {
            "trip_type": trip_type,
            "origin": origin_id or "",
            "destination": destination_id or "",
            "departure_date": departure_date.isoformat() if departure_date else "",
            "return_date": return_date.isoformat() if return_date else "",
            "passengers": passenger_count,
        },
        "passenger_count": passenger_count,
    }
    return render(request, "booking_create.html", context)


def booking_details(request: HttpRequest):
    booking_id = request.GET.get("booking_id")
    is_edit_mode = bool(booking_id)

    if request.method == "POST" and ("confirm_booking" in request.POST or "update_booking" in request.POST):
        booking_session = request.session.get("booking_session", {})
        flights = booking_session.get("flights", [])

        if not flights:
            return redirect("airline:booking_create")

        passenger_id = request.POST.get("passenger_id")
        if not passenger_id:
            messages.error(
                request, "Please select a passenger before confirming the booking.")
            return redirect("airline:booking_details")

        passenger = get_object_or_404(Passenger, passenger_id=passenger_id)

        flights_cost = sum(Decimal(str(f.get("price", 0))) for f in flights)

        baggage_count = int(request.POST.get("baggage_count", 0))
        has_insurance = request.POST.get("has_insurance") == "on"

        additional_cost = Decimal("0.00")
        if baggage_count > 0:
            additional_cost += Decimal("237.00") * baggage_count
        if has_insurance:
            additional_cost += Decimal("208.00")

        total_cost = flights_cost + additional_cost

        booking = Booking.objects.create(
            date_booked=timezone.now().date(),
            total_cost=total_cost,
            passenger=passenger,
        )

        for flight_data in flights:
            flight = get_object_or_404(
                Flight, flight_no=flight_data["flight_id"])
            ItineraryItem.objects.create(
                booking=booking,
                flight=flight,
                cost=Decimal(str(flight_data["price"])),
            )

        if baggage_count > 0:
            baggage_item, _ = AdditionalItem.objects.get_or_create(
                description="Additional Baggage Allowance (5kg)",
                defaults={"cost_per_unit": Decimal("237.00")}
            )
            BookingItem.objects.create(
                booking=booking,
                item=baggage_item,
                quantity=baggage_count,
                subtotal_cost=Decimal("237.00") * baggage_count,
            )

        if has_insurance:
            insurance_item, _ = AdditionalItem.objects.get_or_create(
                description="Travel Insurance",
                defaults={"cost_per_unit": Decimal("208.00")}
            )
            BookingItem.objects.create(
                booking=booking,
                item=insurance_item,
                quantity=1,
                subtotal_cost=Decimal("208.00"),
            )

        request.session.pop("booking_session", None)
        request.session["booking_created"] = True
        return redirect("airline:success_view")

    if request.GET.get("add_flight") == "1":
        booking_session = request.session.get("booking_session", {})
        search_data = booking_session.get("search_data", {})
        params = []
        if search_data.get("trip_type"):
            params.append(f"trip_type={search_data['trip_type']}")
        if search_data.get("origin"):
            params.append(f"origin={search_data['origin']}")
        if search_data.get("destination"):
            params.append(f"destination={search_data['destination']}")
        if search_data.get("departure_date"):
            params.append(f"departure_date={search_data['departure_date']}")
        if search_data.get("return_date"):
            params.append(f"return_date={search_data['return_date']}")
        if search_data.get("passengers"):
            params.append(f"passengers={search_data['passengers']}")

        url = reverse("airline:booking_create")
        if params:
            url += "?" + "&".join(params)
        return redirect(url)

    booking_session = request.session.get("booking_session", {})
    flights = booking_session.get("flights", [])
    search_data = booking_session.get("search_data", {})

    if not flights:
        return redirect("airline:booking_create")

    flight_details = []
    for flight_data in flights:
        try:
            flight = Flight.objects.select_related(
                "route__origin_city", "route__destination_city", "schedule"
            ).get(flight_no=flight_data["flight_id"])

            flight_details.append({
                "flight_id": flight.flight_no,
                "flight_type": flight_data.get("flight_type", "outbound"),
                "flight_no": flight.flight_no,
                "flight_no_formatted": f"MA{flight.flight_no:03d}",
                "origin": flight.route.origin_city.city_name,
                "destination": flight.route.destination_city.city_name,
                "departure_time": flight.departure_time,
                "arrival_time": flight.arrival_time,
                "duration": _format_duration(flight.route.duration),
                "date": flight.schedule.date if flight.schedule else None,
                "price": flight_data.get("price", 0),
            })
        except Flight.DoesNotExist:
            continue

    flights_cost = sum(Decimal(str(f.get("price", 0))) for f in flights)

    passengers = Passenger.objects.order_by("last_name", "first_name")

    additional_items = AdditionalItem.objects.all()

    selected_passenger_id = None
    initial_baggage = 0
    initial_insurance = False

    if is_edit_mode and booking_id:
        booking = get_object_or_404(Booking, booking_id=booking_id)
        selected_passenger_id = booking.passenger.passenger_id

        booking_items = BookingItem.objects.filter(
            booking=booking).select_related("item")
        for item in booking_items:
            if "baggage" in item.item.description.lower():
                initial_baggage = item.quantity
            elif "insurance" in item.item.description.lower():
                initial_insurance = True

    context = {
        "page": "bookings",
        "flights": flight_details,
        "search_data": search_data,
        "passengers": passengers,
        "additional_items": additional_items,
        "flights_cost": flights_cost,
        "baggage_price": Decimal("237.00"),
        "insurance_price": Decimal("208.00"),
        "is_edit_mode": is_edit_mode,
        "booking_id": booking_id,
        "selected_passenger_id": selected_passenger_id,
        "initial_baggage": initial_baggage,
        "initial_insurance": initial_insurance,
    }

    return render(request, "booking_details.html", context)


def booking_edit(request: HttpRequest, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id)

    booking_session = {
        "flights": [],
        "search_data": {}
    }

    itinerary_items = ItineraryItem.objects.filter(booking=booking).select_related(
        "flight__route__origin_city", "flight__route__destination_city", "flight__schedule")

    for item in itinerary_items:
        booking_session["flights"].append({
            "flight_id": item.flight.flight_no,
            "flight_type": "existing",
            "price": float(item.cost),
            "route_id": item.flight.route.route_id,
            "schedule_id": item.flight.schedule.schedule_id if item.flight.schedule else None,
        })

    request.session["booking_session"] = booking_session
    request.session.modified = True

    return redirect(f"{reverse('airline:booking_details')}?booking_id={booking_id}")


@require_POST
def booking_delete(request: HttpRequest, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id)
    booking.delete()
    messages.success(request, "Booking deleted successfully!")
    return redirect("airline:booking_list")


def success_view(request: HttpRequest):
    if not request.session.pop('booking_created', False):
        return redirect('airline:booking_list')

    return render(request, 'success.html')


def passenger_list_view(request: HttpRequest):
    search = request.GET.get("search", "").strip()
    gender = request.GET.get("gender", "").strip().upper()
    selected_id = request.GET.get("selected")

    passengers = Passenger.objects.all()

    if search:
        passengers = passengers.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(passenger_id__icontains=search)
        )

    if gender in dict(Passenger.gender_choices):
        passengers = passengers.filter(gender=gender)

    passengers = passengers.order_by("last_name", "first_name")

    selected_passenger = None
    if selected_id:
        selected_passenger = passengers.filter(
            passenger_id=selected_id).first()

    if not selected_passenger:
        selected_passenger = passengers.first()

    booking_history = []
    if selected_passenger:
        bookings = (
            Booking.objects.filter(passenger=selected_passenger)
            .prefetch_related(
                "itineraryitem_set__flight__route__origin_city",
                "itineraryitem_set__flight__route__destination_city",
                "itineraryitem_set__flight__schedule",
            )
            .order_by("-date_booked")
        )

        booking_history = [
            {
                "id": booking.booking_id,
                "booking_reference": booking.booking_reference,
                "date": booking.date_booked,
                "total": booking.total_cost,
                "itinerary": _serialize_itinerary(booking.itineraryitem_set.all()),
            }
            for booking in bookings
        ]

    context = {
        "page": "passengers",
        "filters": {"search": search, "gender": gender},
        "passengers": passengers,
        "selected_passenger": selected_passenger,
        "booking_history": booking_history,
        "summary": {
            "total": Passenger.objects.count(),
            "filtered": passengers.count(),
        },
    }
    return render(request, "passenger_list.html", context)


def passenger_create_view(request: HttpRequest):
    if request.method == "POST":
        form = PassengerForm(request.POST)
        if form.is_valid():
            passenger = form.save()
            return redirect(
                f"{reverse('airline:passenger_list')}?selected={passenger.passenger_id}"
            )
    else:
        form = PassengerForm()

    context = {
        "page": "passengers",
        "form": form,
    }
    return render(request, "passenger_create.html", context)


def booking_list_view(request: HttpRequest):
    search = request.GET.get("search", "").strip()
    date_filter = _parse_date(request.GET.get("date"))
    cancel = bool(request.GET.get("cancel"))

    if cancel:
        if request.session["booking_session"]["flights"]:
            request.session["booking_session"]["flights"] = []
            request.session.modified = True
        return redirect("airline:booking_list")

    bookings = Booking.objects.select_related("passenger").prefetch_related(
        "itineraryitem_set__flight__route__origin_city",
        "itineraryitem_set__flight__route__destination_city",
        "itineraryitem_set__flight__schedule",
    )

    if search:
        bookings = bookings.filter(
            Q(booking_id__icontains=search)
            | Q(passenger__first_name__icontains=search)
            | Q(passenger__last_name__icontains=search)
        )

    if date_filter:
        bookings = bookings.filter(date_booked=date_filter)

    bookings = bookings.order_by("-date_booked", "-booking_id")

    booking_rows = []
    for booking in bookings:
        itinerary = _serialize_itinerary(booking.itineraryitem_set.all())
        booking_items = booking.bookingitem_set.select_related("item").all()
        additional_items = [
            {
                "id": item.booking_item_id,
                "description": item.item.description if item.item else "Additional service",
                "quantity": item.quantity,
                "subtotal": item.subtotal_cost or Decimal("0.00"),
            }
            for item in booking_items
        ]
        flights_total = sum((leg.get("cost") or Decimal("0.00"))
                            for leg in itinerary)
        additional_total = sum(
            (entry["subtotal"] for entry in additional_items), Decimal("0.00"))
        price_summary = {
            "flights": flights_total,
            "additional": additional_total,
            "total": booking.total_cost or (flights_total + additional_total),
        }
        booking_rows.append(
            {
                "booking": booking,
                "itinerary": itinerary,
                "additional_items": additional_items,
                "price_summary": price_summary,
            }
        )

    totals = bookings.aggregate(
        count=Count("booking_id"), revenue=Sum("total_cost")
    )

    context = {
        "page": "bookings",
        "filters": {
            "search": search,
            "date": date_filter.isoformat() if date_filter else "",
        },
        "bookings": booking_rows,
        "summary": {
            "count": totals.get("count") or 0,
            "revenue": totals.get("revenue") or Decimal("0.00"),
            "average": (
                (totals.get("revenue") or Decimal("0.00"))
                / totals.get("count")
                if totals.get("count")
                else Decimal("0.00")
            ),
        },
    }
    return render(request, "booking_list.html", context)


def page_temp(request: HttpRequest):
    raise Http404('Temporarily Unavailable --- To Be Created')


def crew_assignments_view(request: HttpRequest):
    search = request.GET.get("search", "").strip()
    role = request.GET.get("role", "").strip()
    date_filter = _parse_date(request.GET.get("date"))

    assignments = CrewAssignment.objects.select_related(
        "crew",
        "flight__route__origin_city",
        "flight__route__destination_city",
        "flight__schedule",
    ).order_by("-assignment_date")

    if search:
        assignments = assignments.filter(
            Q(crew__first_name__icontains=search)
            | Q(crew__last_name__icontains=search)
            | Q(flight__flight_no__icontains=search)
        )

    if role:
        assignments = assignments.filter(crew__role__iexact=role)

    if date_filter:
        assignments = assignments.filter(assignment_date=date_filter)

    assignment_rows = [
        {
            "id": assignment.crew_assignment_id,
            "crew_name": f"{assignment.crew.first_name} {assignment.crew.last_name}",
            "role": assignment.crew.role,
            "flight_no": assignment.flight.flight_no,
            "flight_no_formatted": f"MA{assignment.flight.flight_no:03d}",
            "origin": assignment.flight.route.origin_city.city_name,
            "destination": assignment.flight.route.destination_city.city_name,
            "date": assignment.assignment_date,
            "departure": assignment.flight.departure_time,
            "arrival": assignment.flight.arrival_time,
        }
        for assignment in assignments
    ]

    roles = (
        CrewAssignment.objects.select_related("crew")
        .values_list("crew__role", flat=True)
        .order_by("crew__role")
        .distinct()
    )

    context = {
        "page": "crew",
        "filters": {
            "search": search,
            "role": role,
            "date": date_filter.isoformat() if date_filter else "",
        },
        "assignments": assignment_rows,
        "roles": roles,
        "summary": {
            "total": assignments.count(),
            "unique_crew": assignments.values("crew_id").distinct().count(),
        },
    }
    return render(request, "crew_assignments.html", context)


def crew_assignment_create_view(request: HttpRequest):
    if request.method == "POST":
        form = CrewAssignmentForm(request.POST)
        print(form.is_valid())
        if form.is_valid():
            form.save()
            return redirect("airline:crew_assignments")
    else:
        form = CrewAssignmentForm()

    context = {
        "page": "crew",
        "form": form,
    }
    return render(request, "crew_assignment_create.html", context)


@require_POST
def get_arrival_time(request: HttpRequest):
    body = json.loads(request.body)
    route_id = body.get("route")
    departure_time_str = body.get("departure_time")

    try:
        route = FlightRoute.objects.get(route_id=route_id)
        print(route)

        departure_time = datetime.strptime(departure_time_str, "%H:%M")
        print(departure_time)
        total_minutes = route.duration
        print(route.duration)

        arrival_datetime = departure_time + timedelta(minutes=total_minutes)
        print(arrival_datetime)
        arrival_time = arrival_datetime.time()

        return JsonResponse({"arrival_time": arrival_time.strftime("%H:%M")})
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid input"}, status=400)
