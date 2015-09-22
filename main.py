import os

import flask
import telegram

BOT_TOKEN = os.getenv("BOT_TOKEN")
HOST      = "azul-bot.herokuapp.com"
PORT      = 443

app = flask.Flask(__name__)

bot = telegram.Bot(BOT_TOKEN)


# This strange string is part of the bot's token
# I use it so that only telegram hits it.
@app.route("/" + BOT_TOKEN, methods=["POST"])
def webhook():
    # reply = "hola desde heroku"
    # chat_id = 131602840

    update = telegram.update.Update.de_json(flask.request.get_json(force=True))
    ret = bot.sendMessage(chat_id=update.message.chat_id, text='Hello, loco')

    return "OK" if ret else "FAIL"


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
