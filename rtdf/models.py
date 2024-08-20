from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.utils import timezone

####Funcionalidades####

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico es obligatorio.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Los superusuarios deben tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Los superusuarios deben tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)
    
###Tablas del modelamiento creado

class Audio(models.Model):
    id_audio = models.AutoField(primary_key=True)
    url_audio = models.CharField(max_length=200)
    fecha_audio = models.DateTimeField()
    fk_origen_audio = models.ForeignKey('OrigenAudio', on_delete=models.PROTECT, db_column='fk_origen_audio')
    fk_pauta_terapeutica = models.ForeignKey('PautaTerapeutica', on_delete=models.CASCADE, db_column='fk_pauta_terapeutica')

    class Meta:
        db_table = 'audio'
        verbose_name_plural = "audio"

    def __str__(self):
        return self.url_audio


class AudioIndepe(models.Model):
    id_audio = models.AutoField(primary_key=True)
    url_audio = models.CharField(max_length=200)
    fecha_audio = models.DateTimeField()
    id_form_audio = models.ForeignKey('FormularioAudio', on_delete=models.CASCADE, db_column='id_form_audio')

    class Meta:
        db_table = 'audio_independiente'
        verbose_name_plural = "audios independientes"

    def __str__(self):
        return self.url_audio        


class AudioscoefIndepe(models.Model):
    id_audiocoeficientes = models.AutoField(primary_key=True)
    nombre_archivo = models.CharField(max_length=100)
    fecha_coeficiente = models.DateTimeField()
    f0 = models.CharField(max_length=100)
    f1 = models.CharField(max_length=100)
    f2 = models.CharField(max_length=100)
    f3 = models.CharField(max_length=100)
    f4 = models.CharField(max_length=100)
    intensidad = models.CharField(max_length=100)
    hnr = models.CharField(max_length=100)
    local_jitter = models.CharField(max_length=100)
    local_absolute_jitter = models.CharField(max_length=100)
    rap_jitter = models.CharField(max_length=100)
    ppq5_jitter = models.CharField(max_length=100)
    ddp_jitter = models.CharField(max_length=100)
    local_shimmer = models.CharField(max_length=100)
    local_db_shimmer = models.CharField(max_length=100)
    apq3_shimmer = models.CharField(max_length=100)
    aqpq5_shimmer = models.CharField(max_length=100)
    apq11_shimmer = models.CharField(max_length=100)
    fk_tipo_llenado = models.ForeignKey('TpLlenado', on_delete=models.PROTECT, null=True, db_column='fk_tipo_llenado')
    id_audio = models.ForeignKey(AudioIndepe, on_delete=models.CASCADE, db_column='id_audio')

    class Meta:
        db_table = 'audioscoeficientes_indepe'
        verbose_name_plural = "audiocoeficiente independientes"

    def __str__(self):
        return self.nombre_archivo    


class AudioscoefIngesta(models.Model):
    id_audiocoeficientes = models.AutoField(primary_key=True)
    paciente = models.CharField(max_length=100)
    genero = models.CharField(max_length=1)
    nombre_archivo = models.CharField(max_length=100)
    fecha_coeficiente = models.DateTimeField()
    fecha_audio = models.DateField()
    dosis_ingesta = models.DecimalField(max_digits=5, decimal_places=2)
    dt_ingesta = models.IntegerField()
    f0 = models.CharField(max_length=100)
    f1 = models.CharField(max_length=100)
    f2 = models.CharField(max_length=100)
    f3 = models.CharField(max_length=100)
    f4 = models.CharField(max_length=100)
    intensidad = models.CharField(max_length=100)
    hnr = models.CharField(max_length=100)
    local_jitter = models.CharField(max_length=100)
    local_absolute_jitter = models.CharField(max_length=100)
    rap_jitter = models.CharField(max_length=100)
    ppq5_jitter = models.CharField(max_length=100)
    ddp_jitter = models.CharField(max_length=100)
    local_shimmer = models.CharField(max_length=100)
    local_db_shimmer = models.CharField(max_length=100)
    apq3_shimmer = models.CharField(max_length=100)
    aqpq5_shimmer = models.CharField(max_length=100)
    apq11_shimmer = models.CharField(max_length=100)
    #fk_tipo_llenado = models.ForeignKey('TpLlenado', on_delete=models.PROTECT, null=True, db_column='fk_tipo_llenado')
    id_audio = models.ForeignKey('PacienteAudioIngesta', on_delete=models.CASCADE, db_column='id_audio')

    class Meta:
        db_table = 'audioscoeficientes_ingesta'
        verbose_name_plural = "audiocoeficiente ingesta"

    def __str__(self):
        return self.nombre_archivo    

