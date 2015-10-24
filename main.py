# -*- coding: utf-8 -*-
import logging
import os
import re
import requests

from datetime import datetime
from dateutil import tz

import flask
import telebot

BOT_TOKEN = os.getenv("BOT_TOKEN")
HOST      = "azul-bot.herokuapp.com"
PORT      = 443

app = flask.Flask(__name__)

bot = telebot.TeleBot(BOT_TOKEN)
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

BASE_URL = "http://price-tracker.herokuapp.com/api/v1/"
SYMBOLS_URL = BASE_URL + "symbols/{currencies}/{src}"

MARKDOWN = "Markdown"

CMD_START      = "start"
CMD_HELP       = "help"
CMD_ABOUT      = "about"
CMD_COTIZACION = "cotizacion"

SYMBOLS = frozenset(["USDARS", "USDARSB", "BTCUSD", "BTCARS"])
FROM_TO = {"USDARS": ("USD", "ARS"),
           "USDARSB": ("USD", "ARSB"),
           "BTCUSD": ("BTC", "USD"),
           "BTCARS": ("BTC", "ARSB"),
}

markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
markup.add("USDARSB", "USDARS")
markup.add("BTCUSD", "BTCARS")

def get_local_time(strdate):
    try:
        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        utc = datetime.strptime(strdate, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=from_zone)
        # Convert time zone
        local = utc.astimezone(to_zone)
        return local.strftime("%b %d %H:%M")
    except:
        return ""


def parse_text(text):
    """Returns a tuple with the amount and the currencies to convert.
    i.e. "1,23 usdars" -> (1.23, "USDARS")
    "1,23usdars" -> (1.23, "USDARS")
    "1.23USDARS" -> (1.23, "USDARS")
    "usdars" -> (1, "USDARS")
    """
    try:
        input = filter(None, re.split('([0-9.,]+)\s*(\\D+)', text.upper()))
        if len(input) == 1:
            if input[0] in SYMBOLS:
                return (float(1), input[0])
            return None
        if len(input) == 2 and input[1] in SYMBOLS:
            input[0].replace(",", ".")
            return (float(input[0]), input[1])
    except Exception:
        pass
    return None


def isNone(var, default=0):
    if var is None:
        return default
    return var


@bot.message_handler(func=lambda msg: parse_text(msg.text))
def convert(message):
    amount, currs = parse_text(message.text)
    src = "ambito" if currs.startswith("USD") else ("satoshitango" if currs.endswith("ARS") else "bitstamp")
    req = requests.get(SYMBOLS_URL.format(currencies=currs, src=src))
    data = req.json().get("data", {})
    ask = amount * isNone(data.get("ask"))
    bid = amount * isNone(data.get("bid"))
    avg = (ask + bid) / 2.0
    template = """{amount} {curr[0]} =
    {ask:.2f} {curr[1]} Compra
    {bid:.2f} {curr[1]} Venta
    {avg:.2f} {curr[1]} Promedio

    Fuente: {src} {update}"""
    text = template.format(amount=amount,
                           curr=FROM_TO[currs],
                           ask=ask,
                           bid=bid,
                           avg=avg,
                           src=src.capitalize(),
                           update=get_local_time(data.get("stats", {}).get("last_change", "")))

    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(commands=[CMD_START, CMD_HELP])
def send_welcome(message):
    bot.send_message(message.chat.id,
                     "Hola, enviame el tipo de cambio que deseas. Por ej. 2.3btcusd",
                     reply_markup=markup)


@bot.message_handler()
def fallback(message):
    bot.send_message(message.chat.id,
                     "No entiendo.",
                     reply_markup=markup)


# This strange string is part of the bot's token
# I use it so that only telegram hits it.
@app.route("/" + BOT_TOKEN, methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(flask.request.get_json(force=True))
    bot.process_new_messages([update.message])
    return "OK"


@app.route("/updates")
def updates():
    import json
    ret = bot.get_updates()
    return json.dumps(ret)


@app.route("/remove_webhook")
def remove_webhook():
    ret = bot.setWebhook(webhook_url="")
    return "OK" if ret else "FAIL"


@app.route("/set_webhook")
def setWebhook():
    api_url_base = "https://api.telegram.org/bot" + BOT_TOKEN + "/setWebhook"
    webhook_url = "https://%s:%s/%s" % (HOST, PORT, BOT_TOKEN)
    return requests.post(api_url_base, data={"url": webhook_url})
    # ret = bot.setWebhook(webhook_url='https://%s:%s/%s' % (HOST, PORT, BOT_TOKEN))
    # return "OK" if ret else "FAIL"


if __name__ == '__main__':
    # For debugging purposes
    app.run(host="127.0.0.1",
            port=5000,
            debug=True)
