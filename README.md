Telegram Bot - Azul

This project is an implementation of a Telegram Bot.
https://core.telegram.org/bots

# Setup
source venv/bin/activate.fish

# Deploy
git push heroku master

# Setup config variables
heroku config:set BOT\_TOKEN=[TOKEN\_HERE]

# Check config files
heroku config

# Run local
heroku local
