from django import forms
from .models import BusStop, Bus, Driver

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

class DriverForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    
    class Meta:
        model = Driver
        fields = ['bus']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bus'].queryset = Bus.objects.filter(driver__isnull=True)
        if self.instance.pk:  # If editing existing driver
            self.fields['username'].widget.attrs['readonly'] = True
            self.fields['password'].required = False
            # Include current bus in queryset
            if self.instance.bus:
                self.fields['bus'].queryset = self.fields['bus'].queryset | Bus.objects.filter(pk=self.instance.bus.pk)
