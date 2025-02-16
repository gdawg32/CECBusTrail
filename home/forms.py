from django import forms
from .models import BusStop, Bus

class BusStopForm(forms.ModelForm):
    class Meta:
        model = BusStop
        fields = ['name', 'latitude', 'longitude']

class BusForm(forms.ModelForm):
    stops = forms.ModelMultipleChoiceField(
        queryset=BusStop.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Bus
        fields = ['number_plate', 'route', 'capacity', 'stops']
