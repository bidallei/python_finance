# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Deuda, Pago, Gasto, Deudor, EdicionDeuda
from .forms import DeudaForm, EditarDeudaForm, PagoForm, GastoForm
import pandas as pd
from django.http import HttpResponse
from django.utils.timezone import now

def inicio(request):
    return render(request, 'deudores/inicio.html')

def registrar_deuda(request):
    if request.method == 'POST':
        form = DeudaForm(request.POST)
        if form.is_valid():
            deuda = form.save(commit=False)
            nombre_deudor = form.cleaned_data['deudor']  # Obtiene el nombre del deudor

            # Buscar o crear el deudor en la base de datos
            deudor, created = Deudor.objects.get_or_create(nombre=nombre_deudor)

            deuda.deudor = deudor  # Asigna la instancia de Deudor
            deuda.save()

            messages.success(request, "Deuda registrada correctamente.")
            return redirect('registrar_deuda')
        else:
            messages.error(request, "Hubo un error al registrar la deuda.")
    else:
        form = DeudaForm()
    
    return render(request, 'deudores/registrar_deuda.html', {'form': form})


def editar_deuda(request, deuda_id):
    deuda = get_object_or_404(Deuda, id=deuda_id)
    
    if request.method == 'POST':
        form = EditarDeudaForm(request.POST)
        if form.is_valid():
            # Guardar los cambios en la deuda
            nueva_deuda = form.cleaned_data['nueva_deuda']
            deuda.monto = nueva_deuda
            deuda.fecha = form.cleaned_data['fecha']
            deuda.concepto = form.cleaned_data['concepto']
            deuda.save()
            
            # Actualizar la deuda total del deudor (si es necesario)
            # Por ejemplo, si el deudor tiene un saldo total de deudas
            deudor = deuda.deudor
            # Aquí puedes añadir lógica para actualizar el saldo del deudor si es necesario
            
            messages.success(request, "Deuda editada correctamente.")
            return redirect('consulta')
        else:
            messages.error(request, "Hubo un error al editar la deuda.")
    else:
        # Mostrar el formulario con los datos actuales de la deuda
        form = EditarDeudaForm(initial={
            'nueva_deuda': deuda.monto,
            'fecha': deuda.fecha,
            'deudor': deuda.deudor,
            'concepto': deuda.concepto,
        })
    
    return render(request, 'deudores/editar_deuda.html', {'form': form, 'deuda': deuda})

def registrar_pago(request):
    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Pago registrado correctamente.")
            return redirect('consulta')
        else:
            messages.error(request, "Hubo un error al registrar el pago.")
    else:
        form = PagoForm()
    
    return render(request, 'deudores/registrar_pago.html', {'form': form})

def registrar_gasto(request):
    if request.method == 'POST':
        form = GastoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Gasto registrado correctamente.")
            return redirect('consulta')
        else:
            messages.error(request, "Hubo un error al registrar el gasto.")
    else:
        form = GastoForm()
    
    return render(request, 'deudores/registrar_gasto.html', {'form': form})

def consulta(request):
    deudores = Deuda.objects.values_list('deudor__nombre', flat=True).distinct()
    
    if request.method == 'POST':
        tipo_consulta = request.POST.get('tipo_consulta')
        
        if tipo_consulta == 'individual':
            deudor_nombre = request.POST.get('deudor')
            deudas = Deuda.objects.filter(deudor__nombre=deudor_nombre)
            data = list(deudas.values('deudor__nombre', 'monto', 'fecha'))
            filename = f"consulta_individual_{deudor_nombre}.xlsx"
        else:
            deudas = Deuda.objects.all()
            pagos = Pago.objects.all()
            gastos = Gasto.objects.all()
            
            data = list(deudas.values('deudor__nombre', 'monto', 'fecha')) + \
                   list(pagos.values('deuda__deudor__nombre', 'monto', 'fecha')) + \
                   list(gastos.values('concepto', 'monto', 'fecha'))
            filename = "consulta_general.xlsx"
        
        # Crear un DataFrame con los datos
        df = pd.DataFrame(data)
        
        # Crear la respuesta HTTP con el archivo Excel
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        df.to_excel(response, index=False)
        return response
    
    return render(request, 'deudores/consulta.html', {'deudores': deudores})