class Audioscoeficientes(models.Model):
    id_audiocoeficientes = models.AutoField(primary_key=True)
    nombre_archivo = models.CharField(max_length=100)
    fecha_coeficiente = models.DateTimeField()
    f0 = models.CharField(max_length=100)
    f1 = models.CharField(max_length=100)
    f2 = models.CharField(max_length=100)
    f3 = models.CharField(max_length=100)
    f4 = models.CharField(max_length=100)
    intensidad = models.CharField(max_length=100)
    hnr = models.CharField(max_length=100)
    local_jitter = models.CharField(max_length=100)
    local_absolute_jitter = models.CharField(max_length=100)
    rap_jitter = models.CharField(max_length=100)
    ppq5_jitter = models.CharField(max_length=100)
    ddp_jitter = models.CharField(max_length=100)
    local_shimmer = models.CharField(max_length=100)
    local_db_shimmer = models.CharField(max_length=100)
    apq3_shimmer = models.CharField(max_length=100)
    aqpq5_shimmer = models.CharField(max_length=100)
    apq11_shimmer = models.CharField(max_length=100)
    fk_tipo_llenado = models.ForeignKey('TpLlenado', on_delete=models.PROTECT, db_column='fk_tipo_llenado')
    id_audio = models.ForeignKey(Audio, on_delete=models.CASCADE, db_column='id_audio')

    class Meta:
        db_table = 'audioscoeficientes'
        verbose_name_plural = "audiocoeficiente"

    def __str__(self):
        return self.nombre_archivo    

class Comuna(models.Model):
    id_comuna = models.AutoField(primary_key=True)
    comuna = models.CharField(max_length=50)
    id_provincia = models.ForeignKey('Provincia', on_delete=models.CASCADE, db_column='id_provincia')

    class Meta:
        db_table = 'comuna'
        verbose_name_plural = "comuna"

    def __str__(self):
        return self.comuna
    

class EscalaVocales(models.Model):
    id_pauta_terapeutica = models.OneToOneField('PautaTerapeutica', on_delete=models.CASCADE, db_column='id_pauta_terapeutica', primary_key=True)
    palabras = models.TextField()

    class Meta:
        db_table = 'escala_vocales'
        verbose_name_plural = 'escala vocales'

    def __str__(self):
        return self.palabras


class EstadoSeguimiento(models.Model):
    id_estado_seguimiento = models.AutoField(primary_key=True)
    estado_seguimiento = models.CharField(max_length=45)

    class Meta:
        db_table = 'estado_seguimiento'
        verbose_name_plural = 'estados seguimientos'

    def __str__(self):
        return self.estado_seguimiento


class Esv(models.Model):
    id_protocolo = models.OneToOneField('Protocolo', on_delete=models.CASCADE, db_column='id_protocolo', primary_key=True)
    total_esv = models.IntegerField()
    limitacion = models.IntegerField()
    emocional = models.IntegerField()
    fisico = models.IntegerField()

    class Meta:
        db_table = 'esv'
        verbose_name_plural = "esv"
 

class FamiliarPaciente(models.Model):
    id_familiar_paciente = models.AutoField(primary_key=True)
    ##parentesco = models.CharField(max_length=20)
    id_usuario = models.OneToOneField('Usuario', on_delete=models.CASCADE, db_column='id_usuario')
    fk_tipo_familiar = models.ForeignKey('TpFamiliar', on_delete=models.PROTECT, db_column='fk_tipo_familiar',default=1)

    class Meta:
        db_table = 'familiar_paciente'
        verbose_name_plural = "familiar paciente"

    # NO AGREGAR DEBIDO A QUE CONVIERTE EL ID EN STR Y LAS TABLAS VINCULADAS DA ERROR
    # def __str__(self):
    #     return self.id_familiar_paciente    

    def __str__(self):
        return f'{self.fk_tipo_familiar}: {self.id_usuario.primer_nombre} {self.id_usuario.ap_paterno}'


class FormularioAudio(models.Model):
    id_form_audio = models.AutoField(primary_key=True)
    primer_nombre = models.CharField(max_length=30)
    segundo_nombre = models.CharField(max_length=30, blank=True, null=True)
    ap_paterno = models.CharField(max_length=30)
    ap_materno = models.CharField(max_length=30, blank=True, null=True)
    fecha_nacimiento = models.DateField()
    timestamp = models.DateField()
    id_genero = models.ForeignKey('Genero', on_delete=models.PROTECT, db_column='id_genero')
    id_tp_diagnostico = models.ForeignKey('TpDiagnosticoFono', on_delete=models.PROTECT, db_column='id_tp_diagnostico')
    fk_tipo_hipertension = models.ForeignKey('TipoHipertension', on_delete=models.PROTECT, db_column='fk_tipo_hipertension')
    fk_tipo_diabetes = models.ForeignKey('TipoDiabetes', on_delete=models.PROTECT, db_column='fk_tipo_diabetes')
    fk_tipo_parkinson = models.ForeignKey('TipoParkinson', on_delete=models.PROTECT, db_column='fk_tipo_parkinson')
    fk_tipo_acv = models.ForeignKey('TipoACV', on_delete=models.PROTECT, db_column='fk_tipo_acv')
    fk_profesional_salud = models.ForeignKey('ProfesionalSalud', on_delete=models.CASCADE, db_column='fk_profesional_salud')

    class Meta:
        db_table = 'formulario_audio'
        verbose_name_plural = "Formulario audios"

    def __str__(self):
        return f'Formulario: {self.id_form_audio}'

class Genero(models.Model):
    id_genero = models.AutoField(primary_key=True)
    genero = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'genero'
        verbose_name_plural = 'géneros'

    def __str__(self):
            return self.genero



class Grbas(models.Model):
    id_protocolo = models.OneToOneField('Protocolo', on_delete=models.CASCADE, db_column='id_protocolo', primary_key=True)
    g_grado_disfonia = models.CharField(max_length=30)
    r_aspereza = models.CharField(max_length=30)
    b_soplo = models.CharField(max_length=30)
    a_debilidad = models.CharField(max_length=30)
    s_tension = models.CharField(max_length=30)

    class Meta:
        db_table = 'grbas'
        verbose_name_plural = "grbas"

    # def __str__(self):
    #     return self.id_informe    

class Protocolo(models.Model):
    id_protocolo = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)
    fecha = models.DateTimeField()
    observacion = models.TextField()
    fk_relacion_pa_pro = models.ForeignKey('RelacionPaPro', on_delete=models.PROTECT, db_column='fk_relacion_pa_pro')
    id_audio = models.ForeignKey(Audio, on_delete=models.PROTECT, db_column='id_audio', blank=True, null=True)
    tp_protocolo = models.ForeignKey('TpProtocolo', on_delete=models.PROTECT)

    class Meta:
        db_table = 'protocolo'
        verbose_name_plural = "protocolos"
    
    def __str__(self):
        return f'Protocolo: {self.id_protocolo}' 


class Institucion(models.Model):
    id_institucion = models.AutoField(primary_key=True)
    nombre_institucion = models.CharField(max_length=50)
    id_comuna = models.ForeignKey(Comuna, on_delete=models.CASCADE, db_column='id_comuna')

    class Meta:
        db_table = 'institucion'
        verbose_name_plural = "institucion"        

    def __str__(self):
        return self.nombre_institucion


class Intensidad(models.Model):
    id_pauta_terapeutica = models.OneToOneField('PautaTerapeutica', on_delete=models.CASCADE, db_column='id_pauta_terapeutica', primary_key=True)
    intensidad = models.CharField(max_length=20)
    min_db = models.IntegerField(null=True, blank=True)
    max_db = models.IntegerField(null=True, blank=True)  

    class Meta:
        db_table = 'intensidad'
        verbose_name_plural = "intensidad"



    # def __str__(self):
    #     return self.id_pauta_terapeutica

class Medicamento(models.Model):
    id_medicamento = models.AutoField(primary_key=True)
    principio_activo = models.CharField(max_length=120)
    marca = models.CharField(max_length=45, blank=True, null=True)
    accion_terapeutica = models.CharField(max_length=45, blank=True, null=True)
    laboratorio = models.CharField(max_length=45, blank=True, null=True)
    presentacion = models.CharField(max_length=120)
    total_mg = models.DecimalField(max_digits=5, decimal_places=2)
    indicacion = models.CharField(max_length=120, blank=True, null=True)
    cant_caja = models.CharField(max_length=45, blank=True, null=True)
    ges = models.CharField(max_length=1, blank=True, null=True)
    cmax = models.CharField(max_length=45, blank=True, null=True)
    vida_media = models.CharField(max_length=120, blank=True, null=True)
    interacciones = models.TextField(blank=True, null=True)
    dosificacion = models.TextField(blank=True, null=True)
    OBS = models.TextField(blank=True, null=True)
    valor_ref_oferta = models.IntegerField(null=True, blank=True)  
    valor_ref_normal = models.IntegerField(null=True, blank=True)  

    class Meta:
        db_table = 'medicamento'
        verbose_name_plural = "medicamentos"

    def __str__(self):
        return self.presentacion


class OrigenAudio(models.Model):
    id_origen_audio = models.AutoField(primary_key=True)
    origen_audio = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=100)

    class Meta:
        db_table = 'origen_audio'
        verbose_name_plural = "origen audio"

    def __str__(self):
        return self.origen_audio


class Paciente(models.Model):
    id_paciente = models.AutoField(primary_key=True)
    telegram = models.CharField(max_length=30, blank=True, null=True)
    fk_tipo_hipertension = models.ForeignKey('TipoHipertension', on_delete=models.PROTECT, db_column='fk_tipo_hipertension')
    fk_tipo_diabetes = models.ForeignKey('TipoDiabetes', on_delete=models.PROTECT, db_column='fk_tipo_diabetes')
    id_usuario = models.OneToOneField('Usuario', on_delete=models.PROTECT, db_column='id_usuario')

    class Meta:
        db_table = 'paciente'
        verbose_name_plural = "paciente"

    def __str__(self):
        return f'{self.id_usuario.primer_nombre} {self.id_usuario.ap_paterno}'
    
class PacienteAudioIngesta(models.Model):
    id_audio_ingesta = models.AutoField(primary_key=True)
    url_audio = models.CharField(max_length=200)
    fecha_audio = models.DateTimeField()
    fk_paciente = models.ForeignKey('Paciente', on_delete=models.CASCADE, db_column='fk_paciente')

    class Meta:
        db_table = 'paciente_audio_ingesta'
        verbose_name_plural = "audios paciente ingesta"

    def __str__(self):
        return self.url_audio

    
class PacienteIngesta(models.Model):
    id_paciente_ingesta = models.AutoField(primary_key=True)
    ingesta = models.DecimalField(max_digits=3, decimal_places=2)
    hora_ingesta = models.DateTimeField(blank=True, null=True)
    recordatorio_1 = models.DateTimeField(blank=True, null=True)
    recordatorio_2 = models.DateTimeField(blank=True, null=True)
    recordatorio_3 = models.DateTimeField(blank=True, null=True)
    fk_paciente_segui = models.ForeignKey('PacienteSeguimiento', on_delete=models.CASCADE, db_column='fk_paciente_segui')

    class Meta:
        db_table = 'paciente_ingesta'
        verbose_name_plural = "paciente ingestas"

    def __str__(self):
        return f'{self.id_paciente_ingesta}'
    

class PacienteReceta(models.Model):
    id_paciente_receta = models.AutoField(primary_key=True)
    indicacion_ingesta = models.CharField(max_length=100)
    total_dosis = models.DecimalField(max_digits=5, decimal_places=2)
    timestamp = models.DateTimeField()
    estado = models.CharField(max_length=1, default=0)
    fk_medicamento = models.ForeignKey('Medicamento', on_delete=models.PROTECT, db_column='fk_medicamento')
    fk_relacion_pa_pro = models.ForeignKey('RelacionPaPro', on_delete=models.PROTECT, db_column='fk_relacion_pa_pro')
    

    class Meta:
        db_table = 'paciente_receta'
        verbose_name_plural = "paciente recetas"

    def __str__(self):
        return f'Receta N°{self.id_paciente_receta}' 
    

class PacienteSeguimiento(models.Model):
    id_paciente_segui = models.AutoField(primary_key=True)
    paciente_seguimiento = models.TextField()
    total_ingesta = models.DecimalField(max_digits=5, decimal_places=2)
    timestamp = models.DateTimeField()
    fk_paciente_receta = models.ForeignKey('PacienteReceta', on_delete=models.CASCADE, db_column='fk_paciente_receta')
    fk_estado_seguimiento = models.ForeignKey('EstadoSeguimiento', on_delete=models.PROTECT, db_column='fk_estado_seguimiento')
    

    class Meta:
        db_table = 'paciente_seguimiento'
        verbose_name_plural = "paciente seguimientos"

    def __str__(self):
        return f'Seguimiento N°{self.id_paciente_segui}' 


class Pais(models.Model):
    id_pais = models.AutoField(primary_key=True)
    pais = models.CharField(max_length=60)

    class Meta:
        db_table = 'pais'
        verbose_name_plural = "país"

    def __str__(self):
        return self.pais
    
    
class PalabrasPacientes(models.Model):
    id_palabras_pacientes = models.AutoField(primary_key=True)
    palabras_paciente = models.TextField()

    class Meta:
        db_table = 'palabras_pacientes'
        verbose_name_plural = 'palabras pacientes'

    def __str__(self):
        return self.palabras_paciente


class PautaTerapeutica(models.Model):
    id_pauta_terapeutica = models.AutoField(primary_key=True)
    cant_veces_dia = models.IntegerField()
    descripcion = models.TextField()
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    url_video = models.CharField(max_length=200, blank=True, null=True)
    comentario = models.CharField(max_length=200)
    fk_tp_terapia = models.ForeignKey('TpTerapia',on_delete= models.PROTECT, db_column='fk_tp_terapia')
    # fk_relacion_pa_pro = models.ForeignKey('RelacionPaPro', models.DO_NOTHING, db_column='fk_relacion_pa_pro')
    fk_protocolo = models.ForeignKey('Protocolo', on_delete=models.CASCADE, db_column='fk_protocolo',default=1)

    class Meta:
        db_table = 'pauta_terapeutica'
        verbose_name_plural = "Pauta terapéutica"

    def __str__(self):
        return f'Pauta: {self.id_pauta_terapeutica} | Paciente: {self.fk_protocolo.fk_relacion_pa_pro.id_paciente.id_usuario.primer_nombre} {self.fk_protocolo.fk_relacion_pa_pro.id_paciente.id_usuario.ap_paterno}'




class PreRegistro(models.Model):
    id_pre_registro = models.AutoField(primary_key=True)
    numero_identificacion = models.CharField(unique=True, max_length=100)
    primer_nombre = models.CharField(max_length=30)
    segundo_nombre = models.CharField(max_length=30, blank=True, null=True)
    ap_paterno = models.CharField(max_length=30)
    ap_materno = models.CharField(max_length=30, blank=True, null=True)
    fecha_nacimiento = models.DateField()
    email = models.CharField(unique=True, max_length=100)
    password = models.CharField(max_length=120)
    numero_telefonico = models.CharField(max_length=20, blank=True, null=True)
    validado = models.CharField(max_length=1, default=0)
    id_comuna = models.ForeignKey(Comuna, on_delete=models.PROTECT, db_column='id_comuna')
    id_tp_usuario = models.ForeignKey('TpUsuario', on_delete=models.PROTECT, db_column='id_tp_usuario')
    id_institucion = models.ForeignKey(Institucion, on_delete=models.PROTECT, db_column='id_institucion')

    class Meta:
        db_table = 'pre_registro'
        verbose_name_plural = "pre registro"

    def __str__(self):
        return self.numero_identificacion


class ProfesionalSalud(models.Model):
    id_profesional_salud = models.AutoField(primary_key=True)
    titulo_profesional = models.CharField(max_length=30, blank=True, null=True)
    id_institucion = models.ForeignKey(Institucion, on_delete=models.PROTECT, db_column='id_institucion')
    id_usuario = models.OneToOneField('Usuario', on_delete=models.PROTECT, db_column='id_usuario')

    class Meta:
        db_table = 'profesional_salud'
        verbose_name_plural = "profesional salud"

    def __str__(self):
        return f'{self.id_usuario.id_tp_usuario}: {self.id_usuario.primer_nombre} {self.id_usuario.ap_paterno}'
    
class Provincia(models.Model):
    id_provincia = models.AutoField(primary_key=True)
    provincia = models.CharField(max_length=50)
    id_region = models.ForeignKey('Region', on_delete=models.CASCADE, db_column='id_region')

    class Meta:
        db_table = 'provincia'
        verbose_name_plural = "provincia"

    def __str__(self):
        return self.provincia


class Rasati(models.Model): 
    id_protocolo = models.OneToOneField(Protocolo, on_delete=models.CASCADE, db_column='id_protocolo', primary_key=True)
    r_ronquedad = models.CharField(max_length=10)
    a_aspereza = models.CharField(max_length=10)
    s_soplo = models.CharField(max_length=10)
    a_astenia = models.CharField(max_length=10)
    t_tension = models.CharField(max_length=10)
    i_inestabilidad = models.CharField(max_length=10)

    class Meta:
        db_table = 'rasati'
        verbose_name_plural = "rasati"

    # def __str__(self):
    #     return self.id_informe    


class Region(models.Model): 
    id_region = models.AutoField(primary_key=True)
    region = models.CharField(max_length=50)
    id_pais = models.ForeignKey(Pais, on_delete=models.CASCADE, db_column='id_pais')

    class Meta:
        db_table = 'region'
        verbose_name_plural = "región"

    def __str__(self):
        return self.region

class Registros(models.Model):
    id_registros = models.AutoField(primary_key=True)
    numero_identificacion = models.CharField(max_length=100)
    nombre_completo = models.CharField(max_length=100)
    region_laboral = models.CharField(max_length=100)
    titulo_profesional = models.CharField(max_length=100)

    class Meta:
        db_table = 'registros'
        verbose_name_plural = "registro"

    def __str__(self):
        return self.numero_identificacion

class RelacionFp(models.Model):
    id_relacion_fp = models.AutoField(primary_key=True)
    id_paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, db_column='id_paciente')
    fk_familiar_paciente = models.ForeignKey(FamiliarPaciente, on_delete=models.CASCADE, db_column='fk_familiar_paciente')

    class Meta:
        db_table = 'relacion_fp'
        verbose_name_plural = 'relación familiar paciente'


class RelacionPaPro(models.Model):
    id_relacion_pa_pro = models.AutoField(primary_key=True)
    fk_profesional_salud = models.ForeignKey(ProfesionalSalud, on_delete=models.CASCADE, db_column='fk_profesional_salud')
    id_paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, db_column='id_paciente')

    class Meta:
        db_table = 'relacion_pa_pro'
        verbose_name_plural = 'relación profesional paciente'

    def __str__(self):
        return f'Paciente: {self.id_paciente.id_usuario.primer_nombre} {self.id_paciente.id_usuario.ap_paterno}'
    
class TipoDiabetes(models.Model):
    id_tipo_diabetes = models.AutoField(primary_key=True)
    tipo_diabetes = models.CharField(max_length=50)

    class Meta:
        db_table = 'tipo_diabetes'
        verbose_name_plural = 'tipo diabetes'

    def __str__(self):
        return self.tipo_diabetes
    

class TipoParkinson(models.Model):
    id_parkinson = models.AutoField(primary_key=True)
    tipo_parkinson = models.CharField(max_length=50)

    class Meta:
        db_table = 'tipo_parkinson'
        verbose_name_plural = 'tipo parkinson'

    def __str__(self):
        return self.tipo_parkinson
    
class TipoACV(models.Model):
    id_acv = models.AutoField(primary_key=True)
    tipo_acv = models.CharField(max_length=50)

    class Meta:
        db_table = 'tipo_acv'
        verbose_name_plural = 'tipo accidente cerebrovascular'

    def __str__(self):
        return self.tipo_acv
    

class TpDiagnosticoFono(models.Model):
    id_tp_diagnostico = models.AutoField(primary_key=True)
    tp_diagnostico = models.CharField(max_length=50)

    class Meta:
        db_table = 'tipo_diagnostico_fono'
        verbose_name_plural = 'tipo diagnostico fono'

    def __str__(self):
        return self.tp_diagnostico
    
class TpFamiliar(models.Model):
    id_tipo_familiar = models.AutoField(primary_key=True)
    tipo_familiar = models.CharField(max_length=40)

    class Meta:
        db_table = 'tp_familiar'
        verbose_name_plural = 'tipo familiar'

    def __str__(self):
        return self.tipo_familiar

