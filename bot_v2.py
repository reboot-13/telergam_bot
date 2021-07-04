import pyowm
from pyowm.commons.enums import SubscriptionTypeEnum
from pyowm.utils.measurables import kelvin_to_celsius
from pyowm.utils import timestamps
import telebot
from telebot import types


config = {
    'subscription_type': SubscriptionTypeEnum.FREE,
    'language': 'ru',
    'connection': {
        'use_ssl': True,
        'verify_ssl_certs': True,
        'use_proxy': False,
        'timeout_secs': 5
    },
    'proxies': {
        'http': 'http://user:pass@host:port',
        'https': 'socks5://user:pass@host:port'
    }
}

owm = pyowm.OWM('48ae8745e6eb902edd15053fd9dcebbf', config=config)
bot = telebot.TeleBot('1898683125:AAE9Fq4bEmQbrlPoU7dF9IdDE72w9uW0CkQ')
city = 'Самара'
weather_mng = owm.weather_manager()

def check_weather_in_city(city):
    observation = weather_mng.weather_at_place(city)
    weather = observation.weather
    return weather

def check_forecast (city):
    three_h_forecaster = weather_mng.forecast_at_place(city, '3h')
    tomorrow_at_five = timestamps.tomorrow(17, 0)
    weather_tomorrow = three_h_forecaster.get_weather_at(tomorrow_at_five)
    return weather_tomorrow

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, f'Я бот. Приятно познакомиться, '
                          f'{message.from_user.first_name}' )


    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mrk1 = types.KeyboardButton("погода")
    mrk2 = types.KeyboardButton("погода на завтра")
    mrk3 = types.KeyboardButton("Изменить город")
    markup.row(mrk1, mrk2).add (mrk3)
    bot.send_message(message.chat.id, "Выберите в меню,что вам интересно",
                     reply_markup=markup)

city_array = [city] #список в который функция changing_city добавляет город
# из сообщения пользователя, нужен для глобализации city

@bot.message_handler(content_types=['text'])
def get_text_messages(message):

    cid = message.chat.id
    city = city_array[-1] #извлекает последний город из списка (хотя он по
    # идее там всегда один)

    weather = check_weather_in_city(city)
    weather_tomorrow = check_forecast(city)

    if message.text.lower() == 'изменить город':
        msg_city = bot.send_message(cid, 'Напишите город, в котором '
                                               'желаете узнать погоду')

        bot.register_next_step_handler(msg_city, changing_city )

    elif message.text.lower() == 'погода':
        bot.send_message(cid, "В городе " + city + " сейчас " +
                         weather.detailed_status + ' '  +
      '\nТемпература: ' + str(kelvin_to_celsius(weather.temp['temp'])) + '°С\n')

    elif message.text.lower() == 'погода на завтра':
        bot.send_message(cid, 'Температура завтра: ' + str(kelvin_to_celsius (
            weather_tomorrow.temp['temp'])) + ' °С')

    else:
        bot.send_message(message.from_user.id, 'Не понимаю, что это значит.')

def changing_city(message):
    city = message.text
    weather = check_weather_in_city(city)

    bot.send_message(message.from_user.id, "В городе " + city + " сейчас " +
                     weather.detailed_status + ' '  +
                     '\nТемпература: ' + str(
        kelvin_to_celsius(weather.temp['temp'])) + '°С')
    city_array.pop (0) #удаляет первый элемент списка, чтобы список не
    # увеличивался
    city_array.append(city)  #добавляет новый город в список


bot.polling(none_stop=True)


#todo: добавить массив с городами и проверять ввод города пользователя

