from django import forms
from .models import *
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
import re
from django.core import validators
from datetime import date
from django.utils.translation import gettext as _
from django.core.exceptions import ObjectDoesNotExist
##Numero de telefono

def es_numero_telefonico_valido(numero_telefonico):
    patron = r'^\+56\d+$'
    
    if not re.match(patron, numero_telefonico):
        raise ValidationError(_('Ingresa un número de teléfono válido en formato +56XXXXXXXXX.'))

    if len(numero_telefonico) < 12:
        raise ValidationError(_('Número de teléfono inválido.Ingreselo nuevamente'))

def contrasena_valida(password):
    errores = []

    if not re.search(r'[A-Z]', password):
        errores.append('La contraseña debe contener al menos una letra mayúscula.')

    if not re.search(r'[a-z]', password):
        errores.append('La contraseña debe contener al menos una letra minúscula.')

    if not re.search(r'[0-9]', password):
        errores.append('La contraseña debe contener al menos un número.')

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errores.append('La contraseña debe contener al menos un carácter especial.')

    if len(password) < 8:
        errores.append('La contraseña debe tener al menos 8 caracteres.')
    
    if ' ' in password:
        errores.append('La contraseña no puede contener espacios.')

    if errores:
        raise forms.ValidationError(errores)
    
def clean_email(self):
        email = self.cleaned_data.get('email')

        if '@' not in email or not (email.endswith('.com') or email.endswith('.cl')):
            raise ValidationError('El correo electrónico ingresado no es válido.')

        return email

def clean_tipo_usuario(self):
        tipo_usuario = self.cleaned_data.get('tipo_usuario')
        if not tipo_usuario:
            raise forms.ValidationError('Debe seleccionar un tipo de usuario para registrarse.')
        return tipo_usuario

def clean_id_comuna(self):
        id_comuna = self.cleaned_data.get('id_comuna')

        if not id_comuna:
            raise ValidationError('Debe seleccionar una comuna para registrarse.')

        return id_comuna

def clean_numero_identificacion(numero_identificacion):
    cleaned_rut = re.sub('[^\dKk]', '', numero_identificacion)

    if '.' in numero_identificacion:
        raise ValidationError(_('El Rut no debe contener puntos.'))

    if len(cleaned_rut) < 8 or len(cleaned_rut) > 9:
        raise ValidationError(_('El Rut no es válido, inténtelo de nuevo.'))

    if '-' not in numero_identificacion:
        raise ValidationError(_('El Rut no es válido, debe contener un guión.'))

    if not re.match(r'^\d{7,8}-[Kk\d]$', numero_identificacion):
        raise ValidationError(_('El Rut ingresado no es válido.'))

    return numero_identificacion


def validate_fecha_nacimiento(value):
    hoy = date.today()
    if value == hoy:
        raise ValidationError('La fecha de nacimiento no puede ser la fecha actual, ingrese su fecha de nacimiento correcto.')
    if value.year < 1900:
            raise ValidationError('La fecha de nacimiento no es valida, ingréselo nuevamente.')
    if value > hoy:
        raise ValidationError('La fecha de nacimiento no puede ser posterior a la fecha actual, inténtelo de nuevo.')
    
##VALIDADOR PRE REGISTRO

def clean_numero_identificacion_usuario(value):
    if Usuario.objects.filter(numero_identificacion=value).exists():
        raise forms.ValidationError("El número de identificación ya ha sido registrado.")

def clean_correo_usuario(value):
    if Usuario.objects.filter(email=value).exists():
        raise forms.ValidationError("El correo electrónico ya ha sido registrado.")


