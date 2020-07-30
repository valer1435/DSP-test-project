import random

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


from help_functions import *



def get_voice_file(update, context):
    chat_id = update.message.chat.id
    file = context.bot.getFile(update.message.voice.file_id)
    if save_voice_file(file, str(chat_id)):
        context.bot.send_message(chat_id=chat_id, text="Успешно загрузил голосовое сообщение в .wav формат")
    else:
        context.bot.send_message(chat_id=chat_id, text="Произошла ошибка обработки аудиосообщения")


def get_random_voice(update, context):
    chat_id = update.message.chat.id
    chat_id_hash = get_md5(str(chat_id))
    if not os.path.exists(AUDIO_FOLDER):
        context.bot.send_message(chat_id=chat_id, text="Вы еще не отправили ни одного голосового сообщения")
        return
    if not os.path.exists(AUDIO_FOLDER+os.sep+chat_id_hash):
        context.bot.send_message(chat_id=chat_id, text="Вы еще не отправили ни одного голосового сообщения")
        return
    if not os.listdir(AUDIO_FOLDER+os.sep+chat_id_hash):
        context.bot.send_message(chat_id=chat_id, text="Нет подходящих сообщений")
        return
    path = AUDIO_FOLDER+os.sep+chat_id_hash+os.sep+random.choice(os.listdir(AUDIO_FOLDER+os.sep+chat_id_hash))
    context.bot.send_voice(chat_id=chat_id, voice=open(path, 'rb'))


def my_help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="""
                             Я бот! Отправьте мне голосовое сообщение и я сохраню его!
                             Отправьте мне фотографию и я определю, есть ли на ней лица!
                             /myVoice - отправить случайное записанное голосовое сообщение
                             /start - старт
                             /help - помощь""")


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Я бот! Отправьте мне голосовое сообщение или фотографию (/help - помощь)")


def evaluate_photos(update, context):
    photo = context.bot.getFile(update.message.photo[-1].file_id)
    faces_count, photo = process_photo(photo)
    if faces_count:
        context.bot.send_message(update.message.chat.id, f"Кол-во лиц на этой фотографии: {faces_count}, сохраняю")
        context.bot.send_photo(update.message.chat.id, photo)
    elif photo is None:
        context.bot.send_message(update.message.chat.id, "Произошла ошибка обработки изображения")
    else:
        context.bot.send_message(update.message.chat.id, "На этой фотографии нет лиц-не сохраняю")
        context.bot.send_photo(update.message.chat.id, photo)


updater = Updater(token=API_TOKEN, use_context=True)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

help_handler = CommandHandler('help', my_help)
dispatcher.add_handler(help_handler)

get_random_voice_handler = CommandHandler('myVoice', get_random_voice)
dispatcher.add_handler(get_random_voice_handler)

voice_handler = MessageHandler(Filters.voice,  get_voice_file)
dispatcher.add_handler(voice_handler)

photo_handler = MessageHandler(Filters.photo,  evaluate_photos)
dispatcher.add_handler(photo_handler)

updater.start_polling()
