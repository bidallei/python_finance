# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Deuda, Pago, Gasto, Deudor, EdicionDeuda
from .forms import DeudaForm, EditarDeudaForm, PagoForm, GastoForm
import pandas as pd
from django.http import HttpResponse
from django.utils import timezone

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

# def editar_deuda(request, deuda_id):
#     deuda = get_object_or_404(Deuda, id=deuda_id)
    
#     if request.method == 'POST':
#         form = EditarDeudaForm(request.POST)
#         if form.is_valid():
#             # Guardar los cambios en la deuda
#             nueva_deuda = form.cleaned_data['nueva_deuda']
#             deuda.monto = nueva_deuda
#             deuda.fecha = form.cleaned_data['fecha_edicion']
#             deuda.concepto = form.cleaned_data['concepto']
#             deuda.save()
            
#             # Actualizar la deuda total del deudor (si es necesario)
#             # Por ejemplo, si el deudor tiene un saldo total de deudas
#             deudor = deuda.deudor
#             # Aquí puedes añadir lógica para actualizar el saldo del deudor si es necesario
#             deudor.actualizar_deuda()

#             messages.success(request, "Deuda editada correctamente.")
#             return redirect('consulta')
#         else:
#             messages.error(request, "Hubo un error al editar la deuda.")
#     else:
#         # Mostrar el formulario con los datos actuales de la deuda
#         form = EditarDeudaForm(initial={
#             'nueva_deuda': deuda.monto,
#             'fecha_edicion': deuda.fecha,
#             'deudor': deuda.deudor,
#             'concepto': deuda.concepto,
#         })
    
#     return render(request, 'deudores/editar_deuda.html', {'form': form, 'deuda': deuda})

def editar_deuda(request, deuda_id):
    deuda = get_object_or_404(Deuda, id=deuda_id)
    
    if request.method == 'POST':
        form = EditarDeudaForm(request.POST)
        if form.is_valid():
            # Crear una nueva instancia de EdicionDeuda con los datos del formulario
            EdicionDeuda.objects.create(
                deuda=deuda,
                fecha=form.cleaned_data['fecha_edicion'],
                deudor=deuda.deudor,
                nueva_deuda=form.cleaned_data['nueva_deuda'],
                fecha_edicion=form.cleaned_data['fecha_edicion'],
                concepto=form.cleaned_data['concepto'],
            )
            
            messages.success(request, "Deuda editada correctamente.")
            return redirect('consulta')
        else:
            messages.error(request, "Hubo un error al editar la deuda.")
    else:
        # Mostrar el formulario con los datos actuales de la deuda
        form = EditarDeudaForm(initial={
            'nueva_deuda': deuda.monto,
            'fecha': deuda.fecha,
            'fecha_edicion': timezone.now().date(),  # Fecha actual por defecto
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

# def consulta(request):
#     deudores = Deuda.objects.values_list('deudor__nombre', flat=True).distinct()
    
#     if request.method == 'POST':
#         tipo_consulta = request.POST.get('tipo_consulta')
        
#         if tipo_consulta == 'individual':
#             deudor_nombre = request.POST.get('deudor')
#             deudas = Deuda.objects.filter(deudor__nombre=deudor_nombre)
#             data = list(deudas.values('deudor__nombre', 'monto', 'fecha'))
#             filename = f"consulta_individual_{deudor_nombre}.xlsx"
#         else:
#             deudas = Deuda.objects.all()
#             pagos = Pago.objects.all()
#             gastos = Gasto.objects.all()
            
#             data = list(deudas.values('deudor__nombre', 'monto', 'fecha')) + \
#                    list(pagos.values('deuda__deudor__nombre', 'monto', 'fecha')) + \
#                    list(gastos.values('concepto', 'monto', 'fecha'))
#             filename = "consulta_general.xlsx"
        
#         # Crear un DataFrame con los datos
#         df = pd.DataFrame(data)
        
#         # Crear la respuesta HTTP con el archivo Excel
#         response = HttpResponse(content_type='application/ms-excel')
#         response['Content-Disposition'] = f'attachment; filename={filename}'
#         df.to_excel(response, index=False)
#         return response
    
#     return render(request, 'deudores/consulta.html', {'deudores': deudores})

import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render
from .models import Deuda, Pago, Gasto, EdicionDeuda

def consulta(request):
    deudores = Deuda.objects.values_list('deudor__nombre', flat=True).distinct()
    
    if request.method == 'POST':
        tipo_consulta = request.POST.get('tipo_consulta')
        
        if tipo_consulta == 'individual':
            deudor_nombre = request.POST.get('deudor')
            deudas = Deuda.objects.filter(deudor__nombre=deudor_nombre).select_related('deudor')

            # 📌 Incluir la última fecha de edición
            deudas_data = []
            for deuda in deudas:
                ultima_edicion = deuda.ediciones.order_by('-fecha_edicion').first()
                deudas_data.append({
                    "deudor": deuda.deudor.nombre,
                    "deuda_actual": deuda.monto,  # Ya se actualiza en el modelo
                    "fecha": deuda.fecha,
                    "fecha_actualizacion": ultima_edicion.fecha_edicion if ultima_edicion else deuda.fecha,  # Si no hay ediciones, usa la fecha original
                    "concepto": deuda.concepto
                })

            df = pd.DataFrame(deudas_data)
            filename = f"consulta_individual_{deudor_nombre}.xlsx"

        else:  # 📌 Consulta general
            deudas = Deuda.objects.all().select_related('deudor')
            pagos = Pago.objects.all().select_related('deuda__deudor')
            gastos = Gasto.objects.all()

            deudas_data = [
                {
                    "deudor": deuda.deudor.nombre,
                    "deuda_actual": deuda.monto,
                    "fecha": deuda.fecha,
                    "fecha_actualizacion": deuda.ediciones.order_by('-fecha_edicion').first().fecha_edicion if deuda.ediciones.exists() else deuda.fecha,
                    "concepto": deuda.concepto
                } for deuda in deudas
            ]

            pagos_data = [
                {
                    "deudor": pago.deuda.deudor.nombre,
                    "monto": -pago.monto,  # Se muestra como reducción
                    "fecha": pago.fecha,
                    "fecha_actualizacion": pago.fecha,
                    "concepto": "Pago"
                } for pago in pagos
            ]

            gastos_data = [
                {
                    "deudor": "Gasto",  # No tiene deudor
                    "monto": gasto.monto,
                    "fecha": gasto.fecha,
                    "fecha_actualizacion": gasto.fecha,
                    "concepto": gasto.concepto
                } for gasto in gastos
            ]

            df = pd.DataFrame(deudas_data + pagos_data + gastos_data)
            filename = "consulta_general.xlsx"
        
        # 📌 Generar el archivo Excel
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        df.to_excel(response, index=False)
        return response
    
    return render(request, 'deudores/consulta.html', {'deudores': deudores})