class RegistroForm(forms.ModelForm):

    numero_identificacion = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': '12345678-9'}),
        label='Rut',
        validators=[clean_numero_identificacion, clean_numero_identificacion_usuario]
    )

    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(format='%d-%m-%Y', attrs={'type': 'date' , 'class': 'campo_fecha'}),
        required=True,
        validators=[validate_fecha_nacimiento]
        
    )

    email = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': 'usuario@gmail.com'}),
        required=True,
        validators=[clean_correo_usuario]
    )

    numero_telefonico = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '+56912345678'}),
        validators=[es_numero_telefonico_valido]
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': '********'}),
        validators=[contrasena_valida],
        required=True,
        help_text='La contraseña debe contener al menos una mayúscula, una minúscula, un número y un carácter especial.',
    )

    tipo_usuario = forms.ModelChoiceField(
        queryset=TpUsuario.objects.filter(tipo_usuario__in=['Paciente', 'Familiar']),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control form-control-sm', 'id': 'tipo_usuario'}),
        label='Tipo de usuario',
        empty_label= "Seleccione el tipo de usuario",
        error_messages={
            'required': 'Debe seleccionar un tipo de usuario para registrarse.'
        }
    )

    id_comuna = forms.ModelChoiceField(
        queryset=Comuna.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
        label='Comuna'
    )

    telegram = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Telegram'}),
        help_text='Ingrese su usuario de Telegram (opcional)'
    )

    fk_tipo_hipertension = forms.ModelChoiceField(
        queryset=TipoHipertension.objects.all(),
        required=False,
        empty_label= "Seleccione su tipo de hipertensión",
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
        label='Tipo de Hipertensión'
    )

    fk_tipo_diabetes = forms.ModelChoiceField(
        queryset=TipoDiabetes.objects.all(),
        required=False,
        empty_label= "Seleccione su tipo de diabetes",
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
        label='Tipo de Diabetes'
    )

    fk_tipo_familiar = forms.ModelChoiceField(
        queryset=TpFamiliar.objects.all(),  
        required=False,  
        empty_label= "Seleccione su tipo de familiar",
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
        label='Parentesco con paciente'
    )

    rut_paciente = forms.CharField(
        max_length=12,  
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '12345678-9'}),
        help_text='Ingresa el RUT del paciente (Ejemplo: 12345678-9)',
        label='Rut del paciente',
        validators=[clean_numero_identificacion]
    )

    def clean_rut_paciente(self):
        rut_paciente = self.cleaned_data.get('rut_paciente')

        if rut_paciente:
            try:
                paciente_relacionado = Paciente.objects.get(id_usuario__numero_identificacion=rut_paciente)
            except Paciente.DoesNotExist:
                raise forms.ValidationError('El paciente con el rut ingresado no existe, ingresalo nuevamente.')

        return rut_paciente



    class Meta:
        model = Usuario
        fields = ['numero_identificacion', 
                  'primer_nombre', 
                  'segundo_nombre', 
                  'ap_paterno', 
                  'ap_materno', 
                  'fecha_nacimiento', 
                  'email', 
                  'numero_telefonico', 
                  'id_comuna',
                  'password',
                  'tipo_usuario',
                  'telegram',  # Campo para Paciente
                  'fk_tipo_hipertension',  # Campo para Paciente
                  'fk_tipo_diabetes',  # Campo para Paciente
                  'fk_tipo_familiar', #Campo para familiar
                  'rut_paciente'
                  ]


class InformeForm(forms.ModelForm):
    fk_relacion_pa_pro = forms.ModelChoiceField(
        queryset=RelacionPaPro.objects.all(),
        required=True,
        empty_label="Seleccione su paciente",
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
        label='Relación con Paciente y Profesional de Salud'
    )

    titulo = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Vocalización/Intensidad'}),
        label='Título'
    )

    descripcion = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'placeholder': 'Descripción' , 'class': 'campo_descripcion'}),
        label='Descripción'
    )

    fecha = forms.DateTimeField(
        widget=forms.DateTimeInput(format='%d-%m-%Y', attrs={'placeholder': 'día-mes-año', 'class': 'campo_fecha'}),
        required=True
    )

    observacion = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'placeholder': 'Añadir detalles de los síntomas.', 'class': 'campo_observacion'}),
        label='Observación'
    )

    tp_informe = forms.ModelChoiceField(
        queryset=TpInforme.objects.filter(tipo_informe__in=['RASATI', 'GRBAS']),
        required=False,
        empty_label="Tipo de informe",
        widget=forms.Select(attrs={'class': 'form-control form-control-sm','id': 'tp_informe'}),
        label='Tipo de Informe'
    )

    def __init__(self, *args, **kwargs):

        vista_contexto = kwargs.pop('vista_contexto', None)
        super(InformeForm, self).__init__(*args, **kwargs)

        if vista_contexto == "editar_informe":
            self.fields['fk_relacion_pa_pro'].required = False

    class Meta:
        model = Informe  
        fields = [
            'fk_relacion_pa_pro', 
            'titulo', 
            'descripcion', 
            'fecha', 
            'observacion', 
            'tp_informe'
        ]

        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


