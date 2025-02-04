#models.py

from django.db import models

class Deudor(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    deuda_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def actualizar_deuda(self):
        """Recalcula la deuda actual sumando las últimas ediciones de cada deuda."""
        total = self.deudas.aggregate(total=models.Sum('ediciones__nueva_deuda'))['total']
        self.deuda_actual = total if total is not None else 0.0
        self.save()

    def __str__(self):
        return f"{self.nombre} - Deuda: ${self.deuda_actual:,.2f} MXN"

class Deuda(models.Model):
    deudor = models.ForeignKey(Deudor, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)  # Monto inicial de la deuda
    fecha = models.DateField()
    concepto = models.CharField(max_length=255, blank=True, null=True)

    def deuda_actual(self):
        """Calcula la deuda actual restando los pagos realizados."""
        pagos_realizados = self.pagos.aggregate(total=models.Sum('monto'))['total'] or 0
        return self.monto - pagos_realizados

    def __str__(self):
        return f"{self.deudor.nombre} - Deuda actual: ${self.deuda_actual():,.2f} MXN"

class EdicionDeuda(models.Model):
    deuda = models.ForeignKey(Deuda, on_delete=models.CASCADE, related_name='ediciones')
    fecha = models.DateField()
    deudor = models.ForeignKey(Deudor, on_delete=models.CASCADE)
    nueva_deuda = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_edicion = models.DateField(auto_now_add=True, editable=True)
    concepto = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        """Al guardar una edición, actualiza la deuda y el total del deudor."""
        super().save(*args, **kwargs)  
        self.deuda.monto = self.nueva_deuda  # Actualiza el monto en la deuda original
        self.deuda.save()
        self.deudor.actualizar_deuda()  # Actualiza la deuda total del deudor

    def __str__(self):
        return f"Edición de {self.deuda.deudor.nombre} - ${self.nueva_deuda:,.2f} MXN"

class Pago(models.Model):
    deuda = models.ForeignKey(Deuda, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()
    haber = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Nuevo campo

    def save(self, *args, **kwargs):
        """Al guardar un pago, se actualiza la deuda y se suma al Haber."""
        super().save(*args, **kwargs)  # Guarda el pago en la BD
        self.deuda.monto -= self.monto  # Reduce la deuda
        self.deuda.save()
        self.deuda.deudor.actualizar_deuda()  # Actualiza la deuda total del deudor

        # 💰 Se suma el pago al haber total de la empresa
        Empresa.actualizar_haber(self.monto)

    def __str__(self):
        return f"Pago de {self.deuda.deudor.nombre} - ${self.monto:,.2f} MXN"

class Empresa(models.Model):
    haber_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)

    @classmethod
    def actualizar_haber(cls, monto):
        """Suma el monto de un pago al haber total de la empresa."""
        empresa, _ = cls.objects.get_or_create(id=1)  # Obtiene o crea el registro único
        empresa.haber_total += monto
        empresa.save()

    def __str__(self):
        return f"Haber Total: {self.haber_total}"

class Gasto(models.Model):
    concepto = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)  # Relacionamos el gasto con la empresa

    def __str__(self):
        return f"{self.concepto} - {self.monto:,.2f} MXN"

    def save(self, *args, **kwargs):
        """Al guardar el gasto, actualizamos el haber de la empresa."""
        empresa = self.empresa
        empresa.actualizar_haber(-self.monto)  # Restamos el monto del haber de la empresa
        super().save(*args, **kwargs)  # Llamamos al método save() del modelo
