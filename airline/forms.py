from django import forms

from .models import (
    City,
    CrewAssignment,
    CrewMember,
    Flight,
    FlightRoute,
    FlightSchedule,
    Passenger,
)


class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger
        fields = ["first_name", "last_name", "birthdate", "gender"]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last name"}),
            "birthdate": forms.DateInput(
                attrs={"type": "date", "placeholder": "Birthdate"}
            ),
            "gender": forms.Select(),
        }


class FlightRouteForm(forms.ModelForm):
    origin_city_name = forms.CharField(label="Origin City", max_length=100)
    destination_city_name = forms.CharField(label="Destination City", max_length=100)

    class Meta:
        model = FlightRoute
        fields = ["origin_city", "destination_city", "duration"]
        widgets = {
            "duration": forms.NumberInput(
                attrs={"min": 0, "placeholder": "Duration in minutes"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["origin_city"].required = False
        self.fields["origin_city"].widget = forms.HiddenInput()
        self.fields["destination_city"].required = False
        self.fields["destination_city"].widget = forms.HiddenInput()
        self.fields["origin_city_name"].widget.attrs["placeholder"] = "e.g. Manila"
        self.fields["destination_city_name"].widget.attrs["placeholder"] = "e.g. Singapore"
        self.fields["origin_city_name"].widget.attrs["list"] = "city-options"
        self.fields["destination_city_name"].widget.attrs["list"] = "city-options"

    def _resolve_city(self, name):
        if not name:
            return None
        normalized = name.strip()
        if not normalized:
            return None
        city = City.objects.filter(city_name__iexact=normalized).first()
        if not city:
            city = City.objects.create(city_name=normalized)
        return city

    def clean(self):
        cleaned = super().clean()
        origin_city = self._resolve_city(cleaned.get("origin_city_name"))
        destination_city = self._resolve_city(cleaned.get("destination_city_name"))

        if not origin_city:
            self.add_error("origin_city_name", "Please enter an origin city.")
        if not destination_city:
            self.add_error("destination_city_name", "Please enter a destination city.")
        if origin_city and destination_city and origin_city == destination_city:
            self.add_error(
                "destination_city_name", "Destination must be different from origin."
            )

        cleaned["origin_city"] = origin_city
        cleaned["destination_city"] = destination_city
        return cleaned


class FlightCreationForm(forms.Form):
    route = forms.ModelChoiceField(
        queryset=FlightRoute.objects.select_related(
            "origin_city", "destination_city"
        ).order_by("origin_city__city_name", "destination_city__city_name"),
        label="Route",
    )
    schedule_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), label="Flight Date"
    )
    departure_time = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time"}), label="Departure Time"
    )
    arrival_time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={"type": "time", "readonly": "readonly"}),
        label="Arrival Time"
    )

    def clean(self):
        cleaned = super().clean()
        departure = cleaned.get("departure_time")
        arrival = cleaned.get("arrival_time")
        if departure and arrival and arrival <= departure:
            self.add_error(
                "arrival_time", "Arrival time must be later than departure time."
            )
        return cleaned


class CrewAssignmentForm(forms.ModelForm):
    crew = forms.ModelChoiceField(
        queryset=CrewMember.objects.order_by("first_name", "last_name"),
        required=False,
        label="Existing Crew Member",
    )
    new_crew_first_name = forms.CharField(
        required=False,
        label="First Name",
        widget=forms.TextInput(attrs={"placeholder": "e.g. Alex"})
    )
    new_crew_last_name = forms.CharField(
        required=False,
        label="Last Name",
        widget=forms.TextInput(attrs={"placeholder": "e.g. Santos"})
    )
    new_crew_role = forms.CharField(
        required=False,
        label="Role",
        widget=forms.TextInput(attrs={"placeholder": "e.g. Captain"})
    )

    class Meta:
        model = CrewAssignment
        fields = ["crew", "flight", "assignment_date"]
        widgets = {
            "assignment_date": forms.DateInput(attrs={"type": "date"}),
        }

    flight = forms.ModelChoiceField(
        queryset=Flight.objects.select_related(
            "route__origin_city", "route__destination_city", "schedule"
        ).order_by("schedule__date", "departure_time"),
        label="Flight",
    )

    def clean(self):
        cleaned = super().clean()
        crew = cleaned.get("crew")
        first = cleaned.get("new_crew_first_name")
        last = cleaned.get("new_crew_last_name")
        role = cleaned.get("new_crew_role")
        print(role)

        if not crew:
            if not (first and last and role):
                raise forms.ValidationError(
                    "Select an existing crew member or provide details for a new one."
                )
            crew = CrewMember.objects.create(
                first_name=first.strip(),
                last_name=last.strip(),
                role=role.strip(),
            )
            cleaned["crew"] = crew
        return cleaned