OPCIONES_GRBAS = [
        (0, 'Normal'),
        (1, 'Alteración leve'),
        (2, 'Alteración moderada'),
        (3, 'Alteración Severa'),
    ]

class GrbasForm(InformeForm):
    g_grado_disfonia = forms.ChoiceField(
        label='Grado de Disfonía',
        choices=OPCIONES_GRBAS,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    r_aspereza = forms.ChoiceField(
        label='r_aspereza',
        choices=OPCIONES_GRBAS,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    b_soplo = forms.ChoiceField(
        label='b_soplo',
        choices=OPCIONES_GRBAS,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    a_debilidad = forms.ChoiceField(
        label='a_debilidad',
        choices=OPCIONES_GRBAS,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    s_tension = forms.ChoiceField(
        label='s_tension',
        choices=OPCIONES_GRBAS,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Grbas
        fields = InformeForm.Meta.fields + ['g_grado_disfonia', 'r_aspereza', 'b_soplo', 'a_debilidad', 's_tension']

OPCIONES_RASATI = [
        (0, 'Normal'),
        (1, 'Alteración leve'),
        (2, 'Alteración moderada'),
        (3, 'Alteración severa'),
    ]

class RasatiForm(InformeForm):
    r_ronquedad = forms.ChoiceField(
        label='r_ronquedad',
        choices=OPCIONES_RASATI,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    a_aspereza = forms.ChoiceField(
        label='a_aspereza',
        choices=OPCIONES_RASATI,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    s_soplo = forms.ChoiceField(
        label='s_soplo',
        choices=OPCIONES_RASATI,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    a_astenia = forms.ChoiceField(
        label='a_astenia',
        choices=OPCIONES_RASATI,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    t_tension = forms.ChoiceField(
        label='t_tension',
        choices=OPCIONES_RASATI,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    
    i_inestabilidad = forms.ChoiceField(
        label='i_inestabilidad',
        choices=OPCIONES_RASATI,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Rasati
        fields = InformeForm.Meta.fields + ['r_ronquedad', 'a_aspereza', 's_soplo', 'a_astenia', 't_tension', 'i_inestabilidad']            


class PautaTerapeuticaForm(forms.ModelForm):

    cant_veces_dia = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Número de veces al día'}),
        label='Título'
    )

    descripcion = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'placeholder': 'Descripción'}),
        label='Descripción'
    )

    fecha_inicio = forms.DateTimeField(
         widget=forms.DateTimeInput(format='%d-%m-%Y', attrs={'placeholder': 'día-mes-año'}),
         required=True
     )

    fecha_fin = forms.DateTimeField(
         widget=forms.DateTimeInput(format='%d-%m-%Y', attrs={'placeholder': 'día-mes-año'}),
         required=True
     )

    comentario = forms.CharField(
         required=True,
         widget=forms.Textarea(attrs={'placeholder': 'Añadir comentarios'}),
         label='Observación'
    )

    fk_tp_terapia = forms.ModelChoiceField(
        queryset=TpTerapia.objects.filter(tipo_terapia__in=['Vocalización', 'Intensidad']),
        required=False,
        empty_label= "Seleccione el tipo de terapia",
        widget=forms.Select(attrs={'class': 'form-control form-control-sm','id': 'fk_tp_terapia'}),
        label='Tipo de terapia'
    )




    class Meta:
        model = PautaTerapeutica
        fields = ['cant_veces_dia', 'descripcion', 'fecha_inicio', 'fecha_fin', 'comentario', 'fk_tp_terapia']
        widgets = {
            'fecha_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fecha_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class VocalizacionForm(PautaTerapeuticaForm):

    duracion_seg = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Duración en segundos'}),
        required=False,
        label='Duración en segundos'
    )

    bpm = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Ingresar BPM necesario'}),
        required=False,
        label='BPM'
    )

    tempo = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Ingresar Tempo en segundos'}),
        required=False,
        label='Tempo'
    )

    def clean_bpm(self):
        bpm = self.cleaned_data.get('bpm')

        if not bpm.isdigit():
            raise forms.ValidationError('El BPM ingresado no es valido.')

        bpm = int(bpm)

        if not 20 <= bpm <= 280:
            raise forms.ValidationError('BPM debe estar en el rango de 20 a 280.')

        return bpm

    def clean_tempo(self):
        tempo = self.cleaned_data.get('tempo')

        if not tempo.isdigit():
            raise forms.ValidationError('El tempo del ejercicio no es valido.')

        tempo = int(tempo)

        if not 2 <= tempo <= 12:
            raise forms.ValidationError('Tempo debe estar en el rango de 2 a 12.')

        return tempo
    
    def clean_duracion_seg(self):
        duracion_seg = self.cleaned_data['duracion_seg']
        
        if not duracion_seg.isnumeric():
            raise ValidationError('La duración del ejercicio no es valido.')
        return duracion_seg



    def __init__(self, *args, **kwargs):

        tipo_terapia = kwargs.pop('tipo_terapia', None)
        tipo_pauta = kwargs.pop('tipo_pauta', None)
        super(VocalizacionForm, self).__init__(*args, **kwargs)

        if tipo_terapia == "Vocalización":
            self.fields['duracion_seg'].required = True
            self.fields['bpm'].required = True
            self.fields['tempo'].required = True


        if tipo_pauta == "Vocalización":
            self.fields['duracion_seg'].required = True
            self.fields['bpm'].required = True
            self.fields['tempo'].required = True


    class Meta:
        model = Vocalizacion
        fields = PautaTerapeuticaForm.Meta.fields + ['duracion_seg', 'bpm', 'tempo']


class IntensidadForm(PautaTerapeuticaForm):

    intensidad = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Intensidad'}),
        required=False,
        label='Duración en segundos'
    )

    min_db = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'dB mínimo'}),
        required=False,
        label='BPM'
    )

    max_db = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'dB máximo'}),
        required=False,
        label='BPM'
    )

    class Meta:
        model = Intensidad
        fields = PautaTerapeuticaForm.Meta.fields + ['intensidad', 'min_db','max_db']

    def __init__(self, *args, **kwargs):

        tipo_pauta = kwargs.pop('tipo_pauta', None)
        super(IntensidadForm, self).__init__(*args, **kwargs)

        if tipo_pauta == "Intensidad":
            self.fields['intensidad'].required = True
            # self.fields['min_db'].required = True
            # self.fields['max_db'].required = True



