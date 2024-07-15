from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from rtdf.ciencia_datos import *


urlpatterns = [
    path('', views.index, name='index'), 
    path('login/', views.login_view, name="login"),
    path('registro/', views.registro, name='registro'),
    path('pre_registro/', views.pre_registro, name='pre_registro'),
    path('logout/', views.logout_view, name='logout'), 
    path('listado_pacientes/', views.listado_pacientes, name='listado_pacientes'),
    path('vocalizacion/', views.vocalizacion, name='vocalizacion'),
    path('vocalizacion/<int:pauta_id>/', views.vocalizacion, name='vocalizacion_con_pauta'),
    path('intensidad/<int:pauta_id>/', views.intensidad, name='intensidad_con_pauta'),
    path('intensidad/',views.intensidad, name="intensidad"),
    path('list_paci_admin/', views.list_paci_admin, name='list_paci_admin'), 
    path('list_fono_admin/', views.list_fono_admin, name='list_fono_admin'),
    path('list_neur_admin/', views.list_neur_admin, name='list_neur_admin'),
    path('list_fami_admin/', views.list_fami_admin, name='list_fami_admin'),
    path('listado_informes/', views.listado_informes, name='listado_informes'),
    path('detalle_paciente/<int:paciente_id>/', views.detalle_paciente, name='detalle_paciente'),
    path('detalle_fonoaudiologo/<int:fonoaudiologo_id>/', views.detalle_fonoaudiologo, name='detalle_fonoaudiologo'),
    path('detalle_neurologo/<int:neurologo_id>/', views.detalle_neurologo, name='detalle_neurologo'),
    path('detalle_familiar_admin/<int:familiar_id>/', views.detalle_familiar_admin, name='detalle_familiar_admin'),
    path('lista_familiar/', views.lista_familiar, name='lista_familiar'),
    path('detalle_prof_paci/<int:paciente_id>/', views.detalle_prof_paci, name='detalle_prof_paci'),
    path('detalle_familiar/<int:paciente_id>/', views.detalle_familiar, name='detalle_familiar'),
    path('mi_fonoaudiologo/',views.mi_fonoaudiologo,name='mi_fonoaudiologo'),
    path('obtener_provincias/', views.obtener_provincias, name='obtener_provincias'),
    path('obtener_comunas/', views.obtener_comunas, name='obtener_comunas'),
    path('obtener_instituciones/', views.obtener_instituciones, name='obtener_instituciones'),
    path('ingresar_informes/', views.ingresar_informes, name='ingresar_informes'),
    path('editar_informe/<int:informe_id>/', views.editar_informe, name='editar_informe'),
    path('eliminar_informe/<int:informe_id>/', views.eliminar_informe, name='eliminar_informe'),
    path('eliminar_informe_admin/<int:informe_id>/', views.eliminar_informe_admin, name='eliminar_informe_admin'),
    path('detalle_informe/<int:informe_id>/', views.detalle_informe, name='detalle_informe'),
    path('detalle_prof_infor/<int:informe_id>/', views.detalle_prof_infor, name='detalle_prof_infor'),
    path('editar_informe_admin/<int:informe_id>/', views.editar_informe_admin, name='editar_informe_admin'),
    path('pacientes_disponibles/', views.pacientes_disponibles, name='pacientes_disponibles'),
    path('agregar_paciente/<int:paciente_id>/', views.agregar_paciente, name='agregar_paciente'),
    path('desvincular_paciente/<int:paciente_id>/', views.desvincular_paciente, name='desvincular_paciente'),
    path('detalle_prof_pauta/<int:id_pauta_terapeutica_id>/', views.detalle_prof_pauta, name='detalle_prof_pauta'),
    path('editar_prof_pauta/<int:id_pauta_terapeutica_id>/', views.editar_prof_pauta, name='editar_prof_pauta'),
    path('eliminar_prof_pauta/<int:id_pauta_terapeutica_id>/', views.eliminar_prof_pauta, name='eliminar_prof_pauta'),
    
    path('detalle_pauta_admin/<int:id_pauta_terapeutica_id>/', views.detalle_pauta_admin, name='detalle_pauta_admin'),
    path('detalle_pauta_esv_admin/<int:pauta_id>/', views.detalle_pauta_esv_admin, name='detalle_pauta_esv_admin'),

    path('editar_pauta_esv_admin/<int:pauta_id>/', views.editar_pauta_esv_admin, name='editar_pauta_esv_admin'),
    path('eliminar_pauta_esv_admin/<int:pauta_id>/', views.eliminar_pauta_esv_admin, name='eliminar_pauta_esv_admin'),

    path('ciencia_datos/', kmeans_criticidad, name='ciencia_datos'),
    
    path('editar_pauta_admin/<int:id_pauta_terapeutica_id>/', views.editar_pauta_admin, name='editar_pauta_admin'),
    path('eliminar_pauta_admin/<int:id_pauta_terapeutica_id>/', views.eliminar_pauta_admin, name='eliminar_pauta_admin'),
    path('esv/', views.esv, name='esv'),
    path('detalle_esv/<int:informe_id>/', views.detalle_esv, name='detalle_esv'),
    path('editar_esv/<int:informe_id>/', views.editar_esv, name='editar_esv'),
    path('eliminar_informe_esv/<int:informe_id>/', views.eliminar_informe_esv, name='eliminar_informe_esv'),
    path('detalle_esv_admin/<int:informe_id>/', views.detalle_esv_admin, name='detalle_esv_admin'),

    path('eliminar_esv_admin/<int:informe_id>/', views.eliminar_esv_admin, name='eliminar_esv_admin'),
    
    path('analisis_admin/', views.analisis_admin, name='analisis_admin'),
    path('analisis_profe/', views.analisis_profe, name='analisis_profe'),
    path('detalle_audio_admin/<int:audio_id>/', views.detalle_audio_admin, name='detalle_audio_admin'),
    path('detalle_audio_profe/<int:audio_id>/', views.detalle_audio_profe, name='detalle_audio_profe'),
    path('reproducir_audio/<int:audio_id>/', views.reproducir_audio, name='reproducir_audio'),
    path('ingresar_coef_profe/<int:audio_id>/', views.ingresar_coef_profe, name='ingresar_coef_profe'),
    path('eliminar_coef_manual/<int:audiocoeficientes_id>/', views.eliminar_coef_manual, name='eliminar_coef_manual'),
    path('editar_coef_manual/<int:audiocoeficientes_id>/', views.editar_coef_manual, name='editar_coef_manual'),
    path('eliminar_audio_prof/<int:audio_id>/', views.eliminar_audio_prof, name='eliminar_audio_prof'),
    path('eliminar_audio_admin/<int:audio_id>/', views.eliminar_audio_admin, name='eliminar_audio_admin'),
    path('listado_preregistros',views.listado_preregistros, name='listado_preregistros'),
    path('detalle_preregistro/<int:preregistro_id>/', views.detalle_preregistro, name='detalle_preregistro'),
    path('detalle_pauta_esv/<int:pauta_id>/', views.detalle_pauta_esv, name='detalle_pauta_esv'),
    path('escalas_vocales/', views.escalas_vocales, name='escalas_vocales'),
    path('escalas_vocales/<int:pauta_id>/', views.escalas_vocales, name='escalas_vocales_con_pauta'),

    path('editar_pauta_esv/<int:pauta_id>/', views.editar_pauta_esv, name='editar_pauta_esv'),
    path('eliminar_pauta_esv/<int:pauta_id>/', views.eliminar_pauta_esv, name='eliminar_pauta_esv'),

    path('editar_esv_admin/<int:informe_id>/', views.editar_esv_admin, name='editar_esv_admin'),

    #RECUPERAR CONTRASEÑA
    path('recuperar_pw/', views.CustomPasswordResetView.as_view(), name='custom_password_reset'),
    path('recuperar_pw/listo/', views.CustomPasswordResetDoneView.as_view(), name='custom_password_reset_done'),
    path('reiniciar/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='custom_password_reset_confirm'),
    path('reiniciar/listo/', views.CustomPasswordResetCompleteView.as_view(), name='custom_password_reset_complete'),

    path('perfil/<int:usuario_id>/', views.perfil, name='perfil'),
    path('editar_perfil/<int:usuario_id>/', views.editar_perfil, name='editar_perfil'),
    path('analisis_estadistico_profe/<int:informe_id>/', views.analisis_estadistico_profe, name='analisis_estadistico_profe'),
    

]

##urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
