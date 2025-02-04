# forms.py

from django import forms
from .models import Deudor, Deuda, EdicionDeuda, Pago, Gasto

class DeudorForm(forms.ModelForm):
    class Meta:
        model = Deudor
        fields = ['nombre', 'deuda_actual']
        error_messages = {
            'nombre': {
                'unique': "Este nombre ya está registrado.",
            },
            'deuda_actual': {
                'invalid': "La deuda total debe ser un número positivo.",
            },
        }

class DeudaForm(forms.ModelForm):
    deudor = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Nombre del Deudor"
    )

    class Meta:
        model = Deuda
        fields = ['deudor', 'monto', 'fecha']
        widgets = {
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario con la deuda actual del deudor seleccionado."""
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['deuda_actual'].initial = self.instance.deudor.deuda_actual

    def clean_deudor(self):
        """Asegura que el deudor seleccionado exista en la base de datos."""
        deudor = self.cleaned_data.get('deudor')
        if not deudor:
            raise forms.ValidationError("Debe seleccionar un deudor válido.")

        # Busca o crea el deudor con el nombre ingresado
        deudor, created = Deudor.objects.get_or_create(nombre=deudor)

        return deudor

class EditarDeudaForm(forms.ModelForm):
    class Meta:
        model = EdicionDeuda
        fields = ['deudor', 'nueva_deuda', 'fecha_edicion', 'concepto']
        widgets = {
            'deudor': forms.Select(attrs={'class': 'form-control', 'id': 'id_deudor'}),
            'fecha_edicion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nueva_deuda': forms.NumberInput(attrs={'class': 'form-control'}),
            'concepto': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['deuda', 'monto', 'fecha']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'deuda': forms.Select(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ['concepto', 'monto', 'fecha']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
        }

