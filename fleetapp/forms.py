from django import forms
from .models import InspectionRequest,Vehicle

class InspectionRequestForm(forms.ModelForm):
    class Meta:
        model = InspectionRequest
        fields = ['title', 'manager', 'inspection_type', 'status', 'vehicle', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Works only for ForeignKey / ModelChoiceField
        self.fields['inspection_type'].empty_label = "Select Inspection Type"
        self.fields['vehicle'].empty_label = "Select Vehicle"

        # Works for CharField choices (like 'manager')
        self.fields['manager'].choices = [("", "Select Inspection Manager")] + list(self.fields['manager'].choices)


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = '__all__'
        widgets = {
            'insurance_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'insurance_expiry': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'roadtax_last': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'permit_last': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'puc_last': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reg_from': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reg_to': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fitness_end': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }