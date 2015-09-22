# -*- coding: utf-8 -*-
import os

import flask
import telegram

BOT_TOKEN = os.getenv("BOT_TOKEN")
HOST      = "azul-bot.herokuapp.com"
PORT      = 443

app = flask.Flask(__name__)

bot = telegram.Bot(BOT_TOKEN)

CMD_START      = "/start"
CMD_HELP       = "/help"
CMD_ABOUT      = "/about"
CMD_COTIZACION = "/cotizacion"

USDARSB = "USD BLUE"
USDARS  = "USD Oficial"
BTCUSD  = "BTC USD"
BTCARS  = "BTC ARS"


# This strange string is part of the bot's token
# I use it so that only telegram hits it.
@app.route("/" + BOT_TOKEN, methods=["POST"])
def webhook():
    update = telegram.update.Update.de_json(flask.request.get_json(force=True))
    if update.message.text.startswith(CMD_COTIZACION):
        custom_keyboard = [[USDARSB, USDARS],
                           [BTCUSD, BTCARS]]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard,
                                                    one_time_keyboard=True)
        return bot.sendMessage(chat_id=update.message.chat_id,
                               text="Eleji una moneda.",
                               reply_markup=reply_markup)

    elif update.message.text.startswith(USDARSB):
        return bot.sendMessage(chat_id=update.message.chat_id,
                               text = "Ambito:  $XXX")
    msg = "No entiendo. Escribime /help para que te entienda."
    return bot.sendMessage(chat_id=update.message.chat_id, text=msg)


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
    app.run(host="0.0.0.0",
            port=PORT,
            debug=True)