def Validador_coeficiente(value):
    try:
        float(value)
    except (ValueError, TypeError):
        raise ValidationError('El coeficiente ingresado no es valido, intentelo de nuevo.')


class AudioscoeficientesForm(forms.ModelForm):

    nombre_archivo = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Nombre del audio'}),
        required=False,
        label='Nombre audio'
    )    

    fk_tipo_llenado = forms.ModelChoiceField(queryset=TpLlenado.objects.all(),
        required=False,  # Cambia esto a True si el campo es obligatorio para Familiares
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
    )
    

    id_audio = forms.ModelChoiceField(queryset=Audio.objects.all(),
        required=False,  # Cambia esto a True si el campo es obligatorio para Familiares
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
    )
    

    fecha_coeficiente = forms.DateTimeField(
        widget=forms.DateTimeInput(format='%d-%m-%Y', attrs={'placeholder': 'día-mes-año'}),
        required=False
    )

    f0 = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Coeficiente f0'}),
        required=True,
        label='Coeficiente f0',
        validators=[Validador_coeficiente]
    ) 

    f1 = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Coeficiente f1'}),
        required=True,
        label='Coeficiente f1',
        validators=[Validador_coeficiente]
    )    

    f2 = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Coeficiente f2'}),
        required=True,
        label='Coeficiente f2',
        validators=[Validador_coeficiente]
    )    

    f3 = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Coeficiente f3'}),
        required=True,
        label='Coeficiente f3',
        validators=[Validador_coeficiente]
    )    

    f4 = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Coeficiente f4'}),
        required=True,
        label='Coeficiente f4',
        validators=[Validador_coeficiente]
    )       

    intensidad = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Intensidad'}),
        required=True,
        label='Intensidad',
        validators=[Validador_coeficiente]
    )

    hnr = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'HNR'}),
        required=True,
        label='HNR',
        validators=[Validador_coeficiente]
    )

    local_jitter = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Local Jitter'}),
        required=True,
        label='Local Jitter',
        validators=[Validador_coeficiente]
    )

    local_absolute_jitter = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Local Absolute Jitter'}),
        required=True,
        label='Local Absolute Jitter',
        validators=[Validador_coeficiente]
    )

    rap_jitter = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'RAP Jitter'}),
        required=True,
        label='RAP Jitter',
        validators=[Validador_coeficiente]
    )

    ppq5_jitter = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'PPQ5 Jitter'}),
        required=True,
        label='PPQ5 Jitter',
        validators=[Validador_coeficiente]
    )

    ddp_jitter = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'DDP Jitter'}),
        required=True,
        label='DDP Jitter',
        validators=[Validador_coeficiente]
    )

    local_shimmer = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Local Shimmer'}),
        required=True,
        label='Local Shimmer',
        validators=[Validador_coeficiente]
    )

    local_db_shimmer = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Local dB Shimmer'}),
        required=True,
        label='Local dB Shimmer',
        validators=[Validador_coeficiente]
    )

    apq3_shimmer = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'APQ3 Shimmer'}),
        required=True,
        label='APQ3 Shimmer',
        validators=[Validador_coeficiente]
    )

    aqpq5_shimmer = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'APQ5 Shimmer'}),
        required=True,
        label='APQ5 Shimmer',
        validators=[Validador_coeficiente]
    )

    apq11_shimmer = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'APQ11 Shimmer'}),
        required=True,
        label='APQ11 Shimmer',
        validators=[Validador_coeficiente]
    )    

    class Meta:
        model = Audioscoeficientes  
        fields = ['nombre_archivo','fk_tipo_llenado','id_audio','fecha_coeficiente'
                  ,'f0','f1','f2','f3','f4','intensidad','hnr','local_jitter',
                  'local_absolute_jitter','rap_jitter','ppq5_jitter','ddp_jitter',
                  'local_shimmer','local_db_shimmer','apq3_shimmer','aqpq5_shimmer'
                  ,'apq11_shimmer']
        

        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


