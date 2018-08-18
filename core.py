
import RU
import re
import logging
import requests
from SQLite import SQLite
from sqlite3 import Error
from configparser import SafeConfigParser
from telegram import (ReplyKeyboardMarkup, ParseMode, ReplyKeyboardRemove)
from telegram.ext import (Updater,CommandHandler,MessageHandler,Filters,RegexHandler,
                          ConversationHandler)

logging.basicConfig(filename="WORKLOG.log", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

parser = SafeConfigParser()
parser.read('options.conf')

INPUT,WALLET = range(2)

temp = ()

def start(bot, update):
    keyboard = [[RU.buyBTC_btn]]
    update.message.reply_text(str(RU.welcome), reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    logger.info("User %s start the game." % update.message.from_user.first_name)
    return INPUT


def cancel (bot,update):    # /cancel function
    user = update.message.from_user
    logger.info("User %s canceled the conversation."%user.first_name)
    update.message.reply_text(str(RU.bye_a).format(user.first_name), reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def error (bot,update,error):       # if the bot slove error in update
    logger.warn('Update "%s" caused error "%s"'%(update,error))


def inp(bot, update):
    global temp
    user = update.message.from_user
    db = SQLite()
    try:
        i ={'userID': temp[int(user.id)]}
    except :
        try:
            i = {'userID': int(db.get_member(user.id))}
        except :
            logger.warn('User "%s", error "%s"' % (user.id, error))
            try:
                db.add_member(data=(user.id, user.name, user.first_name))
                i = { 'userID': user.id}
            except Error:
                logger.warn('User "%s", error "%s"' % (user.id, error))
                return INPUT
    reg =  re.search(r'[A-Za-z0-9]{34,40}', update.message.text).group(0)
    if re.match(r'[A-Za-z0-9]{34,40}', update.message.text):
        result = requests.get('https://blockchain.info/rawaddr/'+reg).json()
        i['wallet'] = reg
        print(result)
        logger.info("User %s input wallet." % user.first_name)
    logger.info("User %s input end block." % user.first_name)
    update.message.reply_text(RU.inputVal)
    return INPUT



def main ():            # workplace
    updater = Updater(parser.get('core', 'token'))
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            INPUT:[
                MessageHandler(Filters.text, inp),
                CommandHandler('start',start),
                CommandHandler('cancel',cancel)],
        },

        fallbacks=[CommandHandler('cancel',cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__=='__main__':
    main()
