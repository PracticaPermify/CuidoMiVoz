from telegram import Update, Bot, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext, Updater, ConversationHandler
from django.conf import settings
from .models import *
import os
from datetime import datetime, timedelta
from django.conf import settings
from pydub import AudioSegment
from django.utils.text import slugify
import pytz

TELEGRAM_TOKEN = '7276964571:AAHaIIsfETRrpqmEFfRnoq_6n0OTH3U6uW4'
bot = Bot(token=TELEGRAM_TOKEN)

context_data = {}

SELECCIONAR_RECETA, SELECCIONAR_INGESTA, SUBIR_AUDIO = range(3)



def start(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    telegram_nombre = update.message.from_user.username
    paciente = Paciente.objects.filter(telegram=telegram_nombre).first()

    if paciente:
        recetas = PacienteReceta.objects.filter(fk_relacion_pa_pro__id_paciente=paciente.id_paciente)
        if recetas.exists():
            opciones = [
                [f"{i + 1}. {receta.fk_medicamento.presentacion} Dosis: {receta.total_dosis}mg"] 
                for i, receta in enumerate(recetas)
            ]
            
            context.user_data['recetas'] = {
                f"{i + 1}. {receta.fk_medicamento.presentacion} Dosis: {receta.total_dosis}mg": receta.id_paciente_receta 
                for i, receta in enumerate(recetas)
            }
            
            reply_markup = ReplyKeyboardMarkup(opciones, one_time_keyboard=True)
            #update.message.reply_text('Selecciona una receta:', reply_markup=reply_markup)

            update.message.reply_text(
                f'Selecciona una receta, {paciente.id_usuario.primer_nombre} {paciente.id_usuario.ap_paterno}. '
                f'Hemos encontrado {recetas.count()} recetas para ti:', 
                reply_markup=reply_markup
            )
            return SELECCIONAR_RECETA
        else:
            update.message.reply_text('No se encontraron recetas para este paciente.')
            return ConversationHandler.END
    else:
        update.message.reply_text('No estás registrado como paciente.')
        return ConversationHandler.END

def seleccionar_receta(update: Update, context: CallbackContext):
    receta_seleccionada = update.message.text
    receta_id = context.user_data['recetas'].get(receta_seleccionada)

    if receta_id:
        receta = PacienteReceta.objects.filter(id_paciente_receta=receta_id).first()
        if receta:
            context.user_data['receta_id'] = receta.id_paciente_receta
            seguimiento = PacienteSeguimiento.objects.filter(fk_paciente_receta=receta.id_paciente_receta).last()
            if seguimiento:
                ingestas = PacienteIngesta.objects.filter(fk_paciente_segui=seguimiento.id_paciente_segui)
                #opciones = [[str(ingesta.ingesta)] for ingesta in ingestas]

                opciones = [
                    [f"{i + 1}. Hora: {ingesta.hora_ingesta} - {str(ingesta.ingesta)}% de un comprimido"] 
                    for i, ingesta in enumerate(ingestas)
                ]

                context.user_data['ingestas'] = {
                    f"{i + 1}. Hora: {ingesta.hora_ingesta} - {str(ingesta.ingesta)}% de un comprimido": ingesta.id_paciente_ingesta 
                    for i, ingesta in enumerate(ingestas)
                }

                reply_markup = ReplyKeyboardMarkup(opciones, one_time_keyboard=True)
                update.message.reply_text('Selecciona una ingesta:', reply_markup=reply_markup)
                return SELECCIONAR_INGESTA
            else:
                update.message.reply_text('No se encontraron seguimientos para esta receta.')
                return ConversationHandler.END
        else:
            update.message.reply_text('Receta no válida.')
            return ConversationHandler.END
    else:
        update.message.reply_text('Receta no válida.')
        return ConversationHandler.END

def seleccionar_ingesta(update: Update, context: CallbackContext):
    ingesta_seleccionada = update.message.text

    ingesta_id = context.user_data['ingestas'].get(ingesta_seleccionada)

    ingesta = PacienteIngesta.objects.filter(id_paciente_ingesta=ingesta_id).first()

    if ingesta:
        context.user_data['ingesta_id'] = ingesta.id_paciente_ingesta
        update.message.reply_text('Por favor, sube tu audio.')
        return SUBIR_AUDIO
    else:
        update.message.reply_text('Ingesta no válida.')
        return ConversationHandler.END

def guardar_audio(update: Update, context: CallbackContext):
    file = update.message.voice.get_file()
    ingesta_id = context.user_data.get('ingesta_id')
    paciente_ingesta = PacienteIngesta.objects.get(id_paciente_ingesta=ingesta_id)
    
    ingesta = PacienteIngesta.objects.get(id_paciente_ingesta=ingesta_id)
    id_paci = ingesta.fk_paciente_segui.fk_paciente_receta.fk_relacion_pa_pro.id_paciente_id
    nom_paci = ingesta.fk_paciente_segui.fk_paciente_receta.fk_relacion_pa_pro.id_paciente.id_usuario.primer_nombre
    ap_paci = ingesta.fk_paciente_segui.fk_paciente_receta.fk_relacion_pa_pro.id_paciente.id_usuario.ap_paterno

    # creacion de carpetas y sus rutas
    audios_form_path = os.path.join(settings.MEDIA_ROOT, 'audios_ingestas')
    if not os.path.exists(audios_form_path):
        os.makedirs(audios_form_path)

    paci_nombre = slugify(f"{nom_paci}_{ap_paci}")
    paciente_path = os.path.join(audios_form_path, paci_nombre)
    if not os.path.exists(paciente_path):
        os.makedirs(paciente_path)

    # convertir zona horaria
    hora_utc = update.message.date
    timezone_local = pytz.timezone('America/Santiago')  # Cambia esto a tu zona horaria local
    hora_local = hora_utc.astimezone(timezone_local).time()


    # nombre archivo
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_file_name = f"{paci_nombre}_{fecha}.wav"
    file_path = os.path.join(paciente_path, new_file_name)

    # obtener el archivo de audio de telegram (descarga)
    ogg_temp_path = os.path.join(paciente_path, f"{paci_nombre}_{fecha}.ogg")
    file.download(ogg_temp_path)

    # convertir de ogg a wav
    audio = AudioSegment.from_ogg(ogg_temp_path)
    audio.export(file_path, format="wav")
    os.remove(ogg_temp_path)

    # guardado del registro en la tabla correspondiente
    ruta_db = f"{paci_nombre}/{new_file_name}"
    PacienteAudioIngesta.objects.create(
        url_audio=ruta_db,
        hora_audio=hora_local,
        fk_paciente_ingesta_id=ingesta_id
    )

    update.message.reply_text('Audio guardado exitosamente.')
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text('Conversación cancelada.')
    return ConversationHandler.END

def main():
    updater = Updater(token=settings.TELEGRAM_TOKEN, use_context=True)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECCIONAR_RECETA: [MessageHandler(Filters.text & ~Filters.command, seleccionar_receta)],
            SELECCIONAR_INGESTA: [MessageHandler(Filters.text & ~Filters.command, seleccionar_ingesta)],
            SUBIR_AUDIO: [MessageHandler(Filters.voice, guardar_audio)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()