#Inicio de la pesadilla

class PreRegistroForm(forms.ModelForm):

    numero_identificacion = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': '12345678-9'}),
        validators=[clean_numero_identificacion, clean_numero_identificacion_usuario],
        label='Rut'
    )

    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(format='%d-%m-%Y', attrs={'type': 'date'}),
        required=False,
        validators=[validate_fecha_nacimiento]
    )

    email = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': 'usuario@gmail.com'}),
        required=True,
        validators=[clean_correo_usuario]
    )

    numero_telefonico = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '+56912345678'}),
        help_text='Ingrese un número de teléfono válido (Ejemplo: +56912345678)'
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': '********'}),
        required=False,
        help_text='La contraseña debe contener al menos una mayúscula, una minúscula, un número y un carácter especial.'
    )

    tipo_usuario = forms.ModelChoiceField(
        queryset=TpUsuario.objects.filter(tipo_usuario__in=['Fonoaudiologo', 'Neurologo', 'Enfermera']),
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-control form-control-sm', 'id': 'tipo_usuario'}),
        label='Tipo de usuario'
    )

    id_comuna = forms.ModelChoiceField(
        queryset=Comuna.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
        label='Comuna'
    )

    id_institucion = forms.ModelChoiceField(
        queryset=Institucion.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
        label='Institución'
    )

    class Meta:
        model = PreRegistro
        fields = ['numero_identificacion', 
                  'primer_nombre', 
                  'segundo_nombre', 
                  'ap_paterno', 
                  'ap_materno', 
                  'fecha_nacimiento', 
                  'email', 
                  'numero_telefonico', 
                  'id_comuna',
                  'password',
                  'tipo_usuario',
                  'id_institucion',
                  ]
        
    # def clean(self):
    #     cleaned_data = super().clean()

    #     fecha_nacimiento = cleaned_data.get('fecha_nacimiento')
    #     if not fecha_nacimiento:
    #         raise forms.ValidationError("La fecha de nacimiento es requerida.")

    #     return cleaned_data


