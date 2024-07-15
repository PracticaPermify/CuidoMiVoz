from django.contrib import admin
#from .models import Usuario, Audio, Audioscoeficientes, Comuna, Esv, FamiliarPaciente, Grbas, Informe, Institucion
from .models import *
# Register your models here.

class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['numero_identificacion','primer_nombre','ap_paterno','email', 'id_tp_usuario']
    search_fields = ['numero_identificacion','primer_nombre','ap_paterno','email','id_tp_usuario']
    ##list_filter = ['estado']

class AudioAdmin(admin.ModelAdmin):
    list_display = ['id_audio','url_audio','fecha_audio']
    search_fields = ['id_audio','url_audio','fecha_audio']

class AudioscoeficientesAdmin(admin.ModelAdmin):
    list_display = ['id_audiocoeficientes','nombre_archivo','fecha_coeficiente','f0','f1','f2','f3','f4','intensidad','hnr','local_jitter',
                    'local_absolute_jitter','rap_jitter','ppq5_jitter','ddp_jitter','local_shimmer','local_db_shimmer','apq3_shimmer',
                    'aqpq5_shimmer','apq11_shimmer','fk_tipo_llenado','id_audio']
    search_fields = ['id_audiocoeficientes','nombre_archivo','fecha_coeficiente','f0','f1','f2','f3','f4']

class ComunaAdmin(admin.ModelAdmin):
    list_display = ['id_comuna','comuna','id_provincia']
    search_fields = ['id_comuna','comuna','id_provincia']

class EsvAdmin(admin.ModelAdmin):
    list_display = ['id_informe','total_esv','limitacion','emocional','fisico']
    search_fields = ['id_informe','total_esv','limitacion','emocional','fisico']

class FamiliarPacienteAdmin(admin.ModelAdmin):
    list_display = ['id_familiar_paciente','fk_tipo_familiar']
    search_fields = ['id_familiar_paciente','fk_tipo_familiar']

class GrbasAdmin(admin.ModelAdmin):
    list_display = ['id_informe','g_grado_disfonia','r_aspereza', 'b_soplo', 'a_debilidad', 's_tension']
    search_fields = ['id_informe','g_grado_disfonia','r_aspereza', 'b_soplo', 'a_debilidad', 's_tension']

class InformeAdmin(admin.ModelAdmin):
    list_display = ['id_informe','titulo','descripcion', 'fecha', 'observacion']
    search_fields = ['id_informe','titulo','descripcion', 'fecha', 'observacion']

class InstitucionAdmin(admin.ModelAdmin):
    list_display = ['id_institucion','nombre_institucion','id_comuna']
    search_fields = ['id_institucion','nombre_institucion','id_comuna']

class IntensidadAdmin(admin.ModelAdmin):
    list_display = ['id_pauta_terapeutica','intensidad','min_db','max_db']
    search_fields = ['id_pauta_terapeutica','intensidad','min_db','max_db']

class OrigenAudioAdmin(admin.ModelAdmin):
    list_display = ['id_origen_audio','origen_audio','descripcion']
    search_fields = ['id_origen_audio','origen_audio','descripcion']

class PacienteAdmin(admin.ModelAdmin):
    list_display = ['id_paciente','telegram']
    search_fields = ['id_paciente','telegram']

class PaisAdmin(admin.ModelAdmin):
    list_display = ['id_pais','pais']
    search_fields = ['id_pais','pais']

class PautaTerapeuticaAdmin(admin.ModelAdmin):
    list_display = ['id_pauta_terapeutica','cant_veces_dia','descripcion','fecha_inicio','fecha_fin','url_video','comentario']
    search_fields = ['id_pauta_terapeutica','cant_veces_dia','descripcion','fecha_inicio','fecha_fin','url_video','comentario']

class PreRegistroAdmin(admin.ModelAdmin):
    list_display = ['id_pre_registro','numero_identificacion','primer_nombre','segundo_nombre','ap_paterno','ap_materno','fecha_nacimiento','email','password','numero_telefonico','validado']
    search_fields = ['id_pre_registro','numero_identificacion','primer_nombre','segundo_nombre','ap_paterno','ap_materno','fecha_nacimiento','email','password','numero_telefonico','validado']

class ProfesionalSaludAdmin(admin.ModelAdmin):
    list_display = ['id_profesional_salud','titulo_profesional']
    search_fields = ['id_profesional_salud','titulo_profesional']

class ProvinciaAdmin(admin.ModelAdmin):
    list_display = ['id_provincia','provincia']
    search_fields = ['id_provincia','provincia']

class RasatiAdmin(admin.ModelAdmin):
    list_display = ['id_informe','r_ronquedad','a_aspereza','s_soplo','a_astenia','t_tension','i_inestabilidad']
    search_fields = ['id_informe','r_ronquedad','a_aspereza','s_soplo','a_astenia','t_tension','i_inestabilidad']

class RegionAdmin(admin.ModelAdmin):
    list_display = ['id_region','region','id_pais']
    search_fields = ['id_region','region','id_pais']

