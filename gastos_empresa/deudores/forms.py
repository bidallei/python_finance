# forms.py

from django import forms
from .models import Gasto, Pago, Deudor, Deuda, EdicionDeuda

class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ['concepto', 'monto', 'fecha']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['deuda', 'monto', 'fecha']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'deuda': forms.Select(attrs={'class': 'form-control'}),
        }

class DeudorForm(forms.ModelForm):
    class Meta:
        model = Deudor
        fields = ['nombre', 'deuda_total']
        error_messages = {
            'nombre': {
                'unique': "Este nombre ya está registrado.",
            },
            'deuda_total': {
                'invalid': "La deuda total debe ser un número positivo.",
            },
        }

class DeudaForm(forms.ModelForm):
    deudor = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Deuda
        fields = ['deudor', 'monto', 'fecha']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_deudor(self):
        nombre = self.cleaned_data['deudor']
        deudor, creado = Deudor.objects.get_or_create(nombre=nombre)
        return deudor

class EditarDeudaForm(forms.ModelForm):
    deuda = forms.ModelChoiceField(
        queryset=Deuda.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Deuda",
        empty_label="Seleccione una deuda"
    )

    class Meta:
        model = EdicionDeuda
        fields = ['deuda', 'nueva_deuda', 'concepto']
        widgets = {
            'nueva_deuda': forms.NumberInput(attrs={'class': 'form-control'}),
            'concepto': forms.TextInput(attrs={'class': 'form-control'}),
        }