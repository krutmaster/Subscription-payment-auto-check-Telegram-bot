# by krutmaster (telegram: @krutmaster1)
import telebot
import time
import datetime
import random
import json
import socketio


# Classes
from settings import Settings
from user import User


settings = Settings.open()
boss = ''  # ID Owner channel
bot = telebot.TeleBot(settings.token)
TOKEN = settings.donation
sio = socketio.Client()


@bot.message_handler(commands=["start"])
def start(message):
    id = str(message.chat.id)
    name = message.from_user

    if name.last_name:
        name = f'{name.first_name} {name.last_name}'
    else:
        name = name.first_name

    bot.send_message(id, f'Привет, {name}. Здесь ты можешь оплатить месяц доступа к каналу с перезаливами ***.\nЦена - 100 рублей')
    user = User.get_user(id)
    end_date = datetime.datetime.fromtimestamp(user.time) if user and user.time else 0
    today = datetime.datetime.now()

    if not user or (end_date and today > end_date):
        text = 'У вас нет действующей подписки. Нажмите команду /pay, чтобы оплатить'
    elif end_date and today < end_date:
        text = f'У вас есть действующая подписка до {end_date.strftime("%d.%m %H:%M")}\nВы можете заранее оплатить следующий месяц командой /pay'

    bot.send_message(id, text)


@bot.message_handler(commands=["pay"])
def pay(message):
    id = str(message.chat.id)

    try:
        code = str(random.randint(1000, 9999))
        user = User.get_user(id)

        if not user:
            user = User(id, code)
            user.create_user()
        else:
            user.set_code(code)

        bot.send_message(id, f'Перейдите по ссылке доната https://www.donationalerts.com/r/*** и отправьте 100 рублей, '
                             f'указав в сообщении только код: {code}\nКод никому показывать нельзя. Также при оплате можете '
                             f'нажать на сердечко и покрыть комиссию (чтобы я получил чистые 100), но это по желанию, считайте это чаевыми :)'
                             f'\n\nПосле оплаты возвращайтесь в бота и нажмите /check_payment')
    except Exception as e:
        bot.send_message(boss, f'Pay:\n{e}')


@bot.message_handler(commands=["check_payment"])
def check_payment(message):
    id = str(message.chat.id)

    try:
        user = User.get_user(id)

        if user.code == 1:
            user.set_code(0)
            end_date = datetime.datetime.fromtimestamp(user.time) if user.time else 0
            today = datetime.datetime.now()

            if not end_date or today > end_date:
                end_date = today + datetime.timedelta(days=30)
                invite = True
            else:
                end_date += datetime.timedelta(days=30)
                invite = False
            user.set_time(end_date.timestamp())
            channel = ''  # Channel ID
            name = f'{user.id} on {today.strftime("%m.%d %H:%M")}'

            if invite:
                link = bot.create_chat_invite_link(channel, name, member_limit=1).invite_link
                bot.send_message(id, f'*Спасибо!*\n\nВаша подписка активна до {end_date.strftime("%d.%m %H:%M")}.\n\nВаша ссылка на канал: {link}'
                                 f'\n\nОна работает только на один переход!', parse_mode='Markdown')
            else:
                bot.send_message(id, f'*Спасибо!*\n\nВаша подписка продлена до {end_date.strftime("%d.%m %H:%M")}', parse_mode='Markdown')

        else:
            bot.send_message(id, 'Оплата не подтверждена')

    except Exception as e:
        bot.send_message(boss, f'Check_pay:\n{e}')


@bot.message_handler(commands=["check_subs"])
def check_subs(message):
    id = str(message.chat.id)

    if id == boss:

        try:
            users = User.get_all()
            channel = ''  # Channel ID
            count = 0

            for user in users:
                end_date = datetime.datetime.fromtimestamp(user.time) if user.time else 0
                today = datetime.datetime.now()

                if end_date and today > end_date:
                    bot.kick_chat_member(channel, user.id)
                    user.remove()
                    count += 1

            bot.send_message(boss, f'Кикнуто {count}')
        except Exception as e:
            bot.send_message(boss, f'Check_subs:\n{e}')
            bot.send_message(id, 'Пошёл ручной расчёт')
            manual_check_subs(message)


@bot.message_handler(commands=["manual_check_subs"])
def manual_check_subs(message):
    id = str(message.chat.id)

    if id == boss:

        try:
            users = User.get_all()

            for user in users:
                end_date = datetime.datetime.fromtimestamp(user.time) if user.time else 0
                today = datetime.datetime.now()
                text = 'Список на кик:'

                if end_date and today > end_date:
                    name = message.from_user

                    if name.last_name:
                        name = f'{name.first_name} {name.last_name}'
                    else:
                        name = name.first_name

                    text += f'\n{name} {end_date.strftime("%d.%m %H:%M")}'

            bot.send_message(id, text)
        except Exception as e:
            bot.send_message(boss, f'Manual_heck_subs:\n{e}')


@bot.message_handler()
def handle_text(message):
    bot.reply_to(message, 'Нажми /start, пользуйся командами')


@sio.on('connect')
def donation_on_connect():
    sio.emit('add-user', {"token": TOKEN, "type": "alert_widget"})

@sio.on('donation')
def donation_on_message(data):
    try:
        payment = json.loads(data)
        currency = ['RUB', 'USD', 'EUR']

        if payment['currency'] in currency:
            code = int(payment['message'])

            if not User.confirm_payment(code):
                print('Чот не так')

    except Exception as e:
        bot.send_message(boss, f'Pay:\n{e}')


if __name__ == '__main__':
    sio.connect('wss://socket.donationalerts.ru:443', transports='websocket')
    bot.polling(none_stop=True)
