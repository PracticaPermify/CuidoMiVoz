from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from django.contrib.auth import authenticate, login, logout
from .models import *
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.cache import never_cache
from django.utils import timezone
from django.urls import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
import os
from functools import wraps
from django.conf import settings
from rtdf.audio_coef import audio_analysis
from rtdf.analisis_estadistico import *
from rtdf.ciencia_datos import *
from django.http import FileResponse
from django.conf import settings
from datetime import datetime
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.shortcuts import render
from django.template.loader import render_to_string

from plotly.offline import plot
import plotly.graph_objs as go
from plotly.colors import DEFAULT_PLOTLY_COLORS
from plotly.subplots import make_subplots

class CustomPasswordResetView(PasswordResetView):
    template_name = 'registro/password_reset_form.html'
    email_template_name = 'correos/reset_email.html'
    success_url = reverse_lazy('custom_password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registro/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registro/password_reset_confirm.html'
    success_url = reverse_lazy('custom_password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registro/password_reset_complete.html'


# VISTAS GLOBALES ------------------------------------------------------------------------------->

def obtener_provincias(request):
    region_id = request.GET.get('region_id')
    provincias = Provincia.objects.filter(id_region=region_id).values('id_provincia', 'provincia')
    return JsonResponse(list(provincias), safe=False)

def obtener_comunas(request):
    provincia_id = request.GET.get('provincia_id')
    comunas = Comuna.objects.filter(id_provincia=provincia_id).values('id_comuna', 'comuna')
    return JsonResponse(list(comunas), safe=False)

def obtener_instituciones(request):
    comuna_id = request.GET.get('comuna_id')
    intituciones = Institucion.objects.filter(id_comuna=comuna_id).values('id_institucion', 'nombre_institucion')
    return JsonResponse(list(intituciones), safe=False)

def tipo_usuario_required(allowed_types):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            user_tipo = request.user.id_tp_usuario.tipo_usuario if request.user.is_authenticated else None

            if user_tipo in allowed_types:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('index')  

        return wrapper

    return decorator

def verificacion_perfil(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):

        usuario_logeado_id = request.user.id_usuario

        usuario_url_id = kwargs.get('usuario_id')

        if usuario_logeado_id != usuario_url_id:
            return redirect('index')

        return func(request, *args, **kwargs)

    return wrapper


def require_no_session(view_func):
    def wrapped(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index') 
        return view_func(request, *args, **kwargs)
    return wrapped


def validate(request):
    if request.is_anonymous:
        print(request)
        return False
    elif request:
        print(request)
        return True
    
def base(request):
    tipo_usuario = None 

    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

    return render(request, 'rtdf/base.html', {'tipo_usuario': tipo_usuario})

@never_cache
def index(request):
    tipo_usuario = None 
    usuarios = Usuario.objects.all()

    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario
        
        if tipo_usuario == 'Paciente':
            paciente = Paciente.objects.get(id_usuario=request.user)

            now = timezone.now()
            pautas_terapeuticas = PautaTerapeutica.objects.filter(
                fk_informe__fk_relacion_pa_pro__id_paciente=paciente,
                fecha_fin__gte=now 
            )

            pautas_terapeuticas_expiradas = PautaTerapeutica.objects.filter(
                fk_informe__fk_relacion_pa_pro__id_paciente=paciente,
                fecha_fin__lt=now 
            )

            paginador = Paginator(pautas_terapeuticas_expiradas, 5)
            page_number = request.GET.get('page')
            pautas_terapeuticas_expiradas = paginador.get_page(page_number)

            return render(request, 'rtdf/index.html', {'tipo_usuario': tipo_usuario, 
                                                       'usuario': usuarios,
                                                       'pautas_terapeuticas': pautas_terapeuticas,
                                                       'pautas_terapeuticas_expiradas': pautas_terapeuticas_expiradas,})
    
    usuarios_por_pagina = 10  
    paginator = Paginator(usuarios, usuarios_por_pagina)  

    page_number = request.GET.get('page')

    page = paginator.get_page(page_number)

    return render(request, 'rtdf/index.html', {'tipo_usuario': tipo_usuario, 
                                               'usuario': page})

@user_passes_test(validate)
@verificacion_perfil
def perfil(request, usuario_id):

    tipo_usuario = None 
    datos_paciente = None
    datos_familiar = None
    datos_profesional = None

    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

        datos_usuario = Usuario.objects.get(id_usuario=usuario_id)
        nombre_completo = f"{datos_usuario.primer_nombre} {datos_usuario.segundo_nombre if datos_usuario.segundo_nombre is not None else '' } {datos_usuario.ap_paterno} {datos_usuario.ap_materno if datos_usuario.ap_materno is not None else ''}"
        
        
        usuario_dicc = {
            'id_usuario': datos_usuario.id_usuario,
            'rut': datos_usuario.numero_identificacion,
            'primer_nombre': datos_usuario.primer_nombre,
            'segundo_nombre': datos_usuario.segundo_nombre,
            'ap_paterno': datos_usuario.ap_paterno,
            'ap_materno': datos_usuario.ap_materno,
            'fecha_nacimiento': datos_usuario.fecha_nacimiento,
            'email': datos_usuario.email,
            #'contraseña': datos_usuario.password,
            'celular': datos_usuario.numero_telefonico,
            'comuna': datos_usuario.id_comuna,
            'rol': datos_usuario.id_tp_usuario,
            'nombre_completo': nombre_completo,
        }

        if tipo_usuario == "Paciente":
            datos_paciente = Paciente.objects.get(id_usuario=usuario_id)
            print('Soy Paciente 😷')

        elif tipo_usuario == "Familiar":
            datos_familiar = FamiliarPaciente.objects.get(id_usuario=usuario_id)
            print('Soy Familiar 🤦‍♂️')

        elif tipo_usuario == "Admin":
            print('Soy admin 😎')

        else:
            datos_profesional = ProfesionalSalud.objects.get(id_usuario=usuario_id)    

    return render(request, 'rtdf/perfil.html', {'tipo_usuario': tipo_usuario, 
                                                'request':request,
                                                'datos_paciente': datos_paciente,
                                                'datos_familiar': datos_familiar,
                                                'datos_profesional': datos_profesional,
                                                'datos_usuario': usuario_dicc})

@login_required
@never_cache
@verificacion_perfil
def editar_perfil(request, usuario_id):
    regiones = Region.objects.all()
    admin = None
    tipo_usuario = None
    paciente = None
    familiar = None
    profesional_salud = None
    comunas = Comuna.objects.all()
    instituciones = Institucion.objects.all()


    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario
        id_tipo_usuario = request.user.id_tp_usuario_id

        tp_usuario_id = TpUsuario.objects.get(id_tp_usuario=id_tipo_usuario)
        #print(tp_usuario_id)

        usuario = Usuario.objects.get(id_usuario=usuario_id)
        
        if tipo_usuario == "Paciente":
            paciente = Paciente.objects.get(id_usuario=usuario_id)
            print('Soy Paciente 😷')

            fecha_nacimiento_original = usuario.fecha_nacimiento
            print(fecha_nacimiento_original)
            
            if request.method == "POST":
                tipo_usuario = tp_usuario_id.tipo_usuario  
                form = EditarPerfilForm(request.POST or None, tipo_usuario=tipo_usuario)
                

                if form.is_valid():
                    primer_nombre = form.cleaned_data['primer_nombre']
                    segundo_nombre = form.cleaned_data['segundo_nombre']
                    ap_paterno = form.cleaned_data['ap_paterno']
                    ap_materno = form.cleaned_data['ap_materno']
                    fecha_nacimiento = form.cleaned_data['fecha_nacimiento']
                    numero_telefonico = form.cleaned_data['numero_telefonico']
                    id_comuna = form.cleaned_data['id_comuna']
                    telegram = form.cleaned_data['telegram']
                    fk_tipo_diabetes = form.cleaned_data['fk_tipo_diabetes']
                    fk_tipo_hipertension = form.cleaned_data['fk_tipo_hipertension']
                    password = form.cleaned_data['password']
                    confirm_password = form.cleaned_data['confirm_password']
                    original_password = form.cleaned_data['original_password']

                    if password:
                        if request.user.check_password(original_password):
                            if password == confirm_password:
                                request.user.set_password(password)
                                request.user.save()
                                messages.success(request, "Contraseña actualizada con éxito.")

                                # Mantener inicio de sesion
                                update_session_auth_hash(request, request.user)
                            else:
                                messages.error(request, "Las contraseñas no coinciden.")
                        else:
                            messages.error(request, "La contraseña original es incorrecta")
                    else:
                        usuario.primer_nombre = primer_nombre
                        usuario.segundo_nombre = segundo_nombre
                        usuario.ap_paterno = ap_paterno
                        usuario.ap_materno = ap_materno
                        usuario.fecha_nacimiento = fecha_nacimiento
                        usuario.numero_telefonico = numero_telefonico
                        usuario.id_comuna = id_comuna
                        usuario.save()

                        paciente.telegram = telegram
                        paciente.fk_tipo_diabetes = fk_tipo_diabetes
                        paciente.fk_tipo_hipertension= fk_tipo_hipertension
                        paciente.save()

                    messages.success(request, "Datos actualizados con éxito.")
                    return redirect('perfil', usuario_id=usuario_id)
                else:
                    messages.error(request, "Hubo errores en el formulario. Por favor, corrige los campos con errores.")
            else:
                data = {
                    'primer_nombre': usuario.primer_nombre,
                    'segundo_nombre': usuario.segundo_nombre,
                    'ap_paterno': usuario.ap_paterno,
                    'ap_materno': usuario.ap_materno,
                    'fecha_nacimiento': fecha_nacimiento_original,
                    'numero_telefonico': usuario.numero_telefonico,
                    'id_comuna': usuario.id_comuna,
                    'telegram': paciente.telegram,
                    'fk_tipo_hipertension': paciente.fk_tipo_hipertension,
                    'fk_tipo_diabetes': paciente.fk_tipo_diabetes,
                }
                form = EditarPerfilForm(initial=data)

        elif tipo_usuario == "Familiar":
            familiar = FamiliarPaciente.objects.get(id_usuario=usuario_id)
            print('Soy Familiar 🤦‍♂️')

            fecha_nacimiento_original = usuario.fecha_nacimiento
            print(fecha_nacimiento_original)
            
            if request.method == "POST":
                tipo_usuario = tp_usuario_id.tipo_usuario  
                form = EditarPerfilForm(request.POST or None, tipo_usuario=tipo_usuario)
                

                if form.is_valid():
                    primer_nombre = form.cleaned_data['primer_nombre']
                    segundo_nombre = form.cleaned_data['segundo_nombre']
                    ap_paterno = form.cleaned_data['ap_paterno']
                    ap_materno = form.cleaned_data['ap_materno']
                    fecha_nacimiento = form.cleaned_data['fecha_nacimiento']
                    numero_telefonico = form.cleaned_data['numero_telefonico']
                    id_comuna = form.cleaned_data['id_comuna']
                    password = form.cleaned_data['password']
                    confirm_password = form.cleaned_data['confirm_password']
                    original_password = form.cleaned_data['original_password']

                    if password:
                        if request.user.check_password(original_password):
                            if password == confirm_password:
                                request.user.set_password(password)
                                request.user.save()
                                messages.success(request, "Contraseña actualizada con éxito.")

                                # Mantener inicio de sesion
                                update_session_auth_hash(request, request.user)
                            else:
                                messages.error(request, "Las contraseñas no coinciden.")
                        else:
                            messages.error(request, "La contraseña original es incorrecta")
                    else:
                        usuario.primer_nombre = primer_nombre
                        usuario.segundo_nombre = segundo_nombre
                        usuario.ap_paterno = ap_paterno
                        usuario.ap_materno = ap_materno
                        usuario.fecha_nacimiento = fecha_nacimiento
                        usuario.numero_telefonico = numero_telefonico
                        usuario.id_comuna = id_comuna
                        usuario.save()

                    messages.success(request, "Datos actualizados con éxito.")
                    return redirect('perfil', usuario_id=usuario_id)
                else:
                    messages.error(request, "Hubo errores en el formulario. Por favor, corrige los campos con errores.")
            else:
                data = {
                    'primer_nombre': usuario.primer_nombre,
                    'segundo_nombre': usuario.segundo_nombre,
                    'ap_paterno': usuario.ap_paterno,
                    'ap_materno': usuario.ap_materno,
                    'fecha_nacimiento': fecha_nacimiento_original,
                    'numero_telefonico': usuario.numero_telefonico,
                    'id_comuna': usuario.id_comuna,
                }
                form = EditarPerfilForm(initial=data)

        elif tipo_usuario == "Admin":
            print('Soy admin 😎')
            admin = True

            fecha_nacimiento_original = usuario.fecha_nacimiento
            print(fecha_nacimiento_original)
            
            if request.method == "POST":
                tipo_usuario = tp_usuario_id.tipo_usuario  
                form = EditarPerfilForm(request.POST or None, tipo_usuario=tipo_usuario)
                

                if form.is_valid():
                    primer_nombre = form.cleaned_data['primer_nombre']
                    segundo_nombre = form.cleaned_data['segundo_nombre']
                    ap_paterno = form.cleaned_data['ap_paterno']
                    ap_materno = form.cleaned_data['ap_materno']
                    fecha_nacimiento = form.cleaned_data['fecha_nacimiento']
                    numero_telefonico = form.cleaned_data['numero_telefonico']
                    id_comuna = form.cleaned_data['id_comuna']
                    password = form.cleaned_data['password']
                    confirm_password = form.cleaned_data['confirm_password']
                    original_password = form.cleaned_data['original_password']

                    if password:
                        if request.user.check_password(original_password):
                            if password == confirm_password:
                                request.user.set_password(password)
                                request.user.save()
                                messages.success(request, "Contraseña actualizada con éxito.")

                                # Mantener inicio de sesion
                                update_session_auth_hash(request, request.user)
                            else:
                                messages.error(request, "Las contraseñas no coinciden.")
                        else:
                            messages.error(request, "La contraseña original es incorrecta")
                    else:
                        usuario.primer_nombre = primer_nombre
                        usuario.segundo_nombre = segundo_nombre
                        usuario.ap_paterno = ap_paterno
                        usuario.ap_materno = ap_materno
                        usuario.fecha_nacimiento = fecha_nacimiento
                        usuario.numero_telefonico = numero_telefonico
                        usuario.id_comuna = id_comuna
                        usuario.save()

                    messages.success(request, "Datos actualizados con éxito.")
                    return redirect('perfil', usuario_id=usuario_id)
                else:
                    messages.error(request, "Hubo errores en el formulario. Por favor, corrige los campos con errores.")
            else:
                data = {
                    'primer_nombre': usuario.primer_nombre,
                    'segundo_nombre': usuario.segundo_nombre,
                    'ap_paterno': usuario.ap_paterno,
                    'ap_materno': usuario.ap_materno,
                    'fecha_nacimiento': fecha_nacimiento_original,
                    'numero_telefonico': usuario.numero_telefonico,
                    'id_comuna': usuario.id_comuna,
                }
                form = EditarPerfilForm(initial=data)

        else:
            profesional_salud = ProfesionalSalud.objects.get(id_usuario=usuario) 
            fecha_nacimiento_original = usuario.fecha_nacimiento
            print(fecha_nacimiento_original)
            

            if request.method == "POST":
                tipo_usuario = tp_usuario_id.tipo_usuario  
                form = EditarPerfilForm(request.POST or None, tipo_usuario=tipo_usuario)
                

                if form.is_valid():
                    primer_nombre = form.cleaned_data['primer_nombre']
                    segundo_nombre = form.cleaned_data['segundo_nombre']
                    ap_paterno = form.cleaned_data['ap_paterno']
                    ap_materno = form.cleaned_data['ap_materno']
                    fecha_nacimiento = form.cleaned_data['fecha_nacimiento']
                    numero_telefonico = form.cleaned_data['numero_telefonico']
                    id_comuna = form.cleaned_data['id_comuna']
                    titulo_profesional = form.cleaned_data['titulo_profesional']
                    id_institucion = form.cleaned_data['id_institucion']
                    password = form.cleaned_data['password']
                    confirm_password = form.cleaned_data['confirm_password']
                    original_password = form.cleaned_data['original_password']

                    if password:
                        if request.user.check_password(original_password):
                            if password == confirm_password:
                                request.user.set_password(password)
                                request.user.save()
                                messages.success(request, "Contraseña actualizada con éxito.")

                                # Mantener inicio de sesion
                                update_session_auth_hash(request, request.user)
                            else:
                                messages.error(request, "Las contraseñas no coinciden.")
                        else:
                            messages.error(request, "La contraseña original es incorrecta")
                    else:
                        usuario.primer_nombre = primer_nombre
                        usuario.segundo_nombre = segundo_nombre
                        usuario.ap_paterno = ap_paterno
                        usuario.ap_materno = ap_materno
                        usuario.fecha_nacimiento = fecha_nacimiento
                        usuario.numero_telefonico = numero_telefonico
                        usuario.id_comuna = id_comuna
                        usuario.save()

                        profesional_salud.titulo_profesional = titulo_profesional
                        profesional_salud.id_institucion = id_institucion
                        profesional_salud.save()

                    messages.success(request, "Datos actualizados con éxito.")
                    return redirect('perfil', usuario_id=usuario_id)
                else:
                    messages.error(request, "Hubo errores en el formulario. Por favor, corrige los campos con errores.")
            else:
                data = {
                    'primer_nombre': usuario.primer_nombre,
                    'segundo_nombre': usuario.segundo_nombre,
                    'ap_paterno': usuario.ap_paterno,
                    'ap_materno': usuario.ap_materno,
                    'fecha_nacimiento': fecha_nacimiento_original,
                    'numero_telefonico': usuario.numero_telefonico,
                    'id_comuna': usuario.id_comuna,
                    'titulo_profesional': profesional_salud.titulo_profesional,
                    'id_institucion': profesional_salud.id_institucion.id_institucion,
                }
                form = EditarPerfilForm(initial=data)
        

    return render(request, 'rtdf/editar_perfil.html', {'tipo_usuario': tipo_usuario,
                                                    'usuario': usuario,
                                                    'profesional_salud':profesional_salud,
                                                    'comunas':comunas,
                                                    'instituciones':instituciones,
                                                    'paciente': paciente,
                                                    'familiar': familiar,
                                                    'admin': admin,
                                                    'form': form,
                                                    'regiones':regiones})

# FIN DE VISTAS GLOBALES ------------------------------------------------------------------------------->

# VISTAS REGISTROS y LOGIN ------------------------------------------------------------------------------->

##Login para el usuario

@never_cache
@require_no_session
def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            response = redirect('index')
            response.set_cookie('logged_in', 'true')

            return response
        else:
            error_message = "Correo electrónico y/o contraseña inválidos. Inténtalo de nuevo."
            return render(request, 'registro/login.html', {'error_message': error_message})
    else:
        response = render(request, 'registro/login.html')

    response['Cache-Control'] = 'no-store'

    return response

##Cierre de sesion

def logout_view(request):
    logout(request)
    response = redirect('index')
    response.delete_cookie('logged_in')  # Elimina la cookie de inicio de sesión
    return response

@require_no_session
@never_cache
def registro(request):
    regiones = Region.objects.all()
    if request.method == 'POST':
        registro_form = RegistroForm(request.POST)

        if registro_form.is_valid():
            usuario = registro_form.save(commit=False)
            usuario.set_password(usuario.password)

            tipo_usuario = registro_form.cleaned_data['tipo_usuario']
            usuario.id_tp_usuario = tipo_usuario
            usuario.save()
            
            if tipo_usuario.tipo_usuario == 'Paciente':
                paciente = Paciente(
                    telegram=registro_form.cleaned_data['telegram'],
                    fk_tipo_hipertension=registro_form.cleaned_data['fk_tipo_hipertension'],
                    fk_tipo_diabetes=registro_form.cleaned_data['fk_tipo_diabetes'],
                    id_usuario=usuario
                )
                paciente.save()

            elif tipo_usuario.tipo_usuario == 'Familiar':
                rut_paciente = registro_form.cleaned_data.get('rut_paciente')
                
                try:
                    paciente_relacionado = Paciente.objects.get(id_usuario__numero_identificacion=rut_paciente)
                except Paciente.DoesNotExist:
                    mensaje_error = 'El paciente con el RUT proporcionado no se encuentra en la base de datos.'
                    return render(request, 'registro/registro.html', {'registro_form': registro_form, 
                                                                      'regiones': regiones,
                                                                      'mensaje_error': mensaje_error})

                familiar = FamiliarPaciente(
                    fk_tipo_familiar=registro_form.cleaned_data['fk_tipo_familiar'],
                    id_usuario=usuario
                )
                familiar.save()

                relacion_fp = RelacionFp(
                    id_paciente=paciente_relacionado,
                    fk_familiar_paciente=familiar
                )
                relacion_fp.save()

            messages.success(request, "Registrado correctamente")

            return redirect('login')

    else:
        registro_form = RegistroForm()

    return render(request, 'registro/registro.html', {'registro_form': registro_form, 
                                                      'regiones': regiones})

@require_no_session
@never_cache
def pre_registro(request):
    regiones = Region.objects.all()
    password = get_random_string(length=8)

    if request.method == 'POST':
        pre_registro_form = PreRegistroForm(request.POST)

        if pre_registro_form.is_valid():

            usuario = pre_registro_form.save(commit=False)
            # usuario.set_password(usuario.password)
            
            usuario.fecha_nacimiento = '2000-01-01'
            usuario.numero_telefonico = 'No informado'
            usuario.password = password
            usuario.id_comuna = Comuna.objects.get(id_comuna=1) 
            usuario.id_institucion = Institucion.objects.get(id_institucion=1)

            tipo_usuario = pre_registro_form.cleaned_data['tipo_usuario']
            usuario.id_tp_usuario = tipo_usuario
            usuario.save()
            
            messages.success(request, "Pre registrado correctamente")

            return redirect('login')

    else:
        # pre_registro_form = PreRegistroForm()

        # Instancias al formulario y se le pasan los datos directamente
        pre_registro_form = PreRegistroForm()
        del pre_registro_form.fields['fecha_nacimiento']
        del pre_registro_form.fields['numero_telefonico']
        del pre_registro_form.fields['password']
        del pre_registro_form.fields['id_comuna']
        del pre_registro_form.fields['id_institucion']
            

    return render(request, 'registro/pre_registro.html', 
                  {'registro_form': pre_registro_form,
                   'regiones': regiones})

# FIN DE VISTAS DE REGISTROS ------------------------------------------------------------------------------->


# VISTAS DE PACIENTES ------------------------------------------------------------------------------->

##Ejercicios de vocalización-----------------------------------

@never_cache
@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Paciente'])
def vocalizacion(request, pauta_id=None, *args, **kwargs):
    tipo_usuario = None
    pauta_seleccionada = None
    

    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

        # Se obtiene el nombre de usuario y su ID correspondiente
        nombre_usuario = f"{request.user.primer_nombre}_{request.user.ap_paterno}"
        id_usuario = request.user.id_usuario
        fecha = timezone.now()
        fecha_formateada = fecha.strftime("%Y-%m-%d_%H-%M-%S")

        # Ruta para la carpeta del usuario
        carpeta_usuario = os.path.join(settings.MEDIA_ROOT, 'audios_pacientes', nombre_usuario)

        # Verifica si la carpeta del usuario existe realmente
        if not os.path.exists(carpeta_usuario):
            os.makedirs(carpeta_usuario)

        id_pauta = None
        tipo_pauta = None

        if pauta_id is not None:
            try:
                pauta_seleccionada = PautaTerapeutica.objects.get(id_pauta_terapeutica=pauta_id)
                id_pauta = pauta_seleccionada.id_pauta_terapeutica
                tipo_pauta = pauta_seleccionada.fk_tp_terapia.tipo_terapia 
                id_profesional = pauta_seleccionada.fk_informe.fk_relacion_pa_pro.fk_profesional_salud.id_profesional_salud
                request.session['id_pauta'] = id_pauta  
                request.session['tipo_pauta'] = tipo_pauta
                request.session['id_profesional'] = id_profesional
                #print("ID PROFESIONAL", id_profesional)
            except PautaTerapeutica.DoesNotExist:
                pauta_seleccionada = None
       

    if request.method == 'POST':
        audio_file = request.FILES.get('file')
        print("Estoy llegando aquí", audio_file)

        # se obtiene las variables declaradas en la sesion
        id_pauta = request.session.get('id_pauta', None)
        tipo_pauta = request.session.get('tipo_pauta', None)
        id_profesional = request.session.get('id_profesional', None)

        # Construcción del nombre del archivo
        nombre_archivo = f"{nombre_usuario}_{id_usuario}_{fecha_formateada}_{tipo_pauta}_{id_pauta}_{id_profesional}_audio.wav"
        ruta_archivo = os.path.join(carpeta_usuario, nombre_archivo)

        # se elimina la variable de la sesion y se guarda en la DB
        if id_pauta is not None:

            # contruccion de la url para la tabla audio DB
            if tipo_pauta == "Vocalización":
                origen_audio = OrigenAudio.objects.get(id_origen_audio=2)
                
            else:
                origen_audio = OrigenAudio.objects.get(id_origen_audio=1)

            fk_pauta = PautaTerapeutica.objects.get(id_pauta_terapeutica=id_pauta)

            ruta_db = f"{nombre_usuario}/{nombre_archivo}"
            ##print("Ruta para la db:", ruta_db)

            audio_model = Audio.objects.create(url_audio=ruta_db,
                                               fecha_audio=fecha,
                                               fk_origen_audio=origen_audio,
                                               fk_pauta_terapeutica=fk_pauta)
            audio_model.save()

            id_audio_registrado = audio_model.id_audio


            #Esto guardara el archivo en la carpeta 
            if audio_file:
                with open(ruta_archivo, 'wb') as destination:
                    for chunk in audio_file.chunks():
                        destination.write(chunk)


            #REGISTRO DE LOS COEFICIENTES DE AUDIOS DE VOCALIZACION EN LA DB

            #obtencion del tipo de llenado automatico
            tipo_llenado = TpLlenado.objects.get(id_tipo_llenado=1)

            #obtencion del id del audio
            id_audio = Audio.objects.get(id_audio=id_audio_registrado)

            print(ruta_db)
            res = audio_analysis(ruta_db, nombre_archivo, fecha)
            is_coefs=Audioscoeficientes.objects.all().filter(nombre_archivo=nombre_archivo)
            # id_user=int(username.split(' ')[0])
            if not is_coefs.exists():
                print('analizando')
                coefs=Audioscoeficientes.objects.create(
                    nombre_archivo = nombre_archivo,
                    fecha_coeficiente = res['date'],               
                    f0  = res['f0'],
                    f1  = res['f1'],
                    f2  = res['f2'],
                    f3  = res['f3'],
                    f4  = res['f4'],
                    intensidad  = res['Intensity'],
                    hnr  = res['HNR'],
                    local_jitter  = res['localJitter'],
                    local_absolute_jitter  = res['localabsoluteJitter'],
                    rap_jitter  = res['rapJitter'],
                    ppq5_jitter  = res['ppq5Jitter'],
                    ddp_jitter = res['ddpJitter'],
                    local_shimmer = res['localShimmer'],
                    local_db_shimmer = res['localdbShimmer'],
                    apq3_shimmer = res['apq3Shimmer'],
                    aqpq5_shimmer = res['aqpq5Shimmer'],
                    apq11_shimmer = res['apq11Shimmer'],
                    fk_tipo_llenado = tipo_llenado, 
                    id_audio = id_audio
                )
                coefs.save()
                print('analizado')


            # del request.session['id_pauta']
            # del request.session['tipo_pauta']



    return render(request, 'vista_paciente/vocalizacion.html', {'tipo_usuario': tipo_usuario,
                                                               'pauta_seleccionada': pauta_seleccionada})


@never_cache
@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Paciente'])
def intensidad(request, pauta_id=None, *args, **kwargs):

    tipo_usuario = None
    pautas_terapeuticas = None
    pauta_seleccionada = None

    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

        nombre_usuario = f"{request.user.primer_nombre}_{request.user.ap_paterno}"
        id_usuario = request.user.id_usuario
        fecha = timezone.now()
        fecha_formateada = fecha.strftime("%Y-%m-%d-%H-%M-%S")

        carpeta_usuario = os.path.join(settings.MEDIA_ROOT, 'audios_pacientes', nombre_usuario)

        if not os.path.exists(carpeta_usuario):
            os.makedirs(carpeta_usuario)

        id_pauta = None
        tipo_pauta = None

        if pauta_id is not None:
            try:
                pauta_seleccionada = PautaTerapeutica.objects.get(id_pauta_terapeutica=pauta_id)
                id_pauta = pauta_seleccionada.id_pauta_terapeutica
                tipo_pauta = pauta_seleccionada.fk_tp_terapia.tipo_terapia 
                id_profesional = pauta_seleccionada.fk_informe.fk_relacion_pa_pro.fk_profesional_salud.id_profesional_salud
                request.session['id_pauta'] = id_pauta  
                request.session['tipo_pauta'] = tipo_pauta
                request.session['id_profesional'] = id_profesional
            except PautaTerapeutica.DoesNotExist:
                pauta_seleccionada = None

    if request.method == 'POST':
        audio_file = request.FILES.get('file')
        print("Estoy llegando aquí", audio_file)

        id_pauta = request.session.get('id_pauta', None)
        tipo_pauta = request.session.get('tipo_pauta', None)
        id_profesional = request.session.get('id_profesional', None)

        nombre_archivo = f"{nombre_usuario}_{id_usuario}_{fecha_formateada}_{tipo_pauta}_{id_pauta}_{id_profesional}_audio.wav"
        ruta_archivo = os.path.join(carpeta_usuario, nombre_archivo)

        if id_pauta is not None:

            if tipo_pauta == "Intensidad":
                origen_audio = OrigenAudio.objects.get(id_origen_audio=1)
            else:
                origen_audio = OrigenAudio.objects.get(id_origen_audio=2)

            fk_pauta = PautaTerapeutica.objects.get(id_pauta_terapeutica=id_pauta)

            ruta_db = f"{nombre_usuario}/{nombre_archivo}"
            ##print("Ruta para la db:", ruta_db)

            audio_model = Audio.objects.create(url_audio=ruta_db,
                                               fecha_audio=fecha,
                                               fk_origen_audio=origen_audio,
                                               fk_pauta_terapeutica=fk_pauta)
            audio_model.save()

            id_audio_registrado = audio_model.id_audio

            if audio_file:
                with open(ruta_archivo, 'wb') as destination:
                    for chunk in audio_file.chunks():
                        destination.write(chunk)

            #REGISTRO DE LOS COEFICIENTES DE AUDIOS DE INTENSIDAD EN LA DB

            tipo_llenado = TpLlenado.objects.get(id_tipo_llenado=1)

            id_audio = Audio.objects.get(id_audio=id_audio_registrado)

            print(ruta_db)
            res = audio_analysis(ruta_db, nombre_archivo, fecha)
            is_coefs=Audioscoeficientes.objects.all().filter(nombre_archivo=nombre_archivo)
            # id_user=int(username.split(' ')[0])
            if not is_coefs.exists():
                print('analizando')
                coefs=Audioscoeficientes.objects.create(
                    nombre_archivo = nombre_archivo,
                    fecha_coeficiente = fecha,                    
                    f0  = res['f0'],
                    f1  = res['f1'],
                    f2  = res['f2'],
                    f3  = res['f3'],
                    f4  = res['f4'],
                    intensidad  = res['Intensity'],
                    hnr  = res['HNR'],
                    local_jitter  = res['localJitter'],
                    local_absolute_jitter  = res['localabsoluteJitter'],
                    rap_jitter  = res['rapJitter'],
                    ppq5_jitter  = res['ppq5Jitter'],
                    ddp_jitter = res['ddpJitter'],
                    local_shimmer = res['localShimmer'],
                    local_db_shimmer = res['localdbShimmer'],
                    apq3_shimmer = res['apq3Shimmer'],
                    aqpq5_shimmer = res['aqpq5Shimmer'],
                    apq11_shimmer = res['apq11Shimmer'],
                    fk_tipo_llenado = tipo_llenado, 
                    id_audio = id_audio
                )
                coefs.save()
                print('analizado')


            # del request.session['id_pauta']
            # del request.session['tipo_pauta']

    return render(request,'vista_paciente/intensidad.html', {'tipo_usuario': tipo_usuario,
                                                            'pauta_seleccionada': pauta_seleccionada})

@never_cache
@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Paciente'])
def escalas_vocales(request, pauta_id=None, *args, **kwargs):
    tipo_usuario = None
    pauta_seleccionada = None

    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

        nombre_usuario = f"{request.user.primer_nombre}_{request.user.ap_paterno}"
        id_usuario = request.user.id_usuario
        fecha = timezone.now()
        fecha_formateada = fecha.strftime("%Y-%m-%d_%H-%M-%S")

        carpeta_usuario = os.path.join(settings.MEDIA_ROOT, 'audios_pacientes', nombre_usuario)

        if not os.path.exists(carpeta_usuario):
            os.makedirs(carpeta_usuario)

        id_pauta = None
        tipo_pauta = None

        if pauta_id is not None:
            try:
                pauta_seleccionada = PautaTerapeutica.objects.get(id_pauta_terapeutica=pauta_id)
                print(pauta_seleccionada.escalavocales)
                id_pauta = pauta_seleccionada.id_pauta_terapeutica
                tipo_pauta = pauta_seleccionada.fk_tp_terapia.tipo_terapia 
                id_profesional = pauta_seleccionada.fk_informe.fk_relacion_pa_pro.fk_profesional_salud.id_profesional_salud
                request.session['id_pauta'] = id_pauta  
                request.session['tipo_pauta'] = tipo_pauta
                request.session['id_profesional'] = id_profesional

         
                #print("ID PROFESIONAL", id_profesional)
            except PautaTerapeutica.DoesNotExist:
                pauta_seleccionada = None

    if request.method == 'POST':
        audio_file = request.FILES.get('file')
        print("Estoy llegando aquí", audio_file)

        id_pauta = request.session.get('id_pauta', None)
        tipo_pauta = request.session.get('tipo_pauta', None)
        id_profesional = request.session.get('id_profesional', None)

        nombre_archivo = f"{nombre_usuario}_{id_usuario}_{fecha_formateada}_{tipo_pauta}_{id_pauta}_{id_profesional}_audio.wav"
        ruta_archivo = os.path.join(carpeta_usuario, nombre_archivo)

        if id_pauta is not None:

            if tipo_pauta == "Escala_vocal":
                origen_audio = OrigenAudio.objects.get(id_origen_audio=3)
                
            else:
                origen_audio = OrigenAudio.objects.get(id_origen_audio=1)

            fk_pauta = PautaTerapeutica.objects.get(id_pauta_terapeutica=id_pauta)

            ruta_db = f"{nombre_usuario}/{nombre_archivo}"
            ##print("Ruta para la db:", ruta_db)

            audio_model = Audio.objects.create(url_audio=ruta_db,
                                               fecha_audio=fecha,
                                               fk_origen_audio=origen_audio,
                                               fk_pauta_terapeutica=fk_pauta)
            audio_model.save()

            id_audio_registrado = audio_model.id_audio

            if audio_file:
                with open(ruta_archivo, 'wb') as destination:
                    for chunk in audio_file.chunks():
                        destination.write(chunk)

            tipo_llenado = TpLlenado.objects.get(id_tipo_llenado=1)

            id_audio = Audio.objects.get(id_audio=id_audio_registrado)

            print(ruta_db)
            res = audio_analysis(ruta_db, nombre_archivo, fecha)
            is_coefs=Audioscoeficientes.objects.all().filter(nombre_archivo=nombre_archivo)
            # id_user=int(username.split(' ')[0])
            if not is_coefs.exists():
                print('analizando')
                coefs=Audioscoeficientes.objects.create(
                    nombre_archivo = nombre_archivo,
                    fecha_coeficiente = res['date'],               
                    f0  = res['f0'],
                    f1  = res['f1'],
                    f2  = res['f2'],
                    f3  = res['f3'],
                    f4  = res['f4'],
                    intensidad  = res['Intensity'],
                    hnr  = res['HNR'],
                    local_jitter  = res['localJitter'],
                    local_absolute_jitter  = res['localabsoluteJitter'],
                    rap_jitter  = res['rapJitter'],
                    ppq5_jitter  = res['ppq5Jitter'],
                    ddp_jitter = res['ddpJitter'],
                    local_shimmer = res['localShimmer'],
                    local_db_shimmer = res['localdbShimmer'],
                    apq3_shimmer = res['apq3Shimmer'],
                    aqpq5_shimmer = res['aqpq5Shimmer'],
                    apq11_shimmer = res['apq11Shimmer'],
                    fk_tipo_llenado = tipo_llenado, 
                    id_audio = id_audio
                )
                coefs.save()
                print('analizado')


            # del request.session['id_pauta']
            # del request.session['tipo_pauta']



    return render(request, 'vista_paciente/escalas_vocales.html', {'tipo_usuario': tipo_usuario,
                                                               'pauta_seleccionada': pauta_seleccionada})


@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Paciente'])
def mi_fonoaudiologo(request):

    tipo_usuario = None 
    usuarios = Usuario.objects.all()

    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

        id_usuario = request.user.id_usuario 

        try:
            paciente_salud = Paciente.objects.get(id_usuario=id_usuario)
        except Paciente.DoesNotExist:
            paciente_salud = None

        
        profesional_relacionados = []

        
        if paciente_salud:
            profesional_relacionados = RelacionPaPro.objects.filter(id_paciente=paciente_salud)

        # lista de los pacientes con datos de usuario y paciente
        pacientes = []

        for relacion in profesional_relacionados:
            paciente_dicc = {
                'id_fonoaudiologo': relacion.fk_profesional_salud.id_profesional_salud,
                'id_usuario_fonoaudiologo':relacion.fk_profesional_salud.id_usuario.id_usuario,
                'nombre_profesional_salud':relacion.fk_profesional_salud.id_usuario.primer_nombre,
                'ap_paterno_profesional_salud':relacion.fk_profesional_salud.id_usuario.ap_paterno,
                'correo_profesional_salud':relacion.fk_profesional_salud.id_usuario.email,
                'numero_telefonico_profesional_salud':relacion.fk_profesional_salud.id_usuario.numero_telefonico,
                #'id_paciente': relacion.id_paciente.id_paciente,
                #'primer_nombre': relacion.id_paciente.id_usuario.primer_nombre,
                #'ap_paterno': relacion.id_paciente.id_usuario.ap_paterno,
                #'email': relacion.id_paciente.id_usuario.email,
                #'numero_telefonico': relacion.id_paciente.id_usuario.numero_telefonico,
                #'telegram': relacion.id_paciente.telegram,
                #'fecha_nacimiento': relacion.id_paciente.id_usuario.fecha_nacimiento,
                #'tipo_diabetes': relacion.id_paciente.fk_tipo_diabetes,
                #'tipo_hipertension': relacion.id_paciente.fk_tipo_hipertension,
            }
            pacientes.append(paciente_dicc)

    return render(request, 'vista_paciente/mi_fonoaudiologo.html', {'tipo_usuario': tipo_usuario, 'usuario': usuarios, 'pacientes': pacientes})

# FIN DE VISTAS DE PACIENTES ------------------------------------------------------------------------------->

# VISTAS DE FAMILIARES ------------------------------------------------------------------------------->

##Listado para los familiares--------------------------------------

@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Familiar'])
def lista_familiar(request):

    tipo_usuario = None
    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

        # se obtiene el identificador de la fk usuario relacionado al fonoaudiologo
        id_usuario = request.user.id_usuario

        try:
            # se obtiene el fonoaudiologo relacionado
            familiar = FamiliarPaciente.objects.get(id_usuario=id_usuario)
        except FamiliarPaciente.DoesNotExist:
            familiar = None

        # lista para almacenar los pacientes relacionados
        pacientes_relacionados = []

        # filtrado de los pacientes relacionados
        if familiar:
            pacientes_relacionados = RelacionFp.objects.filter(fk_familiar_paciente=familiar)

        # lista de los pacientes con datos de usuario y paciente
        pacientes = []

        # se cargan los datos en variables 
        for relacion in pacientes_relacionados:
            paciente_dicc = {
                'id_usuario': relacion.id_paciente.id_usuario.id_usuario,
                'id_paciente': relacion.id_paciente.id_paciente,
                'primer_nombre': relacion.id_paciente.id_usuario.primer_nombre,
                'ap_paterno': relacion.id_paciente.id_usuario.ap_paterno,
                'email': relacion.id_paciente.id_usuario.email,
                'numero_telefonico': relacion.id_paciente.id_usuario.numero_telefonico,
                'telegram': relacion.id_paciente.telegram,
                'fecha_nacimiento': relacion.id_paciente.id_usuario.fecha_nacimiento,
                'tipo_diabetes': relacion.id_paciente.fk_tipo_diabetes,
                'tipo_hipertension': relacion.id_paciente.fk_tipo_hipertension,
            }
            pacientes.append(paciente_dicc)

    return render(request,'vista_familiar/lista_familiar.html', {'tipo_usuario': tipo_usuario, 'pacientes': pacientes})

## Detalles de los pacientes de un familiar

@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Familiar'])
def detalle_familiar(request, paciente_id):

    tipo_usuario = None
    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

    paciente = get_object_or_404(Usuario, id_usuario=paciente_id, id_tp_usuario__tipo_usuario='Paciente')
    paciente_info = paciente.paciente

    fonoaudiologos_asociados = ProfesionalSalud.objects.filter(relacionpapro__id_paciente=paciente_info.id_paciente)

    return render(request, 'vista_familiar/detalle_familiar.html',{'paciente': paciente, 
                                                                 'tipo_usuario': tipo_usuario,
                                                                 'paciente_info': paciente_info,
                                                                 'fonoaudiologos_asociados': fonoaudiologos_asociados
                                                                 })

# FIN DE VISTAS DE FAMILIARES ------------------------------------------------------------------------------->


# VISTAS DE PROFESIONALES ------------------------------------------------------------------------------->

@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Fonoaudiologo'])
def esv(request):
    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

        profesional_salud = request.user.profesionalsalud
        relaciones_pacientes = RelacionPaPro.objects.filter(fk_profesional_salud=profesional_salud)

        preguntas = [
            "¿Tiene dificultades para llamar la atención de los demás usando su voz?",
            "¿Tiene problemas al cantar?",
            "¿Le duele la garganta?",
            "¿Su voz está ronca?",
            "En conversaciones grupales, ¿Las personas tienen dificultades para escucharlo(a)?",
            "¿Suele perder su voz?",
            "¿Suele toser o carraspear?",
            "¿Considera que tiene una voz débil?",
            "¿Tiene problemas al hablar por teléfono?",
            "¿Se siente menos valorado o deprimido debido a su problema de la voz?",
            "¿Siente como si tuviera algo atascado en su garganta?",
            "¿Siente inflamación en la garganta?",
            "¿Siente pudor al usar su voz?",
            "¿Siente que se cansa al hablar?",
            "¿Su problema de la voz lo hace sentir estresado y nervioso?",
            "¿Tiene dificultades para hacerse escuchar cuando hay ruido en el ambiente?",
            "¿Es incapaz de gritar o alzar la voz?",
            "¿Su problema de la voz le genera complicaciones con su familia y amigos?",
            "¿Tiene mucha flema o mucosidad en su garganta?",
            "¿Siente que la calidad de su voz varía durante el día?",
            "¿Siente que a las personas les molesta su voz?",
            "¿Tiene la nariz tapada?",
            "¿La gente le pregunta qué le pasa a su voz?",
            "¿Siente que su voz suena ronca y seca?",
            "¿Siente que debe esforzarse para sacar la voz?",
            "¿Con cuánta frecuencia presenta infecciones en la garganta?",
            "¿Su voz se “agota” mientras está hablando?",
            "¿Su voz lo(a) hace sentir incompetente?",
            "¿Se siente avergonzado debido a su problema de la voz?",
            "¿Se siente aislado por sus problemas con la voz?"
        ]

        opciones_respuesta = ["Nunca", "Casi nunca", "A veces", "Casi siempre", "Siempre"]

        if request.method == 'POST':
            form = InformeForm(request.POST)
            if form.is_valid():
                form.instance.tp_informe = TpInforme.objects.get(tipo_informe='ESV')
                informe = form.save()
                informe.fecha = timezone.now()

                #Declaro variables para almacenar los puntajes
                puntaje_limitacion = 0
                puntaje_emocional = 0
                puntaje_fisico = 0

                for i, pregunta in enumerate(preguntas):
                    respuesta = request.POST.get(f"respuesta_{i + 1}")

                    if respuesta == "Nunca":
                        puntaje = 0
                    elif respuesta == "Casi nunca":
                        puntaje = 1
                    elif respuesta == "A veces":
                        puntaje = 2
                    elif respuesta == "Casi siempre":
                        puntaje = 3
                    else:
                        puntaje = 4

                    if i + 1 in [1, 2, 4, 5, 6, 8, 9, 14, 16, 17, 20, 23, 24, 25, 27]:
                        puntaje_limitacion += puntaje
                    elif i + 1 in [10, 13, 15, 18, 21, 28, 29, 30]:
                        puntaje_emocional += puntaje
                    elif i + 1 in [3, 7, 11, 12, 19, 22, 26]:
                        puntaje_fisico += puntaje

                #Segun el documento de fonoaudiologia, el puntaje requerido es de 60, 32 y 28 para la escala vocal
                puntaje_limitacion = min(puntaje_limitacion, 60)
                puntaje_emocional = min(puntaje_emocional, 32)
                puntaje_fisico = min(puntaje_fisico, 28)

                puntaje_total = puntaje_limitacion + puntaje_emocional + puntaje_fisico
                if puntaje_total > 120:
                    puntaje_total = 120

                #Con los valores agregados en cada variable, le asigno que lo almacene en la tabla correspondiente
                esv_instance = Esv(id_informe=informe, total_esv=puntaje_total, limitacion=puntaje_limitacion,
                                    emocional=puntaje_emocional, fisico=puntaje_fisico)
                esv_instance.save()

                messages.success(request, "Informe ESV ingresado correctamente")  

                return redirect('listado_informes')
        else:
            form = InformeForm(initial={'fecha': timezone.now()})
            form.fields['fk_relacion_pa_pro'].queryset = relaciones_pacientes

    return render(request, 'vista_profe/esv.html', {
        'form': form,
        'tipo_usuario': tipo_usuario,
        'preguntas': preguntas,
        'opciones_respuesta': opciones_respuesta,
    })

@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Fonoaudiologo'])
def listado_pacientes(request):

    tipo_usuario = None 
    usuarios = Usuario.objects.all()

    # se verifica que el usuario este registrado como profesional salud
    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

        # se obtiene el identificador de la fk usuario relacionado al fonoaudiologo
        id_usuario = request.user.id_usuario

        try:
            # se obtiene el fonoaudiologo relacionado
            profesional_salud = ProfesionalSalud.objects.get(id_usuario=id_usuario)
        except ProfesionalSalud.DoesNotExist:
            profesional_salud = None

        # lista para almacenar los pacientes relacionados
        pacientes_relacionados = []

        # filtrado de los pacientes relacionados
        if profesional_salud:
            pacientes_relacionados = RelacionPaPro.objects.filter(fk_profesional_salud=profesional_salud)

        # lista de los pacientes con datos de usuario y paciente
        pacientes = []

        # se cargan los datos en variables 
        for relacion in pacientes_relacionados:
            paciente_dicc = {
                'id_usuario': relacion.id_paciente.id_usuario.id_usuario,
                'id_paciente': relacion.id_paciente.id_paciente,
                'primer_nombre': relacion.id_paciente.id_usuario.primer_nombre,
                'segundo_nombre': relacion.id_paciente.id_usuario.segundo_nombre,
                'ap_paterno': relacion.id_paciente.id_usuario.ap_paterno,
                'ap_materno': relacion.id_paciente.id_usuario.ap_materno,
                'email': relacion.id_paciente.id_usuario.email,
                'numero_telefonico': relacion.id_paciente.id_usuario.numero_telefonico,
                'telegram': relacion.id_paciente.telegram,
                'fecha_nacimiento': relacion.id_paciente.id_usuario.fecha_nacimiento,
                'tipo_diabetes': relacion.id_paciente.fk_tipo_diabetes,
                'tipo_hipertension': relacion.id_paciente.fk_tipo_hipertension,
            }
            pacientes.append(paciente_dicc)

    return render(request, 'vista_profe/listado_pacientes.html', {'tipo_usuario': tipo_usuario, 
                                                                  'usuario': usuarios, 
                                                                  'pacientes': pacientes,})

@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Fonoaudiologo'])
def ingresar_informes(request):
    tipo_usuario = None

    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario
        
        profesional_salud = request.user.profesionalsalud
        relaciones_pacientes = RelacionPaPro.objects.filter(fk_profesional_salud=profesional_salud)

        if request.method == 'POST':
            form = InformeForm(request.POST)
            grbas_form = GrbasForm(request.POST)
            rasati_form = RasatiForm(request.POST)

            form.fields['fk_relacion_pa_pro'].queryset = relaciones_pacientes

            if form.is_valid() and grbas_form.is_valid() and rasati_form.is_valid():
                informe = form.save()
                tipo_informe = str(form.cleaned_data['tp_informe']).strip()
                informe.fecha = timezone.now()
                print(f"Tipo de informe seleccionado: {tipo_informe}")

                # Filtro segun el tipo de informe seleccionado
                if tipo_informe == 'GRBAS':
                    
                    grbas = grbas_form.save(commit=False)
                    grbas.id_informe = informe
                    grbas.save()

                elif tipo_informe == 'RASATI':
                    
                    ##print(f"Tipo AAA: {tipo_informe}")    
                    rasati = rasati_form.save(commit=False)
                    rasati.id_informe = informe
                    rasati.save()
                messages.success(request, "Informe "+ tipo_informe + " ingresado correctamente")  
                return redirect('listado_informes')
        else:
            form = InformeForm(initial={'fecha': timezone.now()})
            form.fields['fk_relacion_pa_pro'].queryset = relaciones_pacientes
            grbas_form = GrbasForm()
            rasati_form = RasatiForm()
            form.fields['tp_informe'].required = True

        return render(request, 'vista_profe/ingresar_informes.html', {
            'form': form,
            'grbas_form': grbas_form,
            'rasati_form': rasati_form,
            'tipo_usuario': tipo_usuario,
        })
    else:
        return redirect('vista_profe/index.html')
    

@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Fonoaudiologo'])
def editar_informe(request, informe_id):
    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

        informe = get_object_or_404(Informe, id_informe=informe_id)
        profesional_salud = request.user.profesionalsalud
        relaciones_pacientes = RelacionPaPro.objects.filter(fk_profesional_salud=profesional_salud)

        paciente = informe.fk_relacion_pa_pro
        rasati_form = None
        grbas_form = None
        vista= "editar_informe"

        try:
            if informe.rasati:
                rasati_form = RasatiForm(request.POST or None, instance=informe.rasati)
        except Rasati.DoesNotExist:
            rasati_form = RasatiForm()

        try:
            if informe.grbas:
                grbas_form = GrbasForm(request.POST or None, instance=informe.grbas)
        except Grbas.DoesNotExist:
            grbas_form = GrbasForm()

        if request.method == 'POST':
            form = InformeForm(request.POST, instance=informe, vista_contexto=vista)
            # form.fields['fk_relacion_pa_pro'].queryset = relaciones_pacientes

            if form.is_valid():

                print(f"Valor después de asignar: {form.cleaned_data['fk_relacion_pa_pro']}")
                form = form.save(commit=False)
                form.fk_relacion_pa_pro = paciente
                form.fecha = timezone.now()
                form.save()
                print(f"Informe guardado: {informe.fk_relacion_pa_pro}")

            if rasati_form and rasati_form.is_valid():
                print(f"Informe.rasati: {rasati_form}")
                rasati_form.save()

            if grbas_form and grbas_form.is_valid():
                grbas_form.save()

            messages.success(request, "Informe "+ str(informe_id) + " editado correctamente")  
            return redirect('detalle_prof_infor', informe_id=informe.id_informe)
        else:
            form = InformeForm(instance=informe)
            form.fields['fk_relacion_pa_pro'].queryset = relaciones_pacientes
        
        
        return render(request, 'vista_profe/editar_informe.html', {'form': form, 
                                                                'informe': informe,
                                                                'grbas_form': grbas_form,
                                                                'rasati_form': rasati_form,
                                                                'tipo_usuario': tipo_usuario,
                                                                })


@never_cache
@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Fonoaudiologo'])
def detalle_esv(request, informe_id):
    tipo_usuario = None

    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario
        informe = get_object_or_404(Informe, pk=informe_id)
        paciente_relacionado = informe.fk_relacion_pa_pro.id_paciente

        pautas_terapeuticas = PautaTerapeutica.objects.filter(
            fk_informe=informe,
            fk_informe__fk_relacion_pa_pro__id_paciente=paciente_relacionado,
            fk_tp_terapia__tipo_terapia='Escala_vocal'
        )

    if request.method == 'POST':
        pauta_terapeutica_form = PautaTerapeuticaForm(request.POST)

        if pauta_terapeutica_form.is_valid():
            pauta_terapeutica = pauta_terapeutica_form.save(commit=False)
            pauta_terapeutica.fk_informe = informe
            pauta_terapeutica.fk_tp_terapia = TpTerapia.objects.get(tipo_terapia='Escala_vocal')
            pauta_terapeutica.save()

            palabras = []
            for i in range(1, 21): 
                palabra_id = request.POST.get(f'palabra{i}', '')  
                if palabra_id:
                    palabra = PalabrasPacientes.objects.get(pk=palabra_id) 
                    palabras.append(palabra.palabras_paciente)

            palabras_concatenadas = ", ".join(palabras)

            escala_vocales = EscalaVocales(palabras=palabras_concatenadas)
            escala_vocales.id_pauta_terapeutica = pauta_terapeutica
            escala_vocales.save()

            messages.success(request, "Pauta Escala Vocal agregada correctamente")  
            return HttpResponseRedirect(request.path_info)

    else:
        pauta_terapeutica_form = PautaTerapeuticaForm()

    palabras_pacientes = PalabrasPacientes.objects.all()

    selects = []
    for i in range(1, 21):
        palabras_select = PalabrasPacientes.objects.filter().order_by('id_palabras_pacientes')[i-1]
        selects.append({
            'id': i,
            'palabras_pacientes': palabras_pacientes,
            'palabras_select': palabras_select,
        })

    return render(request, 'vista_profe/detalle_esv.html', {
        'informe': informe,
        'tipo_usuario': tipo_usuario,
        'paciente_relacionado': paciente_relacionado,
        'pauta_terapeutica_form': pauta_terapeutica_form,
        'pautas_terapeuticas': pautas_terapeuticas,
        'selects': selects,
    })


@never_cache
@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Fonoaudiologo'])
def detalle_pauta_esv(request, pauta_id):

    tipo_usuario = None

    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

    source = request.GET.get('source')

    if source == 'plantilla1':
        url_regreso = reverse('listado_informes')
    elif source == 'plantilla2':
        url_regreso = reverse('detalle_esv')
    else:
        url_regreso = reverse('listado_informes')

    pauta = get_object_or_404(PautaTerapeutica, pk=pauta_id)

    if pauta.fk_tp_terapia.tipo_terapia == 'Escala_vocal':
        paciente = pauta.fk_informe.fk_relacion_pa_pro.id_paciente.id_usuario
        escala_vocales = pauta.escalavocales 
        palabras = escala_vocales.palabras

        return render(request, 'vista_profe/detalle_pauta_esv.html', {'pauta': pauta, 
                                                                      'palabras': palabras,
                                                                      'paciente': paciente,
                                                                      'url_regreso': url_regreso,
                                                                      'tipo_usuario': tipo_usuario})
    else:
        return render(request, 'vista_profe/error.html', {'message': 'La pauta no es del tipo "Escala Vocal."'})
    
@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Fonoaudiologo'])
def analisis_profe(request):
    tipo_usuario = None

    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

        datos_audiocoeficientes = Audioscoeficientes.objects.select_related(
        'id_audio__fk_pauta_terapeutica__fk_informe__fk_relacion_pa_pro__id_paciente__id_usuario'
        ).filter(
            id_audio__fk_pauta_terapeutica__fk_informe__fk_relacion_pa_pro__fk_profesional_salud__id_usuario=request.user.id_usuario
        ).order_by('-fecha_coeficiente')


        relaciones = RelacionPaPro.objects.filter(
            fk_profesional_salud__id_usuario=request.user.id_usuario
        )

        conteo_audios = []

        total_intensidad = 0
        total_vocalizacion = 0

        for relacion in relaciones:
            relacion_info = {
                'relacion': relacion,
                'origenes_audio': {}
            }

            for origen_id, origen_nombre in [(1, 'Intensidad'), (2, 'Vocalización')]:
                audios = Audio.objects.filter(
                    fk_origen_audio=origen_id,
                    fk_pauta_terapeutica__fk_informe__fk_relacion_pa_pro=relacion
                )
                relacion_info['origenes_audio'][origen_nombre] = len(audios)

                if origen_id == 1:
                    total_intensidad += len(audios)
                else:
                    total_vocalizacion += len(audios)

            conteo_audios.append(relacion_info)

        items_por_pagina = 10

        paginator = Paginator(datos_audiocoeficientes, items_por_pagina)

        page = request.GET.get('page', 1)

        try:
            audios_pagina = paginator.page(page)
        except PageNotAnInteger:
            audios_pagina = paginator.page(1)
        except EmptyPage:
            audios_pagina = paginator.page(paginator.num_pages)

    return render(request, 'vista_profe/analisis_profe.html', {
        'tipo_usuario': tipo_usuario,
        'datos_audiocoeficientes': audios_pagina,
        'datos_audio_relacion': conteo_audios,
        'total_intensidad': total_intensidad,
        'total_vocalizacion': total_vocalizacion,
        'paginator': paginator,
    })

@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Fonoaudiologo'])
def editar_pauta_esv(request, pauta_id):

    tipo_usuario = None

    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario
    
    pauta = get_object_or_404(PautaTerapeutica, pk=pauta_id)
    
    if pauta.fk_tp_terapia.tipo_terapia != 'Escala_vocal':
        return render(request, 'vista_profe/error.html', {'message': 'Error: Esta pauta no es de Escala Vocal.'})

    palabras_pacientes = PalabrasPacientes.objects.all()
    palabras_pauta = pauta.escalavocales.palabras.split(', ') if pauta.escalavocales else []

    if request.method == 'POST':
        form = PautaTerapeuticaForm(request.POST, instance=pauta)

        if form.is_valid():
            form.instance.fk_tp_terapia_id = 3  
            form.save()

            palabras = []
            for i in range(1, 21):
                palabra_id = request.POST.get(f'palabra{i}', '')
                if palabra_id:
                    palabra = PalabrasPacientes.objects.get(pk=palabra_id)
                    palabras.append(palabra.palabras_paciente)

            palabras_concatenadas = ", ".join(palabras)

            if pauta.escalavocales:
                pauta.escalavocales.palabras = palabras_concatenadas
                pauta.escalavocales.save()
            else:
                escala_vocales = EscalaVocales(palabras=palabras_concatenadas)
                escala_vocales.id_pauta_terapeutica = pauta
                escala_vocales.save()

            messages.success(request, "Pauta ESV N°" + str(pauta_id) + " editada correctamente")  
            return redirect('detalle_pauta_esv', pauta_id)
    else:
        form = PautaTerapeuticaForm(instance=pauta)

        selects = []
        for i in range(1, 21):
            selects.append({
                'id': i,
                'palabras_pacientes': palabras_pacientes,
                'palabra_seleccionada': palabras_pauta[i - 1] if i <= len(palabras_pauta) else None,
            })

    return render(request, 'vista_profe/editar_pauta_esv.html', {
        'form': form,
        'pauta': pauta,
        'selects': selects,
        'tipo_usuario': tipo_usuario
    })

@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Fonoaudiologo'])
def eliminar_pauta_esv(request, pauta_id):

    pauta = get_object_or_404(PautaTerapeutica, pk=pauta_id)

    if pauta.fk_tp_terapia.tipo_terapia == 'Escala_vocal':
        pauta.delete()

    messages.success(request, "Pauta ESV N°" + str(pauta_id) + " eliminada correctamente")
    return redirect('detalle_esv', informe_id=pauta.fk_informe.id_informe)


@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Fonoaudiologo'])
def editar_esv(request, informe_id):
    tipo_usuario = None
    
    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

    informe = get_object_or_404(Informe, pk=informe_id)

    if request.method == 'POST':
        informe.titulo = request.POST.get('titulo')
        informe.fecha = request.POST.get('fecha')
        informe.descripcion = request.POST.get('descripcion')
        informe.observacion = request.POST.get('observacion')
        informe.save()

        messages.success(request, "Informe ESV N°" + str(informe_id) + " editado correctamente")

        return redirect('detalle_esv', informe_id)
    else:
        return render(request, 'vista_profe/editar_esv.html', {'informe': informe, 
                                                                 'tipo_usuario': tipo_usuario})

@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Fonoaudiologo'])
def eliminar_informe_esv(request, informe_id):
    informe = get_object_or_404(Informe, id_informe=informe_id)
    esv_instance = Esv.objects.filter(id_informe=informe)

    if esv_instance.exists():
        esv_instance.delete()

    informe.delete()
    messages.success(request, "Informe ESV eliminado correctamente")
    return redirect('listado_informes')


@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Fonoaudiologo'])
def eliminar_informe(request, informe_id):
    informe = get_object_or_404(Informe, id_informe=informe_id)
    tipo_informe = informe.tp_informe

    if tipo_informe == 'GRBAS':
        informe.grbas.delete()
    elif tipo_informe == 'RASATI':
        informe.rasati.delete()

    informe.delete()

    messages.success(request, "Informe N°"+ str(informe_id)+" fue eliminado correctamente")    

    return redirect('listado_informes')

@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Fonoaudiologo'])
def analisis_estadistico_profe(request, informe_id):

    tipo_usuario = None
    plot_div = None
    hay_pautas_terapeuticas = True  

    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario
        plot_div = generar_grafico(informe_id)

    if hay_pautas_terapeuticas:
        return render(request, 'vista_profe/analisis_estadistico_profe.html', 
                      {'tipo_usuario': tipo_usuario,
                       'informe_id': informe_id,
                       'plot_div': plot_div})
    else:
        mensaje_error = "No hay pautas terapéuticas para analizar. Ingrese una para analizar el tratamiento del paciente."
        return render(request, 'vista_profe/analisis_estadistico_profe.html', 
                      {'tipo_usuario': tipo_usuario,
                       'informe_id': informe_id,
                       'mensaje_error': mensaje_error})

##Detalles por paciente de los fonoaudiologos
@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Fonoaudiologo'])
def detalle_prof_paci(request, paciente_id):

    paciente = get_object_or_404(Usuario, id_usuario=paciente_id, id_tp_usuario__tipo_usuario='Paciente')
    traer_paciente = paciente.paciente

    obtener_rasati = Rasati.objects.filter(id_informe__fk_relacion_pa_pro__id_paciente=traer_paciente)
    obtener_grbas = Grbas.objects.filter(id_informe__fk_relacion_pa_pro__id_paciente=traer_paciente)

    informes_rasati = obtener_rasati 
    informes_grbas = obtener_grbas    

    tipo_usuario = None
    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

        paciente = get_object_or_404(Usuario, id_usuario=paciente_id, id_tp_usuario__tipo_usuario='Paciente')
        paciente_info = paciente.paciente

        edad_paciente = paciente.fecha_nacimiento

        fecha_nacimiento = edad_paciente
        if fecha_nacimiento:
            hoy = datetime.today()
            edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
        else:
            edad = None


    fonoaudiologos_asociados = ProfesionalSalud.objects.filter(relacionpapro__id_paciente=paciente_info.id_paciente)

    return render(request, 'vista_profe/detalle_prof_paci.html', {'paciente': paciente, 
                                                                 'tipo_usuario': tipo_usuario,
                                                                 'paciente_info': paciente_info,
                                                                 'fonoaudiologos_asociados': fonoaudiologos_asociados,
                                                                 'informes_rasati': informes_rasati,
                                                                 'informes_grbas': informes_grbas,
                                                                 'edad': edad,
                                                                 })

def enviar_correo_paciente(paciente, profesional_salud):
    usuario_paciente = Usuario.objects.get(paciente=paciente)

    subject = '¡Bienvenido a RTDF!'
    from_email = 'permify.practica@gmail.com'
    recipient_list = [usuario_paciente.email]

    context = {'paciente': paciente, 'profesional_salud': profesional_salud}
    
    html_content = render_to_string('correos/bienvenida_paciente.html', context)
    
    email = EmailMessage(subject, html_content, from_email, recipient_list)
    email.content_subtype = 'html'
    
    email.send()




@never_cache   
def desvincular_paciente(request, paciente_id):

    paciente = get_object_or_404(Paciente, id_paciente=paciente_id)
    profesional_salud = request.user.profesionalsalud

    relacion = RelacionPaPro.objects.filter(fk_profesional_salud=profesional_salud, id_paciente=paciente)
    
    if relacion.exists():
        relacion.delete()
        messages.success(request, "Desvinculado correctamente.")
        return redirect('listado_pacientes')
    else:
        return redirect('listado_pacientes')
    

@never_cache
@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Fonoaudiologo'])
def detalle_prof_pauta(request, id_pauta_terapeutica_id):

    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

        #print(tipo_usuario)

        pauta = get_object_or_404(PautaTerapeutica, id_pauta_terapeutica=id_pauta_terapeutica_id)

        if tipo_usuario == 'Admin':
            url_regreso = reverse('detalle_prof_infor', kwargs={'informe_id': pauta.fk_informe.id_informe})
        elif tipo_usuario == 'Fonoaudiologo':
            url_regreso = reverse('detalle_prof_infor', kwargs={'informe_id': pauta.fk_informe.id_informe})
        else:
            url_regreso = reverse('detalle_prof_infor', kwargs={'informe_id': pauta.fk_informe.id_informe})

        

        try:
            intensidad = Intensidad.objects.get(id_pauta_terapeutica=pauta)
        except Intensidad.DoesNotExist:
            intensidad = None

        try:
            vocalizacion = Vocalizacion.objects.get(id_pauta_terapeutica=pauta)
        except Vocalizacion.DoesNotExist:
            vocalizacion = None

    paciente_relacionado = pauta.fk_informe.fk_relacion_pa_pro.id_paciente

    return render(request, 'vista_profe/detalle_prof_pauta.html', {
        'tipo_usuario': tipo_usuario,
        'pauta' : pauta, 
        'intensidad' : intensidad,
        'vocalizacion': vocalizacion,
        'paciente_relacionado': paciente_relacionado,
        'url_regreso': url_regreso,

    })

@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Fonoaudiologo'])
def detalle_audio_profe(request, audio_id):
    tipo_usuario = None
    graph_html =None
    graph_frecuencias = None
    graph_intensidad = None
    graph_jitter = None
    graph_shimmer = None
    
    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario


        audio = Audio.objects.get(id_audio=audio_id)
        audio_coeficiente_automatico = Audioscoeficientes.objects.filter(id_audio=audio_id,fk_tipo_llenado='1').first()
        audio_coeficiente_manual = Audioscoeficientes.objects.filter(id_audio=audio_id,fk_tipo_llenado='2').first()


        print(audio_coeficiente_manual)


        
        x = ['f0', 'f1', 'f2', 'f3', 'f4', 'intensidad', 'hnr', 'local_jitter', 'local_absolute_jitter',
            'rap_jitter', 'ppq5_jitter', 'ddp_jitter', 'local_shimmer', 'local_db_shimmer', 'apq3_shimmer',
            'aqpq5_shimmer', 'apq11_shimmer']


        y_auto = convertir_a_numeros(audio_coeficiente_automatico)

        if audio_coeficiente_manual:
            y_manual = convertir_a_numeros(audio_coeficiente_manual)

            
            #graph_html = generar_grafico_audio(x, y_auto, y_manual) 

            graph_frecuencias = grafico_frecuencias(x, y_auto, y_manual) 
            graph_intensidad = grafico_intensidad(x, y_auto, y_manual)
            graph_jitter = grafico_jitter(x, y_auto, y_manual)
            graph_shimmer = grafico_shimmer(x, y_auto, y_manual)

        audio_dicc = {
            'id_audio': audio.id_audio,
            'fecha_audio': audio.fecha_audio,
            'id_pauta': audio.fk_pauta_terapeutica_id,
            'id_origen': audio.fk_origen_audio,
            'rut_paciente': audio.fk_pauta_terapeutica.fk_informe.fk_relacion_pa_pro.id_paciente.id_usuario.numero_identificacion,
            'primer_nombre_paciente': audio.fk_pauta_terapeutica.fk_informe.fk_relacion_pa_pro.id_paciente.id_usuario.primer_nombre,
            'ap_paterno_paciente': audio.fk_pauta_terapeutica.fk_informe.fk_relacion_pa_pro.id_paciente.id_usuario.ap_paterno,
            'tipo_profesional': audio.fk_pauta_terapeutica.fk_informe.fk_relacion_pa_pro.fk_profesional_salud.id_usuario.id_tp_usuario,
            'primer_nombre_profesional':audio.fk_pauta_terapeutica.fk_informe.fk_relacion_pa_pro.fk_profesional_salud.id_usuario.primer_nombre,
            'ap_paterno_profesional':audio.fk_pauta_terapeutica.fk_informe.fk_relacion_pa_pro.fk_profesional_salud.id_usuario.ap_paterno,
            #Relacion con
            'nombre_audio': audio_coeficiente_automatico.nombre_archivo if audio_coeficiente_automatico else None
        }
        


    return render(request, 'vista_profe/detalle_audio_profe.html', {
        'tipo_usuario': tipo_usuario,
        'detalle_audio': audio_dicc,
        'coef_auto': audio_coeficiente_automatico,
        'coef_manual': audio_coeficiente_manual,
        'graph_html': graph_html,
        'graph_frecuencias': graph_frecuencias,
        'graph_intensidad': graph_intensidad,
        'graph_jitter': graph_jitter,
        'graph_shimmer': graph_shimmer,
    })

@user_passes_test(validate)
@never_cache
@tipo_usuario_required(allowed_types=['Fonoaudiologo'])
def ingresar_coef_profe(request, audio_id):

    tipo_usuario = None
    audio = Audio.objects.get(id_audio=audio_id)
    timestamp=datetime.today()
    fecha_audio= timestamp.strftime('%Y-%m-%d %H:%M')
    tp_llenado= TpLlenado.objects.get(id_tipo_llenado=2)
    audio_coeficiente_manual = Audioscoeficientes.objects.filter(id_audio=audio_id,fk_tipo_llenado='2').first()
    

    #desconcatenacion del url del audio

    audio_url = audio.url_audio
    parts = audio_url.split('/')
    if len(parts) > 1:
        nombre_audio = parts[1]
    else:
        nombre_audio = audio_url

    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

        if request.method == 'POST':
            form = AudioscoeficientesForm(request.POST)

           

            # form.fields['nombre_archivo'].initial = nombre_audio
            # form.fields['fecha_coeficiente'].initial = timezone.now()  # Establece la fecha y hora en el formato correcto
            # tp_llenado= TpLlenado.objects.get(id_tipo_llenado=2)
            # form.instance.fk_tipo_llenado = tp_llenado.id_tipo_llenado
            # ##print(tp_llenado.id_tipo_llenado)
            # id_wav= Audio.objects.get(id_audio=audio_id)
            # # print (id_wav)
            # form.instance.id_audio = id_wav


            # form.fk_tipo_llenado = nombre_audio
            # form.id_audio = audio
            # form.fecha_coeficiente = timezone.now()
            

            if form.is_valid():

                informe = form.save(commit=False)  # No guardes inmediatamente en la base de datos
                informe.fk_tipo_llenado = tp_llenado  # Asigna el valor a través del objeto informe
                informe.id_audio = audio
                informe.fecha_coeficiente = timezone.now()
                informe.save()  # Ahora guarda en la base de dato

                messages.success(request, "Coeficiente manual ingresado correctamente")
                return redirect('detalle_audio_profe', audio_id)
        else:
            form = AudioscoeficientesForm(initial={'fecha_coeficiente': timezone.now(),
                                                   'nombre_archivo': nombre_audio,
                                                   'fk_tipo_llenado': tp_llenado,
                                                    'id_audio': audio })

    return render(request, 'vista_profe/ingresar_coef_profe.html', {
    'tipo_usuario': tipo_usuario,
    'form': form,
    'id_audio': audio_id,
    'coef_manual': audio_coeficiente_manual,
    })


def reproducir_audio(request, audio_id):

    audio = Audio.objects.get(id_audio=audio_id)
    # Ruta del audio
    audio_path = os.path.join(settings.MEDIA_ROOT, 'audios_pacientes' , audio.url_audio)
    #Despliegue del audio
    return FileResponse(open(audio_path, 'rb'), content_type='audio/wav')

@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Fonoaudiologo'])
def eliminar_coef_manual(request, audiocoeficientes_id):

    coef_manual = get_object_or_404(Audioscoeficientes, id_audiocoeficientes=audiocoeficientes_id)

    id_audio = coef_manual.id_audio_id

    coef_manual.delete()

    messages.success(request, "Coeficiente manual N°" + str(audiocoeficientes_id) + " eliminado correctamente")
    return redirect('detalle_audio_profe', audio_id=id_audio)

@never_cache
@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Fonoaudiologo'])
def editar_coef_manual(request, audiocoeficientes_id):
    tipo_usuario = None
    
    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

        coef_manual = get_object_or_404(Audioscoeficientes, id_audiocoeficientes=audiocoeficientes_id)
        tp_llenado = coef_manual.fk_tipo_llenado
        fecha = coef_manual.fecha_coeficiente
        id_audio = coef_manual.id_audio_id
        audio = Audio.objects.get(id_audio=id_audio)

        if request.method == 'POST':
            form = AudioscoeficientesForm(request.POST, instance=coef_manual)

            if form.is_valid():
                informe = form.save(commit=False)
                informe.fk_tipo_llenado = tp_llenado  
                informe.id_audio = audio
                informe.fecha_coeficiente = fecha
                informe.save() 

                messages.success(request, "Coeficiente manual N°" + str(audiocoeficientes_id) + " editada correctamente")
                return redirect('detalle_audio_profe', audio_id=id_audio)
            
        else:
            form = AudioscoeficientesForm(instance=coef_manual)
    
    return render(request, 'vista_profe/editar_coef_manual.html', 
                      {'form': form, 
                     'tipo_usuario': tipo_usuario,
                     'id_audio': id_audio})


@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Fonoaudiologo'])
def eliminar_audio_prof(request, audio_id):

    audio_registro = get_object_or_404(Audio, id_audio=audio_id)

    ruta = audio_registro.url_audio

    os.remove(os.path.join(settings.MEDIA_ROOT, 'audios_pacientes', ruta))

    audio_registro.delete()

    messages.success(request, "Audio N°" + str(audio_id) + " eliminado correctamente")
    return redirect('analisis_profe')


@never_cache
@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Fonoaudiologo'])
def editar_prof_pauta(request, id_pauta_terapeutica_id):
 
    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

        pauta = get_object_or_404(PautaTerapeutica, id_pauta_terapeutica=id_pauta_terapeutica_id)
        profesional_salud = request.user.profesionalsalud
        relaciones_pacientes = RelacionPaPro.objects.filter(fk_profesional_salud=profesional_salud)

        tipo_pauta=pauta.fk_tp_terapia.tipo_terapia

        intensidad_form = None
        vocalizacion_form = None

        try:
            if pauta.intensidad:
                intensidad_form = IntensidadForm(request.POST or None, instance=pauta.intensidad, tipo_pauta=tipo_pauta)
        except Intensidad.DoesNotExist:
            intensidad_form = IntensidadForm()

        try:
            if pauta.vocalizacion:
                vocalizacion_form = VocalizacionForm(request.POST or None, instance=pauta.vocalizacion, tipo_pauta=tipo_pauta)
        except Vocalizacion.DoesNotExist:
            vocalizacion_form = VocalizacionForm()

        if request.method == 'POST':
            form = PautaTerapeuticaForm(request.POST, instance=pauta)

            if form.is_valid():
                form.save()

            if intensidad_form and intensidad_form.is_valid():

                if not intensidad_form.cleaned_data['min_db']:
                        #se setea a null
                        intensidad_form.cleaned_data['min_db'] = None

                if not intensidad_form.cleaned_data['max_db']:
                        intensidad_form.cleaned_data['max_db'] = None  

                #antes de guardar el formulario se setea el campo de min db y max db
                intensidad_form.instance.min_db = intensidad_form.cleaned_data['min_db']
                intensidad_form.instance.max_db = intensidad_form.cleaned_data['max_db'] 

                
                intensidad = intensidad_form.save(commit=False)

                intensidad.save()

            if vocalizacion_form and vocalizacion_form.is_valid():
                vocalizacion_form.save()

            messages.success(request, "Pauta N°" + str(id_pauta_terapeutica_id) + " editada correctamente")
            return redirect('detalle_prof_pauta', id_pauta_terapeutica_id=pauta.id_pauta_terapeutica)
        else:
            form = PautaTerapeuticaForm(instance=pauta)


    return render(request, 'vista_profe/editar_prof_pauta.html', {
        'tipo_usuario': tipo_usuario,
        'pauta': pauta,
        'form': form, 
        'intensidad_form': intensidad_form,
        'vocalizacion_form': vocalizacion_form,


    })

@never_cache
@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Fonoaudiologo'])
def eliminar_prof_pauta(request, id_pauta_terapeutica_id):

    pauta = get_object_or_404(PautaTerapeutica, id_pauta_terapeutica=id_pauta_terapeutica_id)
    tipo_pauta = pauta.fk_tp_terapia

    if tipo_pauta == 'Intensidad':
        pauta.intensidad.delete()
    elif tipo_pauta == 'Vocalización':
        pauta.vocalizacion.delete()

    pauta.delete()

    messages.success(request, "Pauta N°" + str(id_pauta_terapeutica_id) + " eliminada correctamente")
    return redirect('detalle_prof_infor', informe_id=pauta.fk_informe.id_informe)

@never_cache
@tipo_usuario_required(allowed_types=['Fonoaudiologo'])
@user_passes_test(validate)
def listado_informes(request):
    # Fonoaudiologo de la sesion
    profesional_medico = request.user.profesionalsalud

    # Filtro por fonoaudiologo 
    informes = Informe.objects.filter(fk_relacion_pa_pro__fk_profesional_salud=profesional_medico).annotate(
    num_pautas_terapeuticas=Count('pautaterapeutica')).order_by('-fecha')

    informes_por_pagina = 10

    paginator = Paginator(informes, informes_por_pagina)

    page_number = request.GET.get('page')

    page = paginator.get_page(page_number)

    tipo_usuario = None
    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

    return render(request, 'vista_profe/listado_informes.html', {'informes': informes,
                                                                 'tipo_usuario': tipo_usuario,
                                                                 'page': page})
    

@never_cache 
@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Fonoaudiologo'])   
def pacientes_disponibles(request):
    tipo_usuario = None 

    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

        pacientes_disponibles = Paciente.objects.filter(relacionpapro__isnull=True)

        return render(request, 'vista_profe/pacientes_disponibles.html', {'tipo_usuario': tipo_usuario, 
                                                                          'pacientes_disponibles': pacientes_disponibles})

@never_cache
@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Fonoaudiologo'])
def agregar_paciente(request, paciente_id):
    if request.user.is_authenticated and request.user.id_tp_usuario.tipo_usuario == 'Fonoaudiologo':
        profesional_salud = request.user.profesionalsalud
        paciente = Paciente.objects.get(pk=paciente_id)
        
        if RelacionPaPro.objects.filter(fk_profesional_salud=profesional_salud).count() < 10:

            if not RelacionPaPro.objects.filter(id_paciente=paciente).exists():

                relacion = RelacionPaPro(fk_profesional_salud=profesional_salud, id_paciente=paciente)
                relacion.save()

                enviar_correo_paciente(paciente, profesional_salud)

                messages.success(request, "Paciente vinculado correctamente")
                return redirect('listado_pacientes')
            else:
                return render(request, 'vista_profe/error.html', {'error_message': 'El paciente ya está asignado a otro profesional.'})
        else:
            return render(request, 'vista_profe/error.html', {'error_message': 'Has alcanzado el límite de 10 pacientes asignados.'})
    else:
        return render(request, 'vista_profe/error.html', {'error_message': 'No tienes permiso para realizar esta acción.'})

@user_passes_test(validate)
@never_cache
@tipo_usuario_required(allowed_types=['Fonoaudiologo'])
def detalle_prof_infor(request, informe_id):

    source = request.GET.get('source')

    if source == 'plantilla1':
        url_regreso = reverse('detalle_prof_paci')
    elif source == 'plantilla2':
        url_regreso = reverse('listado_informes')
    else:
        url_regreso = reverse('listado_informes')


    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario
    informe = get_object_or_404(Informe, id_informe=informe_id)

    try:
        grbas = Grbas.objects.get(id_informe=informe)
    except Grbas.DoesNotExist:
        grbas = None

    try:
        rasati = Rasati.objects.get(id_informe=informe)
    except Rasati.DoesNotExist:
        rasati = None

    datos_vocalizacion = Vocalizacion.objects.filter(id_pauta_terapeutica__fk_informe=informe_id,id_pauta_terapeutica__fk_tp_terapia= 1)    
    datos_intensidad = Intensidad.objects.filter(id_pauta_terapeutica__fk_informe=informe_id,id_pauta_terapeutica__fk_tp_terapia= 2)

    paciente_relacionado = informe.fk_relacion_pa_pro.id_paciente

    tipo_usuario = None
    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

        if request.method == 'POST':

            #guardo la pk del informe del detalle_informe
            informe = Informe.objects.get(pk=informe_id)
            form = PautaTerapeuticaForm(request.POST)
            vocalizacion_form = VocalizacionForm(request.POST)
            intensidad_form = IntensidadForm(request.POST)

            if form.is_valid() and vocalizacion_form.is_valid() and intensidad_form.is_valid():
                pauta_terapeutica = form.save(commit=False) #guardo el form para agregar el id informe manualmente
                pauta_terapeutica.fk_informe = informe # le paso la pk del informe
                pauta_terapeutica.save()

                tipo_terapia = str(form.cleaned_data['fk_tp_terapia']).strip()

                # asociar el informe con VOCALIZACION O INTENSIDAD
                if tipo_terapia == 'Vocalización':
                    
                    vocalizacion = vocalizacion_form.save(commit=False)
                    vocalizacion.id_pauta_terapeutica = pauta_terapeutica
                    vocalizacion.save()

                elif tipo_terapia == 'Intensidad':
                        
                    #se obtiene en valor del campo validado del form y se compara que este vacio    
                    if not intensidad_form.cleaned_data['min_db']:
                        #se setea a null
                        intensidad_form.cleaned_data['min_db'] = None

                    if not intensidad_form.cleaned_data['max_db']:
                        intensidad_form.cleaned_data['max_db'] = None   

                    #antes de guardar el formulario se setea el campo de min db y max db
                    intensidad_form.instance.min_db = intensidad_form.cleaned_data['min_db']
                    intensidad_form.instance.max_db = intensidad_form.cleaned_data['max_db']

                    intensidad = intensidad_form.save(commit=False)
                    intensidad.id_pauta_terapeutica = pauta_terapeutica
                    intensidad.save()    
                
                messages.success(request, "Pauta ingresada correctamente")  

                return redirect('detalle_prof_infor', informe_id=informe.id_informe)
        

        else:
            # Si la solicitud no es POST, muestra el formulario en blanco
            form = PautaTerapeuticaForm()
            form.fields['fk_tp_terapia'].required = True
            vocalizacion_form = VocalizacionForm()
            intensidad_form = IntensidadForm()

        return render(request, 'vista_profe/detalle_prof_infor.html', {
            'form': form,
            'vocalizacion_form': vocalizacion_form,
            'intensidad_form': intensidad_form,
            'datos_intensidad': datos_intensidad,
            'informe': informe,
            'datos_vocalizacion': datos_vocalizacion,
            'grbas': grbas,
            'rasati': rasati,
            'paciente_relacionado': paciente_relacionado,
            'tipo_usuario': tipo_usuario,
            'url_regreso': url_regreso,
        })
    
    else:
        return redirect('vista_profe/index.html')

# FIN DE VISTAS DE PROFESIONALES ------------------------------------------------------------------------------->

# VISTAS DE ADMINISTRADOR ------------------------------------------------------------------------------->
@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Admin'])
def listado_preregistros(request):

    tipo_usuario = None 

    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario
        pre_registrados = PreRegistro.objects.filter(validado='0').order_by('-id_pre_registro')
        validados = PreRegistro.objects.filter(validado='1').order_by('-id_pre_registro')


        elementos_por_pagina = 5  

        paginator = Paginator(pre_registrados, elementos_por_pagina)
        paginator2 = Paginator(validados, elementos_por_pagina)


        page = request.GET.get('page')

        #PAGINATOR 1
        try:
            pre_registrados = paginator.page(page)
            
        except PageNotAnInteger:
           
            pre_registrados = paginator.page(1)
        except EmptyPage:

            pre_registrados = paginator.page(paginator.num_pages)

        #PAGINATOR 2
        try:
            validados = paginator2.page(page)
        except PageNotAnInteger:
            
            validados = paginator2.page(1)
        except EmptyPage:

            validados = paginator2.page(paginator.num_pages)


    return render(request, 'vista_admin/listado_preregistros.html', 
                  {'tipo_usuario': tipo_usuario,
                   'pre_registrados': pre_registrados,
                   'validados': validados,
                     })

@never_cache
@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Admin'])
def detalle_preregistro(request, preregistro_id):

    tipo_usuario = None 
    registro_precargado = None

    # se verifica que el usuario este registrado como profesional salud
    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario
        id_admin = request.user.id_usuario
        nombre_admin = None
        fecha_validacion = None

        pre_registro = PreRegistro.objects.get(id_pre_registro=preregistro_id)


        if pre_registro.validado == '1':
            validacion = Validacion.objects.get(id_pre_registro=preregistro_id)
            nombre_admin = f"{validacion.id_usuario.primer_nombre} {validacion.id_usuario.segundo_nombre if validacion.id_usuario.segundo_nombre is not None else ''} {validacion.id_usuario.ap_paterno} {validacion.id_usuario.ap_materno if validacion.id_usuario.ap_materno is not None else ''}"
            fecha_validacion = validacion.fecha_validacion


        nombre_completo = f"{pre_registro.primer_nombre} {pre_registro.segundo_nombre} {pre_registro.ap_paterno} {pre_registro.ap_materno}"
        
        
        pre_dicc = {
            'id_preregistro': pre_registro.id_pre_registro,
            'rut': pre_registro.numero_identificacion,
            'primer_nombre': pre_registro.primer_nombre,
            'segundo_nombre': pre_registro.segundo_nombre,
            'ap_paterno': pre_registro.ap_paterno,
            'ap_materno': pre_registro.ap_materno,
            'fecha_nacimiento': pre_registro.fecha_nacimiento,
            'email': pre_registro.email,
            'contraseña': pre_registro.password,
            'celular': pre_registro.numero_telefonico,
            'validado': pre_registro.validado,
            'comuna': pre_registro.id_comuna,
            'rol': pre_registro.id_tp_usuario,
            'intitucion': pre_registro.id_institucion,
            'nombre_completo': nombre_completo,
            'admin': nombre_admin,
            'fecha_validacion': fecha_validacion,
        }

        numero_identificacion= pre_dicc['rut']
        #print(pre_dicc['rut'])

        # se divide el número de identificación en dos partes: antes y después del guión
        partes = numero_identificacion.split('-')
        numero_parte_antes_del_guion = partes[0]
        numero_parte_despues_del_guion = partes[1]

        # formateo de  la parte antes del guion
        numero_parte_antes_del_guion = '{:,}'.format(int(numero_parte_antes_del_guion.replace('.', ''))).replace(',', '.')

        # se concatena las dos partes
        numero_identificacion_formateado = f'{numero_parte_antes_del_guion}-{numero_parte_despues_del_guion}'

        #print(numero_identificacion_formateado)

        try:
            registro_precargado = Registros.objects.get(numero_identificacion=numero_identificacion_formateado)
            print(registro_precargado)          
        except Registros.DoesNotExist:
            print("El registro no fue encontrado en la base de datos.")
        except Exception as e:
            print(f"Ocurrió un error al buscar el registro: {e}")

        if request.method == 'POST':
            pre_registro = PreRegistro.objects.get(id_pre_registro=preregistro_id)

            usuario = Usuario.objects.create(
                numero_identificacion=pre_registro.numero_identificacion,
                primer_nombre=pre_registro.primer_nombre,
                segundo_nombre=pre_registro.segundo_nombre,
                ap_paterno= pre_registro.ap_paterno,
                ap_materno= pre_registro.ap_materno,
                fecha_nacimiento = pre_registro.fecha_nacimiento,
                email = pre_registro.email,
                password = make_password(pre_registro.password),
                numero_telefonico = pre_registro.numero_telefonico,
                id_tp_usuario = pre_registro.id_tp_usuario,
                id_comuna = pre_registro.id_comuna,
            )

            profesional_salud = ProfesionalSalud.objects.create(
                # titulo_profesional=pre_registro.titulo_profesional,
                id_institucion=pre_registro.id_institucion,
                id_usuario=usuario
            )            

            pre_registro.validado = 1
            pre_registro.save()

            id_admin = request.user.id_usuario
            admin_usuario = Usuario.objects.get(id_usuario=id_admin)

            # registro en la tabla Validacion
            validacion = Validacion.objects.create(
                id_pre_registro=pre_registro,
                id_usuario=admin_usuario,
                fecha_validacion=timezone.now()
            )

            #print(usuario.email)
            # Enviar correo al usuario registrado
            subject = 'Pre-Registro confirmado'
            from_email = 'permify.practica@gmail.com'
            recipient_list = [usuario.email]
            context = {'usuario': usuario, 'profesional_salud': profesional_salud, 'validacion': validacion, 'pre_registro': pre_registro}  # Datos para la plantilla

            # contenido del correo
            html_content = render_to_string('correos/confirmacion_preregistro.html', context)
            email = EmailMessage(subject, html_content, from_email, recipient_list)
            email.content_subtype = 'html' 

            email.send()



            messages.success(request, "Pre-registro N°" + str(preregistro_id) + " validado correctamente. Correo enviado al usuario " + usuario.primer_nombre + " " + usuario.ap_paterno)
            return redirect('detalle_preregistro', preregistro_id )

    return render(request, 'vista_admin/detalle_preregistro.html', 
                  {'tipo_usuario': tipo_usuario,
                   'pre_registro': pre_dicc,
                   'registro_precargado':  registro_precargado,
                     })


##LISTADO DE LOS PACIENTES PARA ADMINSITRADOR


@user_passes_test(validate)
@never_cache
@tipo_usuario_required(allowed_types=['Admin'])
def list_paci_admin(request):
    pacientes = Usuario.objects.filter(id_tp_usuario__tipo_usuario='Paciente')
    tipo_usuario = None
    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario
    return render(request, 'vista_admin/list_paci_admin.html',{'tipo_usuario': tipo_usuario, 'pacientes': pacientes})


@never_cache
@user_passes_test(validate)  
@tipo_usuario_required(allowed_types=['Admin'])
def detalle_paciente(request, paciente_id):
    paciente = get_object_or_404(Usuario, id_usuario=paciente_id, id_tp_usuario__tipo_usuario='Paciente')
    traer_paciente = paciente.paciente

    fonoaudiologos_asociados = ProfesionalSalud.objects.filter(relacionpapro__id_paciente=traer_paciente.id_paciente)

    obtener_rasati = Rasati.objects.filter(id_informe__fk_relacion_pa_pro__id_paciente=traer_paciente)
    obtener_grbas = Grbas.objects.filter(id_informe__fk_relacion_pa_pro__id_paciente=traer_paciente)
    obtener_esv = Esv.objects.filter(id_informe__fk_relacion_pa_pro__id_paciente=traer_paciente)

    # Calcular la edad del paciente
    fecha_nacimiento = paciente.fecha_nacimiento
    if fecha_nacimiento:
        hoy = date.today()
        edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
    else:
        edad = None

    tipo_usuario = None
    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

    informes_rasati = obtener_rasati 
    informes_grbas = obtener_grbas    
    informes_esv= obtener_esv

    return render(request, 'vista_admin/detalle_paciente.html', {
        'paciente': paciente,
        'tipo_usuario': tipo_usuario,
        'paciente_info': traer_paciente,
        'fonoaudiologos_asociados': fonoaudiologos_asociados,
        'informes_esv': informes_esv,
        'informes_rasati': informes_rasati,
        'informes_grbas': informes_grbas,
        'edad': edad,  
    })

##LISTADO DE LOS FONOAUDIOLOGOS PARA ADMINSITRADOR

@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Admin'])
def list_fono_admin(request):
    fonoaudiologos = Usuario.objects.filter(id_tp_usuario__tipo_usuario='Fonoaudiologo')
    tipo_usuario = None
    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario
    return render(request, 'vista_admin/list_fono_admin.html', {'tipo_usuario': tipo_usuario, 'fonoaudiologos': fonoaudiologos})

@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Admin'])
def detalle_fonoaudiologo(request, fonoaudiologo_id):

    fonoaudiologo = get_object_or_404(Usuario, id_usuario=fonoaudiologo_id, id_tp_usuario__tipo_usuario='Fonoaudiólogo')

    fecha_nacimiento = fonoaudiologo.fecha_nacimiento
    if fecha_nacimiento:
        hoy = date.today()
        edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
    else:
        edad = None

    profesional_salud = ProfesionalSalud.objects.get(id_usuario=fonoaudiologo)

    institucion = ProfesionalSalud.objects.get(id_usuario=fonoaudiologo).id_institucion

    relaciones = RelacionPaPro.objects.filter(fk_profesional_salud=profesional_salud)

    pacientes_asociados = [relacion.id_paciente for relacion in relaciones]

    tipo_usuario = None
    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario
    return render(request, 'vista_admin/detalle_fonoaudiologo.html', {'fonoaudiologo': fonoaudiologo, 
                                                                      'tipo_usuario': tipo_usuario,
                                                                      'pacientes_asociados': pacientes_asociados,
                                                                      'profesional_salud': profesional_salud,
                                                                      'institucion': institucion,
                                                                      'edad': edad })

##LISTADO PARA NEUROLOGOS PARA ADMINSITRADOR

@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Admin'])
def list_neur_admin(request):
    neurologos = Usuario.objects.filter(id_tp_usuario__tipo_usuario='Neurologo')
    
    tipo_usuario = None 
    usuarios = Usuario.objects.all()
    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

    return render(request, 'vista_admin/list_neur_admin.html', {'tipo_usuario': tipo_usuario, 
                                                                'usuario': usuarios,
                                                                'neurologos': neurologos})

@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Admin'])
def detalle_neurologo(request, neurologo_id):

    neurologo = get_object_or_404(Usuario, id_usuario=neurologo_id, id_tp_usuario__tipo_usuario='Neurologo')

    profesional_salud = ProfesionalSalud.objects.get(id_usuario=neurologo)

    institucion = ProfesionalSalud.objects.get(id_usuario=neurologo).id_institucion

    relaciones = RelacionPaPro.objects.filter(fk_profesional_salud=profesional_salud)

    pacientes_asociados = [relacion.id_paciente for relacion in relaciones]

    fecha_nacimiento = neurologo.fecha_nacimiento
    if fecha_nacimiento:
        hoy = date.today()
        edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
    else:
        edad = None

    tipo_usuario = None
    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario
    return render(request, 'vista_admin/detalle_neurologo.html', {  'neurologo': neurologo, 
                                                                    'tipo_usuario': tipo_usuario,
                                                                    'pacientes_asociados': pacientes_asociados,
                                                                    'profesional_salud': profesional_salud,
                                                                    'institucion': institucion,
                                                                    'edad': edad})

##LISTADO PARA FAMILIARES PARA VISTA DE ADMINISTRADOR

@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Admin'])
def list_fami_admin(request):
    familiar = Usuario.objects.filter(id_tp_usuario__tipo_usuario='Familiar')
    
    tipo_usuario = None 
    usuarios = Usuario.objects.all()
    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

    return render(request, 'vista_admin/list_fami_admin.html', {'tipo_usuario': tipo_usuario, 
                                                                'usuario': usuarios,
                                                                'familiar': familiar})

@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Admin'])
def detalle_familiar_admin(request, familiar_id):
    familiar = get_object_or_404(Usuario, id_usuario=familiar_id, id_tp_usuario__tipo_usuario='Familiar')

    fecha_nacimiento = familiar.fecha_nacimiento
    if fecha_nacimiento:
        hoy = date.today()
        edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
    else:
        edad = None

    familiar_paciente = FamiliarPaciente.objects.get(id_usuario=familiar)
    parentesco = familiar_paciente.fk_tipo_familiar

    relacion_fp = RelacionFp.objects.filter(fk_familiar_paciente=familiar_paciente).first()
    paciente_asociado = relacion_fp.id_paciente if relacion_fp else None


    tipo_usuario = None
    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

    return render(request, 'vista_admin/detalle_familiar_admin.html', {
                                                                'familiar': familiar, 
                                                                'tipo_usuario': tipo_usuario,
                                                                'parentesco': parentesco,
                                                                'paciente_asociado': paciente_asociado,
                                                                'edad': edad
                                                            })

@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Admin'])
def eliminar_informe_admin(request, informe_id):
    informe = get_object_or_404(Informe, id_informe=informe_id)
    tipo_informe = informe.tp_informe

    if tipo_informe == 'GRBAS':
        informe.grbas.delete()
    elif tipo_informe == 'RASATI':
        informe.rasati.delete()

    informe.delete()
    messages.success(request, "Informe N°" + str(informe_id) + " eliminado correctamente")
    return redirect('detalle_paciente', paciente_id=informe.fk_relacion_pa_pro.id_paciente.id_usuario.id_usuario)

@never_cache
@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Admin'])
def detalle_informe(request, informe_id):

    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

        informe = get_object_or_404(Informe, id_informe=informe_id)

        try:
            grbas = Grbas.objects.get(id_informe=informe)
        except Grbas.DoesNotExist:
            grbas = None

        try:
            rasati = Rasati.objects.get(id_informe=informe)
        except Rasati.DoesNotExist:
            rasati = None

        datos_vocalizacion = Vocalizacion.objects.filter(id_pauta_terapeutica__fk_informe=informe_id,id_pauta_terapeutica__fk_tp_terapia= 1)    
        datos_intensidad = Intensidad.objects.filter(id_pauta_terapeutica__fk_informe=informe_id,id_pauta_terapeutica__fk_tp_terapia= 2)

        paciente_relacionado = informe.fk_relacion_pa_pro.id_paciente

        if request.method == 'POST':

            #guardo la pk del informe del detalle_informe
            informe = Informe.objects.get(pk=informe_id)
            form = PautaTerapeuticaForm(request.POST)
            vocalizacion_form = VocalizacionForm(request.POST)
            intensidad_form = IntensidadForm(request.POST)

            if form.is_valid() and vocalizacion_form.is_valid() and intensidad_form.is_valid():
                pauta_terapeutica = form.save(commit=False) #guardo el form para agregar el id informe manualmente
                pauta_terapeutica.fk_informe = informe # le paso la pk del informe
                pauta_terapeutica.save()

                tipo_terapia = str(form.cleaned_data['fk_tp_terapia']).strip()

                # asociar el informe con VOCALIZACION O INTENSIDAD
                if tipo_terapia == 'Vocalización':
                    
                    vocalizacion = vocalizacion_form.save(commit=False)
                    vocalizacion.id_pauta_terapeutica = pauta_terapeutica
                    vocalizacion.save()

                elif tipo_terapia == 'Intensidad':
                    
                    if not intensidad_form.cleaned_data['min_db']:
                        #se setea a null
                        intensidad_form.cleaned_data['min_db'] = None

                    if not intensidad_form.cleaned_data['max_db']:
                        intensidad_form.cleaned_data['max_db'] = None   

                    #antes de guardar el formulario se setea el campo de min db y max db
                    intensidad_form.instance.min_db = intensidad_form.cleaned_data['min_db']
                    intensidad_form.instance.max_db = intensidad_form.cleaned_data['max_db']

                    intensidad = intensidad_form.save(commit=False)
                    intensidad.id_pauta_terapeutica = pauta_terapeutica
                    intensidad.save()    

                messages.success(request, "Pauta " + tipo_terapia + " ingresada correctamente")
                return redirect('detalle_informe', informe_id=informe.id_informe)
        

        else:
            # Si la solicitud no es POST, muestra el formulario en blanco
            form = PautaTerapeuticaForm()
            vocalizacion_form = VocalizacionForm()
            intensidad_form = IntensidadForm()
            form.fields['fk_tp_terapia'].required = True

    return render(request, 'vista_admin/detalle_informe.html', {
        'form': form,
        'vocalizacion_form': vocalizacion_form,
        'intensidad_form': intensidad_form,
        'datos_vocalizacion': datos_vocalizacion,
        'datos_intensidad': datos_intensidad,
        'informe': informe,
        'grbas': grbas,
        'rasati': rasati,
        'paciente_relacionado': paciente_relacionado, 
        'tipo_usuario': tipo_usuario 
    })

@never_cache
@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Admin'])
def editar_informe_admin(request, informe_id):
    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

        
        informe = get_object_or_404(Informe, id_informe=informe_id)

        pk_profesional = informe.fk_relacion_pa_pro.fk_profesional_salud
        relaciones_pacientes = RelacionPaPro.objects.filter(fk_profesional_salud=pk_profesional)

        # for relacion in relaciones_pacientes:
        #   print(relacion)

        rasati_form = None
        grbas_form = None

        try:
            if informe.rasati:
                rasati_form = RasatiForm(request.POST or None, instance=informe.rasati)
        except Rasati.DoesNotExist:
            rasati_form = RasatiForm()

        try:
            if informe.grbas:
                grbas_form = GrbasForm(request.POST or None, instance=informe.grbas)
        except Grbas.DoesNotExist:
            grbas_form = GrbasForm()

        if request.method == 'POST':
            form = InformeForm(request.POST, instance=informe)

            if form.is_valid():
                informe.fecha = timezone.now()
                form.save()

            if rasati_form and rasati_form.is_valid():
                rasati_form.save()

            if grbas_form and grbas_form.is_valid():
                grbas_form.save()

            messages.success(request, "Informe N°" + str(informe_id) + " editado correctamente")
            return redirect('detalle_informe', informe_id=informe.id_informe)
        else:
            form = InformeForm(instance=informe)
            form.fields['fk_relacion_pa_pro'].queryset = relaciones_pacientes

        return render(request, 'vista_admin/editar_informe_admin.html', {'form': form, 
                                                                        'informe': informe,
                                                                        'grbas_form': grbas_form,
                                                                        'rasati_form': rasati_form,
                                                                        'tipo_usuario': tipo_usuario})

@never_cache
@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Admin'])
def detalle_pauta_admin(request, id_pauta_terapeutica_id):

    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

        #print(tipo_usuario)

        pauta = get_object_or_404(PautaTerapeutica, id_pauta_terapeutica=id_pauta_terapeutica_id)

        if tipo_usuario == 'Admin':
            url_regreso = reverse('detalle_informe', kwargs={'informe_id': pauta.fk_informe.id_informe})
        elif tipo_usuario == 'Fonoaudiologo':
            url_regreso = reverse('detalle_prof_infor', kwargs={'informe_id': pauta.fk_informe.id_informe})
        else:
            url_regreso = reverse('detalle_prof_infor', kwargs={'informe_id': pauta.fk_informe.id_informe})   

        try:
            intensidad = Intensidad.objects.get(id_pauta_terapeutica=pauta)
        except Intensidad.DoesNotExist:
            intensidad = None

        try:
            vocalizacion = Vocalizacion.objects.get(id_pauta_terapeutica=pauta)
        except Vocalizacion.DoesNotExist:
            vocalizacion = None

    paciente_relacionado = pauta.fk_informe.fk_relacion_pa_pro.id_paciente

    return render(request, 'vista_admin/detalle_pauta_admin.html', {
        'tipo_usuario': tipo_usuario,
        'pauta' : pauta, 
        'intensidad' : intensidad,
        'vocalizacion': vocalizacion,
        'paciente_relacionado': paciente_relacionado,
        'url_regreso': url_regreso,
        })



@never_cache
@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Admin'])
def detalle_pauta_esv_admin(request, pauta_id):

    tipo_usuario = None

    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

    source = request.GET.get('source')

    if source == 'plantilla1':
        url_regreso = reverse('listado_informes')
    elif source == 'plantilla2':
        url_regreso = reverse('detalle_esv')
    else:
        url_regreso = reverse('listado_informes')

    pauta = get_object_or_404(PautaTerapeutica, pk=pauta_id)

    if pauta.fk_tp_terapia.tipo_terapia == 'Escala_vocal':
        paciente = pauta.fk_informe.fk_relacion_pa_pro.id_paciente.id_usuario
        escala_vocales = pauta.escalavocales 
        palabras = escala_vocales.palabras

        return render(request, 'vista_admin/detalle_pauta_esv_admin.html', {'pauta': pauta, 
                                                                      'palabras': palabras,
                                                                      'paciente': paciente,
                                                                      'url_regreso': url_regreso,
                                                                      'tipo_usuario': tipo_usuario})
    
@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Admin'])
def editar_pauta_esv_admin(request, pauta_id):
    tipo_usuario = None

    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario
    
    pauta = get_object_or_404(PautaTerapeutica, pk=pauta_id)
    
    if pauta.fk_tp_terapia.tipo_terapia != 'Escala_vocal':
        return render(request, 'vista_profe/error.html', {'message': 'Error: Esta pauta no es de Escala Vocal.'})

    palabras_pacientes = PalabrasPacientes.objects.all()
    palabras_pauta = pauta.escalavocales.palabras.split(', ') if pauta.escalavocales else []

    if request.method == 'POST':
        form = PautaTerapeuticaForm(request.POST, instance=pauta)

        if form.is_valid():
            form.instance.fk_tp_terapia_id = 3  
            form.save()

            palabras = []
            for i in range(1, 21):
                palabra_id = request.POST.get(f'palabra{i}', '')
                if palabra_id:
                    palabra = PalabrasPacientes.objects.get(pk=palabra_id)
                    palabras.append(palabra.palabras_paciente)

            palabras_concatenadas = ", ".join(palabras)

            if pauta.escalavocales:
                pauta.escalavocales.palabras = palabras_concatenadas
                pauta.escalavocales.save()
            else:
                escala_vocales = EscalaVocales(palabras=palabras_concatenadas)
                escala_vocales.id_pauta_terapeutica = pauta
                escala_vocales.save()

            messages.success(request, "Pauta N°" + str(pauta_id) + " editada correctamente")
            return redirect('detalle_pauta_esv_admin', pauta_id)
    else:
        form = PautaTerapeuticaForm(instance=pauta)

        selects = []
        for i in range(1, 21):
            selects.append({
                'id': i,
                'palabras_pacientes': palabras_pacientes,
                'palabra_seleccionada': palabras_pauta[i - 1] if i <= len(palabras_pauta) else None,
            })

    return render(request, 'vista_admin/editar_pauta_esv_admin.html', {
        'form': form,
        'pauta': pauta,
        'selects': selects,
        'tipo_usuario': tipo_usuario
    })

@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Admin'])
def eliminar_pauta_esv_admin(request, pauta_id):
    pauta = get_object_or_404(PautaTerapeutica, pk=pauta_id)

    if pauta.fk_tp_terapia.tipo_terapia == 'Escala_vocal':
        pauta.delete()

    messages.success(request, "Pauta ESV N°" + str(pauta_id) + " eliminada correctamente")
    return redirect('detalle_esv_admin', informe_id=pauta.fk_informe.id_informe)
    


@never_cache
@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Admin'])
def editar_pauta_admin(request, id_pauta_terapeutica_id):

    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

        pauta = get_object_or_404(PautaTerapeutica, id_pauta_terapeutica=id_pauta_terapeutica_id)
        # profesional_salud = request.user.profesionalsalud
        # relaciones_pacientes = RelacionPaPro.objects.filter(fk_profesional_salud=profesional_salud)

        tipo_pauta=pauta.fk_tp_terapia.tipo_terapia

        intensidad_form = None
        vocalizacion_form = None

        try:
            if pauta.intensidad:
                intensidad_form = IntensidadForm(request.POST or None, instance=pauta.intensidad, tipo_pauta=tipo_pauta)
        except Intensidad.DoesNotExist:
            intensidad_form = IntensidadForm()

        try:
            if pauta.vocalizacion:
                vocalizacion_form = VocalizacionForm(request.POST or None, instance=pauta.vocalizacion, tipo_pauta=tipo_pauta )
        except Vocalizacion.DoesNotExist:
            vocalizacion_form = VocalizacionForm()

        if request.method == 'POST':
            form = PautaTerapeuticaForm(request.POST, instance=pauta)

            if form.is_valid():
                form.save()

            if intensidad_form and intensidad_form.is_valid():

                if not intensidad_form.cleaned_data['min_db']:
                        #se setea a null
                        intensidad_form.cleaned_data['min_db'] = None

                if not intensidad_form.cleaned_data['max_db']:
                        intensidad_form.cleaned_data['max_db'] = None  

                #antes de guardar el formulario se setea el campo de min db y max db
                intensidad_form.instance.min_db = intensidad_form.cleaned_data['min_db']
                intensidad_form.instance.max_db = intensidad_form.cleaned_data['max_db'] 

                
                intensidad = intensidad_form.save(commit=False)

                intensidad.save()

            if vocalizacion_form and vocalizacion_form.is_valid():

                if not vocalizacion_form.cleaned_data['tempo']:
                        #se setea a null
                        vocalizacion_form.cleaned_data['tempo'] = None

                if not vocalizacion_form.cleaned_data['tempo']:
                        vocalizacion_form.cleaned_data['tempo'] = None  

                #antes de guardar el formulario se setea el campo de min db y max db
                vocalizacion_form.instance.tempo = vocalizacion_form.cleaned_data['tempo']
        

                
                vocalizacion = vocalizacion_form.save(commit=False)

                vocalizacion.save()

            messages.success(request, "Pauta N°" + str(id_pauta_terapeutica_id) + " editada correctamente")
            return redirect('detalle_pauta_admin', id_pauta_terapeutica_id=pauta.id_pauta_terapeutica)
        else:
            form = PautaTerapeuticaForm(instance=pauta)

    return render(request, 'vista_admin/editar_pauta_admin.html',{
        'tipo_usuario': tipo_usuario,
        'pauta': pauta,
        'form': form, 
        'intensidad_form': intensidad_form,
        'vocalizacion_form': vocalizacion_form,
    })

@never_cache
@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Admin'])
def eliminar_pauta_admin(request, id_pauta_terapeutica_id):

    pauta = get_object_or_404(PautaTerapeutica, id_pauta_terapeutica=id_pauta_terapeutica_id)
    tipo_pauta = pauta.fk_tp_terapia

    if tipo_pauta == 'Intensidad':
        pauta.intensidad.delete()
    elif tipo_pauta == 'Vocalización':
        pauta.vocalizacion.delete()

    pauta.delete()

    messages.success(request, "Pauta N°" + str(id_pauta_terapeutica_id) + " eliminada correctamente")

    return redirect('detalle_informe', informe_id=pauta.fk_informe.id_informe)

@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Admin'])
def detalle_esv_admin(request, informe_id):
    tipo_usuario = None 

    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario
        informe = get_object_or_404(Informe, pk=informe_id)
        paciente_relacionado = informe.fk_relacion_pa_pro.id_paciente

        pautas_terapeuticas = PautaTerapeutica.objects.filter(
            fk_informe=informe,
            fk_informe__fk_relacion_pa_pro__id_paciente=paciente_relacionado,
            fk_tp_terapia__tipo_terapia='Escala_vocal'
        )

        if request.method == 'POST':
            pauta_terapeutica_form = PautaTerapeuticaForm(request.POST)

            if pauta_terapeutica_form.is_valid():
                pauta_terapeutica = pauta_terapeutica_form.save(commit=False)
                pauta_terapeutica.fk_informe = informe
                pauta_terapeutica.fk_tp_terapia = TpTerapia.objects.get(tipo_terapia='Escala_vocal')
                pauta_terapeutica.save()

                
                palabras = []
                for i in range(1, 21):  
                    palabra_id = request.POST.get(f'palabra{i}', '') 
                    if palabra_id:
                        palabra = PalabrasPacientes.objects.get(pk=palabra_id) 
                        palabras.append(palabra.palabras_paciente)

                palabras_concatenadas = ", ".join(palabras)

                escala_vocales = EscalaVocales(palabras=palabras_concatenadas)
                escala_vocales.id_pauta_terapeutica = pauta_terapeutica
                escala_vocales.save()

                messages.success(request, "Pauta Escala Vocal ingresada correctamente")
                return HttpResponseRedirect(request.path_info)

        else:
            pauta_terapeutica_form = PautaTerapeuticaForm()

        palabras_pacientes = PalabrasPacientes.objects.all()

        selects = []
        for i in range(1, 21):
            palabras_select = PalabrasPacientes.objects.filter().order_by('id_palabras_pacientes')[i-1]
            selects.append({
                'id': i,
                'palabras_pacientes': palabras_pacientes,
                'palabras_select': palabras_select,
            })

        return render(request, 'vista_admin/detalle_esv_admin.html', {
            'informe': informe,
            'tipo_usuario': tipo_usuario,
            'paciente_relacionado': paciente_relacionado,
            'pauta_terapeutica_form': pauta_terapeutica_form,
            'selects': selects,
            'pautas_terapeuticas': pautas_terapeuticas
        })
    
@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Admin'])
def editar_esv_admin(request, informe_id):
    tipo_usuario = None

    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

        if tipo_usuario == 'Admin':
            informe = get_object_or_404(Informe, pk=informe_id)

            fecha_actual = timezone.now()

            valores_actuales = {
                'titulo': informe.titulo,
                'fecha': fecha_actual, 
                'descripcion': informe.descripcion,
                'observacion': informe.observacion,
            }

            if request.method == 'POST':
                informe.titulo = request.POST.get('titulo')
                informe.fecha = request.POST.get('fecha')
                informe.descripcion = request.POST.get('descripcion')
                informe.observacion = request.POST.get('observacion')
                informe.save()

                messages.success(request, "Informe ESV N°" + str(informe_id) + " editado correctamente")
                return redirect('detalle_esv_admin', informe_id=informe.id_informe)

            return render(request, 'vista_admin/editar_esv_admin.html', {
                'informe': informe,
                'tipo_usuario': tipo_usuario,
                'valores_actuales': valores_actuales,
            })

    return redirect('index')
    
@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Admin'])
def eliminar_esv_admin(request, informe_id):
    if request.user.is_authenticated and request.user.id_tp_usuario.tipo_usuario == 'Admin':
        informe = get_object_or_404(Informe, id_informe=informe_id)

        if informe.tp_informe and informe.tp_informe.tipo_informe == 'ESV':
            informe.esv.delete()

        informe.delete()

        messages.success(request, "Informe ESV N°" + str(informe_id) + " eliminado correctamente")
        return redirect('detalle_paciente', paciente_id=informe.fk_relacion_pa_pro.id_paciente.id_usuario.id_usuario)

    return redirect('index')


@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Admin'])
def analisis_admin(request):
    tipo_usuario = None

    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario

        datos_audiocoeficientes = Audioscoeficientes.objects.select_related(
            'id_audio__fk_pauta_terapeutica__fk_informe__fk_relacion_pa_pro__id_paciente__id_usuario',
            'id_audio__fk_pauta_terapeutica__fk_informe__fk_relacion_pa_pro__fk_profesional_salud'
        ).order_by('-fecha_coeficiente')

        relaciones = RelacionPaPro.objects.all()

        conteo_audios = []
        total_intensidad = 0
        total_vocalizacion = 0

        for relacion in relaciones:
            relacion_info = {
                'relacion': relacion,
                'origenes_audio': {}
            }

            for origen_id, origen_nombre in [(1, 'Intensidad'), (2, 'Vocalización')]:
                audios = Audio.objects.filter(
                    fk_origen_audio=origen_id,
                    fk_pauta_terapeutica__fk_informe__fk_relacion_pa_pro=relacion
                )
                relacion_info['origenes_audio'][origen_nombre] = len(audios)

                if origen_id == 1:
                    total_intensidad += len(audios)
                else:
                    total_vocalizacion += len(audios)

            conteo_audios.append(relacion_info)

        page_number_audios = request.GET.get('page_audios')
        paginator_audios = Paginator(datos_audiocoeficientes, 10)  
        audios_pagina = paginator_audios.get_page(page_number_audios)

        # Paginación para la tabla de conteo_audios
        page_number_conteo = request.GET.get('page_conteo')
        paginator_conteo = Paginator(conteo_audios, 5)  
        conteo_pagina = paginator_conteo.get_page(page_number_conteo)

    return render(request, 'vista_admin/analisis_admin.html', {
        'tipo_usuario': tipo_usuario,
        'datos_audiocoeficientes': audios_pagina,
        'conteo_audios': conteo_pagina,
        'total_intensidad': total_intensidad,
        'total_vocalizacion': total_vocalizacion,
    })

@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Admin'])
def detalle_audio_admin(request, audio_id):
    tipo_usuario = None

    if request.user.is_authenticated:
        tipo_usuario = request.user.id_tp_usuario.tipo_usuario


        audio = Audio.objects.get(id_audio=audio_id)
        audio_coeficiente_automatico = Audioscoeficientes.objects.filter(id_audio=audio_id,fk_tipo_llenado='1').first()
        audio_coeficiente_manual = Audioscoeficientes.objects.filter(id_audio=audio_id,fk_tipo_llenado='2').first()


        # audio = Audio.objects.select_related(
        #     'fk_pauta_terapeutica__fk_informe__fk_relacion_pa_pro__id_paciente',
        #     'fk_pauta_terapeutica__fk_informe__fk_relacion_pa_pro__fk_profesional_salud'
        # ).get(id_audio=audio_id)

        audio_dicc = {
            'id_audio': audio.id_audio,
            'fecha_audio': audio.fecha_audio,
            'id_pauta': audio.fk_pauta_terapeutica_id,
            'id_origen': audio.fk_origen_audio,
            'rut_paciente': audio.fk_pauta_terapeutica.fk_informe.fk_relacion_pa_pro.id_paciente.id_usuario.numero_identificacion,
            'primer_nombre_paciente': audio.fk_pauta_terapeutica.fk_informe.fk_relacion_pa_pro.id_paciente.id_usuario.primer_nombre,
            'ap_paterno_paciente': audio.fk_pauta_terapeutica.fk_informe.fk_relacion_pa_pro.id_paciente.id_usuario.ap_paterno,
            'tipo_profesional': audio.fk_pauta_terapeutica.fk_informe.fk_relacion_pa_pro.fk_profesional_salud.id_usuario.id_tp_usuario,
            'primer_nombre_profesional':audio.fk_pauta_terapeutica.fk_informe.fk_relacion_pa_pro.fk_profesional_salud.id_usuario.primer_nombre,
            'ap_paterno_profesional':audio.fk_pauta_terapeutica.fk_informe.fk_relacion_pa_pro.fk_profesional_salud.id_usuario.ap_paterno,
            #Relacion con
            'nombre_audio': audio_coeficiente_automatico.nombre_archivo if audio_coeficiente_automatico else None
        }
        
        print()


    return render(request, 'vista_admin/detalle_audio_admin.html', {
        'tipo_usuario': tipo_usuario,
        'detalle_audio': audio_dicc,
        'coef_auto': audio_coeficiente_automatico,
        'coef_manual': audio_coeficiente_manual,

    })

@user_passes_test(validate)
@tipo_usuario_required(allowed_types=['Admin'])
def eliminar_audio_admin(request, audio_id):

    audio_registro = get_object_or_404(Audio, id_audio=audio_id)

    ruta = audio_registro.url_audio

    os.remove(os.path.join(settings.MEDIA_ROOT, 'audios_pacientes', ruta))

    audio_registro.delete()

    return redirect('analisis_admin')
# FIN DE VISTAS DE ADMINISTRADOR ------------------------------------------------------------------------------->
