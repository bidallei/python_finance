#models.py

from django.db import models

class Deudor(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    deuda_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.nombre}"

class Deuda(models.Model):
    deudor = models.ForeignKey(Deudor, on_delete=models.CASCADE, related_name='deudas')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()

    def __str__(self):
        return f"{self.deudor.nombre} - ${self.monto:,.2f} MXN"

class EdicionDeuda(models.Model):
    deuda = models.ForeignKey(Deuda, on_delete=models.CASCADE, related_name='ediciones')
    nueva_deuda = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_edicion = models.DateField(auto_now_add=True)
    concepto = models.CharField(max_length=255)

    def __str__(self):
        return f"Edición de {self.deuda.deudor.nombre} - {self.nueva_deuda}"

class Pago(models.Model):
    deuda = models.ForeignKey(Deuda, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()

    def __str__(self):
        return f"Pago de {self.deuda.deudor.nombre} - {self.monto}"

class Gasto(models.Model):
    concepto = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()

    def __str__(self):
        return f"{self.concepto} - {self.monto}"