class TipoHipertension(models.Model):
    id_tipo_hipertension = models.AutoField(primary_key=True)
    tipo_hipertension = models.CharField(max_length=50)

    class Meta:
        db_table = 'tipo_hipertension'
        verbose_name_plural = 'tipo hipertensión'

    def __str__(self):
        return self.tipo_hipertension


class TpProtocolo(models.Model):
    tp_protocolo_id = models.AutoField(primary_key=True)
    tipo_protocolo = models.CharField(max_length=30)

    class Meta:
        db_table = 'tp_protocolo'
        verbose_name_plural = 'tipo protocolos'

    def __str__(self):
        return self.tipo_protocolo
    
class TpLlenado(models.Model):
    id_tipo_llenado = models.AutoField(primary_key=True)
    llenado = models.CharField(max_length=20)

    class Meta:
        db_table = 'tp_llenado'
        verbose_name_plural = 'tipo llenado'

    def __str__(self):
        return self.llenado

class TpTerapia(models.Model):
    id_tp_terapia = models.AutoField(primary_key=True)
    tipo_terapia = models.CharField(max_length=100)

    class Meta:
        db_table = 'tp_terapia'
        verbose_name_plural = 'tipo terapia'

    def __str__(self):
        return self.tipo_terapia
    
class TpUsuario(models.Model):
    id_tp_usuario = models.AutoField(primary_key=True)
    tipo_usuario = models.CharField(max_length=30)
    
    class Meta:
        db_table = 'tp_usuario'
        verbose_name_plural = 'tipo usuario'

    def __str__(self):
        return self.tipo_usuario
    

    def __str__(self):
        return self.tipo_usuario

class UsuarioManager(BaseUserManager):
    def create_user(self, numero_identificacion, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El campo "email" debe estar configurado')

        email = self.normalize_email(email)
        user = self.model(
            numero_identificacion=numero_identificacion,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, numero_identificacion, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(numero_identificacion, email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email=email)

class Usuario(AbstractBaseUser, PermissionsMixin):
    id_usuario = models.AutoField(primary_key=True)
    numero_identificacion = models.CharField(unique=True, max_length=100)
    primer_nombre = models.CharField(max_length=30)
    segundo_nombre = models.CharField(max_length=30, blank=True, null=True)
    ap_paterno = models.CharField(max_length=30)
    ap_materno = models.CharField(max_length=30, blank=True, null=True)
    fecha_nacimiento = models.DateField()
    email = models.CharField(unique=True, max_length=100)
    id_genero = models.ForeignKey(Genero, on_delete=models.PROTECT, null=True, db_column='id_genero')
    #password = models.CharField(max_length=20) #Generado Automaticamente por Django
    numero_telefonico = models.CharField(max_length=20, blank=True, null=True)
    id_tp_usuario = models.ForeignKey(TpUsuario, on_delete=models.PROTECT, db_column='id_tp_usuario',default=1)
    id_comuna = models.ForeignKey(Comuna, on_delete=models.PROTECT, db_column='id_comuna',default=1)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    # related_name único para grupos y permisos. Problema con nombres de la clases internas de Django
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='usuarios'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='usuarios'
    )

    objects = UsuarioManager()


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['numero_identificacion', 'primer_nombre', 'ap_paterno', 'ap_materno', 'fecha_nacimiento']

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'usuario'
        verbose_name_plural = 'usuario'


class Validacion(models.Model):
    id_validacion = models.AutoField(primary_key=True)
    fecha_validacion = models.DateTimeField()
    id_pre_registro = models.OneToOneField(PreRegistro, on_delete=models.CASCADE, db_column='id_pre_registro')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')

    class Meta:
        db_table = 'validacion'
        verbose_name_plural = 'validación'

    # def __str__(self):
    #     return self.id_validacion

class Vocalizacion(models.Model):
    id_pauta_terapeutica = models.OneToOneField(PautaTerapeutica, on_delete=models.CASCADE, db_column='id_pauta_terapeutica', primary_key=True)
    duracion_seg = models.IntegerField()
    bpm = models.IntegerField()
    tempo = models.IntegerField(default=4, blank=True, null=True)

    class Meta:
        db_table = 'vocalizacion'
        verbose_name_plural = 'vocalización'

    # def __str__(self):
    #     return self.id_pauta_terapeutica



