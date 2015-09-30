# -*- coding: utf-8 -*-
import logging
import os
import re
import requests

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
SYMBOLS_URL = BASE_URL + "symbols/{currencies}/ambito"

MARKDOWN = "Markdown"

CMD_START      = "start"
CMD_HELP       = "help"
CMD_ABOUT      = "about"
CMD_COTIZACION = "cotizacion"

USDARSB = "USD BLUE"
USDARS  = "USD Oficial"
BTCUSD  = "BTC USD"
BTCARS  = "BTC ARS"

SYMBOLS = frozenset(["USDARS", "USDARSB"])
FROM_TO = {"USDARS": ("USD", "ARS"),
           "USDARSB": ("USD", "ARSB")
}

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
        if len(input) == 2:
            input[0].replace(",", ".")
            return (float(input[0]), input[1])
    except Exception:
        pass
    return None


@bot.message_handler(func=lambda msg: parse_text(msg.text))
def convert(message):
    amount, currs = parse_text(message.text)
    req = requests.get(SYMBOLS_URL.format(currencies=currs))
    data = req.json()["data"]
    ask = amount * data["ask"]
    bid = amount * data["bid"]
    avg = (ask + bid) / 2.0
    template = """{amount:.4f} {curr[0]} = {ask:.4f} {curr[1]} Compra
    {amount:.4f} {curr[0]} = {bid:.4f} {curr[1]} Venta
    {amount:.4f} {curr[0]} = {avg:.4f} {curr[1]} Promedio

    Fuente: Ambito Financiero {update}"""
    text = template.format(amount=amount,
                           curr=FROM_TO[currs],
                           ask=ask,
                           bid=bid,
                           avg=avg,
                           update=data["updated_on"])
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=[CMD_START, CMD_HELP])
def send_welcome(message):
    # bot.reply_to(message, "Howdy, how are you doing?")
    bot.send_message(message.chat.id, "Howdy, how are *you* doing?", parse_mode="Markdown")


# This strange string is part of the bot's token
# I use it so that only telegram hits it.
@app.route("/" + BOT_TOKEN, methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(flask.request.get_json(force=True))
    bot.process_new_messages([update.message])
    return "OK"
    # update = telegram.update.Update.de_json(flask.request.get_json(force=True))
    # if update.message.text.startswith(CMD_COTIZACION):
    #     custom_keyboard = [[USDARSB, USDARS],
    #                        [BTCUSD, BTCARS]]
    #     reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard,
    #                                                 one_time_keyboard=True)
    #     return bot.sendMessage(chat_id=update.message.chat_id,
    #                            text="Eleji una moneda.",
    #                            reply_markup=reply_markup)

    # elif update.message.text.startswith(USDARSB):
    #     return bot.sendMessage(chat_id=update.message.chat_id,
    #                            text = "Ambito:  $XXX")
    # msg = "No entiendo. Escribime /help para que te entienda."
    # return bot.sendMessage(chat_id=update.message.chat_id, text=msg)


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
    ret = bot.setWebhook(webhook_url='https://%s:%s/%s' % (HOST, PORT, BOT_TOKEN))
    return "OK" if ret else "FAIL"


if __name__ == '__main__':
    # For debugging purposes
    app.run(host="127.0.0.1",
            port=5000,
            debug=True)
