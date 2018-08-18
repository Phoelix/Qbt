
import logging
import requests
from SQLite import SQLite
from configparser import SafeConfigParser
from telegram import (ReplyKeyboardMarkup, ParseMode, ReplyKeyboardRemove)
from telegram.ext import (Updater,CommandHandler,MessageHandler,Filters,RegexHandler,
                          ConversationHandler)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

parser = SafeConfigParser()
parser.read('options.conf')

def start(bot, update):
    keyboard = [[]]



def main ():            # workplace
    updater = Updater(token)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            Q1:[RegexHandler(nextreg,q1),
                CommandHandler('start',start),
                CommandHandler('cancel',cancel)],

            CHECKANSWER:[
                RegexHandler(regex_answer,check),
                CommandHandler('start', start),
                CommandHandler('cancel',cancel)],

            GOAL:[
                RegexHandler(Gresultsreg,goal),
                CommandHandler('start', start),
                CommandHandler('cancel',cancel)],

            RESTART: [
                CommandHandler('start', start),
                CommandHandler('cancel',cancel)]
        },

        fallbacks=[CommandHandler('cancel',cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__=='__main__':
    main()
