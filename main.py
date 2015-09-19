import os

from flask import Flask
import twx.botapi as botapi

BOT_TOKEN = os.getenv("BOT_TOKEN")
CERT      = os.getenv("CERT")
CERT_KEY  = os.getenv("CERT_KEY")
HOST      = "azul-bot.herokuapp.com"
PORT      = 8443

app = Flask(__name__)
context = (CERT, CERT_KEY)

bot = botapi.TelegramBot(BOT_TOKEN)


@app.route("/debug")
def debug():
    ret = "BOT_TOKEN %s<br>CERT %s<br>KEY %s" % (BOT_TOKEN,
                                                 "".join(open(CERT).readlines()),
                                                 "".join(open(CERT_KEY).readlines()))
    return ret


# This strange string is part of the bot's token
# I use it so that only telegram hits it.
@app.route("/" + BOT_TOKEN, methods=['POST'])
def webhook():
    # update = telegram.update.Update.de_json(request.get_json(force=True))
    # bot.sendMessage(chat_id=update.message.chat_id, text='Hello, there')
    reply = "hola desde heroku"
    chat_id = 131602840
    bot.send_message(chat_id, reply).wait()
    return "OK"


@app.route("/get_updates")
def get_updates():
    return bot.get_updates()


@app.route("/set_webhook")
def set_webhook():
    file_info = botapi.InputFileInfo(os.path.split(CERT)[-1],
                                     open(CERT, "rb"),
                                     "multipart/form-data")
    cert = botapi.InputFile("document", file_info)
    ret = bot.set_webhook(url='https://%s:%s/%s' % (HOST, PORT, BOT_TOKEN))
                          # certificate=cert)
    if ret:
        return "webhook setup ok"
    return "webhook setup failed: %s" % ret


if __name__ == '__main__':
    set_webhook()

    app.run(host='0.0.0.0',
            port=PORT,
            ssl_context=context,
            debug=True)
