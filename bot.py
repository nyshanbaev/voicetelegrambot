import os
import telebot
import requests
import speech_recognition as sr
import subprocess
import datetime
from gtts import gTTS
import os
from decouple import config

logfile = str(datetime.date.today()) + '.log'
token = config('token')
bot = telebot.TeleBot(token)


def audio_to_text(dest_name: str):

    r = sr.Recognizer()
    message = sr.AudioFile(dest_name)
    with message as source:
        audio = r.record(source)
    result = r.recognize_google(audio, language="ru_RU")
    return result


@bot.message_handler(content_types=['voice'])
def get_audio_messages(message):

    try:
        print("Started recognition...")
        file_info = bot.get_file(message.voice.file_id)
        path = file_info.file_path
        fname = os.path.basename(path) 
        doc = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path))
        with open(fname+'.oga', 'wb') as f:
            f.write(doc.content)
        process = subprocess.run(['ffmpeg', '-i', fname+'.oga', fname+'.wav'])
        result = audio_to_text(fname+'.wav') 
        bot.send_message(message.from_user.id, format(result))
    except sr.UnknownValueError as e:

        bot.send_message(message.from_user.id,  "Прошу прощения, но я не разобрал сообщение, или оно поустое...")
        with open(logfile, 'a', encoding='utf-8') as f:
            f.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + ':' + str(message.from_user.id) + ':' + str(message.from_user.first_name) + '_' + str(message.from_user.last_name) + ':' + str(message.from_user.username) +':'+ str(message.from_user.language_code) + ':Message is empty.\n')
    except Exception as e:

        bot.send_message(message.from_user.id,  "Что-то пошло через жопу, но наши смелые инженеры уже трудятся над решением... \nДа ладно, никто эту ошибку исправлять не будет, она просто потеряется в логах.")
        with open(logfile, 'a', encoding='utf-8') as f:
            f.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + ':' + str(message.from_user.id) + ':' + str(message.from_user.first_name) + '_' + str(message.from_user.last_name) + ':' + str(message.from_user.username) +':'+ str(message.from_user.language_code) +':' + str(e) + '\n')
    finally:
        
        os.remove(fname+'.wav')
        os.remove(fname+'.oga')


@bot.message_handler(content_types=['text'])
def speak(message):
    text = message.text
    language = 'ru' 
    tts = gTTS(text=text, lang=language)
    file_name = 'speech.mp3'
    tts.save(file_name)
    chat_id = message.chat.id
    audio = open(file_name, 'rb')
    bot.send_audio(chat_id, audio)
    os.remove(file_name)


bot.polling(none_stop=True, interval=0)