from django import forms
from .models import Passenger, Flight, FlightRoute, City 


class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger
        # We exclude passenger_id because we will generate it automatically
        fields = ['first_name', 'last_name', 'birthdate', 'gender']
        
        # Add Bootstrap styling to the inputs
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Juan'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Dela Cruz'}),
            'birthdate': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
        }

class FlightForm(forms.ModelForm):
    # Add a simpler date field that isn't tied to the database yet
    schedule_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    class Meta:
        model = Flight
        # Remove 'schedule' from here, we will handle it manually
        fields = ['route', 'departure_time', 'arrival_time'] 
        
        widgets = {
            'route': forms.Select(attrs={'class': 'form-select'}),
            'departure_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'arrival_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

class FlightRouteForm(forms.ModelForm):
    class Meta:
        model = FlightRoute
        fields = ['origin_city', 'destination_city', 'duration']
        
        widgets = {
            'origin_city': forms.Select(attrs={'class': 'form-select'}),
            'destination_city': forms.Select(attrs={'class': 'form-select'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minutes (e.g. 90)'}),
        }

class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ['city_name'] # We will auto-generate ID
        
        widgets = {
            'city_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Tokyo'}),
        }