class RegistrosAdmin(admin.ModelAdmin):
    list_display = ['id_registros','numero_identificacion','nombre_completo','region_laboral','titulo_profesional']
    search_fields = ['id_registros','numero_identificacion','nombre_completo','region_laboral','titulo_profesional']

class RelacionFpAdmin(admin.ModelAdmin):
    list_display = ['id_relacion_fp','id_paciente','fk_familiar_paciente']
    search_fields = ['id_relacion_fp','id_paciente','fk_familiar_paciente']

class RelacionPaProAdmin(admin.ModelAdmin):
    list_display = ['id_relacion_pa_pro','fk_profesional_salud','id_paciente']
    search_fields = ['id_relacion_pa_pro','fk_profesional_salud','id_paciente']

class TipoDiabetesAdmin(admin.ModelAdmin):
    list_display = ['id_tipo_diabetes','tipo_diabetes']
    search_fields = ['id_tipo_diabetes','tipo_diabetes']

class TpFamiliarAdmin(admin.ModelAdmin):
    list_display = ['id_tipo_familiar','tipo_familiar']
    search_fields = ['id_tipo_familiar','tipo_familiar']

class TipoHipertensionAdmin(admin.ModelAdmin):
    list_display = ['id_tipo_hipertension','tipo_hipertension']
    search_fields = ['id_tipo_hipertension','tipo_hipertension']

class TpInformeAdmin(admin.ModelAdmin):
    list_display = ['tp_informe_id','tipo_informe']
    search_fields = ['tp_informe_id','tipo_informe']

class TpLlenadoAdmin(admin.ModelAdmin):
    list_display = ['id_tipo_llenado','llenado']
    search_fields = ['id_tipo_llenado','llenado']

class TpTerapiaAdmin(admin.ModelAdmin):
    list_display = ['id_tp_terapia','tipo_terapia']
    search_fields = ['id_tp_terapia','tipo_terapia']

class TpUsuarioAdmin(admin.ModelAdmin):
    list_display = ['id_tp_usuario','tipo_usuario']
    search_fields = ['id_tp_usuario','tipo_usuario']

class ValidacionAdmin(admin.ModelAdmin):
    list_display = ['id_validacion','fecha_validacion','id_pre_registro','id_usuario']
    search_fields = ['id_validacion','fecha_validacion','id_pre_registro','id_usuario']

class VocalizacionAdmin(admin.ModelAdmin):
    list_display = ['id_pauta_terapeutica','duracion_seg','bpm']
    search_fields = ['id_pauta_terapeutica','duracion_seg','bpm']

class EscalaVocalAdmin(admin.ModelAdmin):
    list_display = ['id_pauta_terapeutica','palabras']
    search_fields = ['id_pauta_terapeutica','palabras']

class PalabrasPacientesAdmin(admin.ModelAdmin):
    list_display = ['id_palabras_pacientes','palabras_paciente']
    search_fields = ['id_palabras_pacientes','palabras_paciente']


admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Audio, AudioAdmin)
admin.site.register(Audioscoeficientes, AudioscoeficientesAdmin)
admin.site.register(Comuna,ComunaAdmin)
admin.site.register(Esv, EsvAdmin)
admin.site.register(FamiliarPaciente,FamiliarPacienteAdmin)
admin.site.register(Grbas, GrbasAdmin)
admin.site.register(Informe, InformeAdmin)
admin.site.register(Institucion, InstitucionAdmin)
admin.site.register(OrigenAudio, OrigenAudioAdmin)
admin.site.register(Paciente, PacienteAdmin)
admin.site.register(Pais, PaisAdmin)
admin.site.register(PautaTerapeutica, PautaTerapeuticaAdmin)
admin.site.register(PreRegistro, PreRegistroAdmin)
admin.site.register(ProfesionalSalud, ProfesionalSaludAdmin)
admin.site.register(Provincia, ProvinciaAdmin)
admin.site.register(Rasati, RasatiAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Registros, RegistrosAdmin)
admin.site.register(RelacionFp, RelacionFpAdmin)
admin.site.register(RelacionPaPro, RelacionPaProAdmin)
admin.site.register(TipoDiabetes, TipoDiabetesAdmin)
admin.site.register(TipoHipertension, TipoHipertensionAdmin)
admin.site.register(TpInforme, TpInformeAdmin)
admin.site.register(TpLlenado, TpLlenadoAdmin)
admin.site.register(TpTerapia, TpTerapiaAdmin)
admin.site.register(Validacion, ValidacionAdmin)
admin.site.register(Vocalizacion, VocalizacionAdmin)
admin.site.register(TpUsuario, TpUsuarioAdmin)
admin.site.register(TpFamiliar, TpFamiliarAdmin)
admin.site.register(Intensidad, IntensidadAdmin)
admin.site.register(EscalaVocales, EscalaVocalAdmin)
admin.site.register(PalabrasPacientes, PalabrasPacientesAdmin)