class EditarPerfilForm(forms.Form):
    primer_nombre = forms.CharField(max_length=30, required=True)
    ap_paterno = forms.CharField(max_length=30, required=True)
    segundo_nombre = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'placeholder': 'Opcional'}))
    ap_materno = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'placeholder': 'Opcional'}))
    fecha_nacimiento = forms.DateField(widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}), validators=[validate_fecha_nacimiento], required=True)
    numero_telefonico = forms.CharField(max_length=20, validators=[es_numero_telefonico_valido], required=True)
    id_comuna = forms.ModelChoiceField(queryset=Comuna.objects.all(), required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Dejar en blanco si no se desea modificar'}),max_length=128, validators=[contrasena_valida], required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': '********'}),max_length=128, validators=[contrasena_valida], required=False)
    original_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': '********'}),max_length=128, required=False)

    #campos de paciente
    telegram= forms.CharField(max_length=30, required=False)
    fk_tipo_hipertension = forms.ModelChoiceField(queryset=TipoHipertension.objects.all() , required=False)
    fk_tipo_diabetes = forms.ModelChoiceField(queryset=TipoDiabetes.objects.all() , required=False)

    #campo de profesional
    titulo_profesional = forms.CharField(max_length=30, required=False)
    id_institucion = forms.ModelChoiceField(queryset=Institucion.objects.all() , required=False)



    # id_tp_usuario = forms.ModelChoiceField(queryset=TpUsuario.objects.all(), required=True)

    def __init__(self, *args, **kwargs):

        tipo_usuario = kwargs.pop('tipo_usuario', None)
        super(EditarPerfilForm, self).__init__(*args, **kwargs)

        if tipo_usuario == "Paciente":
            self.fields['telegram'].required = True
            self.fields['fk_tipo_hipertension'].required = True
            self.fields['fk_tipo_diabetes'].required = True

        elif tipo_usuario == "Familiar":

            pass

        elif tipo_usuario == "Fonoaudiologo":
            # self.fields['segundo_nombre'].required = True
            self.fields['titulo_profesional'].required = True
            self.fields['id_institucion'].required = True

        elif tipo_usuario == "Neurologo":
            # self.fields['segundo_nombre'].required = True
            self.fields['titulo_profesional'].required = True
            self.fields['id_institucion'].required = True

        elif tipo_usuario == "Enfermera":
            # self.fields['segundo_nombre'].required = True
            self.fields['titulo_profesional'].required = True
            self.fields['id_institucion'].required = True

 
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        original_password = cleaned_data.get('original_password')


        if password:
            if not (confirm_password and original_password):
                self.add_error(None, "Debe completar los campos de confirmar contraseña y contraseña original.")

        return cleaned_data
    

    # class Meta:
    #     model = Usuario

    #     fields = ['numero_identificacion', 
    #               'primer_nombre', 
    #               #'segundo_nombre', 
    #               'ap_paterno', 
    #               #'ap_materno', 
    #               'fecha_nacimiento', 
    #               'email', 
    #               'numero_telefonico', 
    #               #'id_comuna',
    #               'password',
    #               #'tipo_usuario',
    #               #'telegram',  # Campo para Paciente
    #               #'fk_tipo_hipertension',  # Campo para Paciente
    #               #'fk_tipo_diabetes',  # Campo para Paciente
    #               #'fk_tipo_familiar', #Campo para familiar
    #               #'rut_paciente'
    #               ]
        
    #     widgets = {
    #         'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    #     }