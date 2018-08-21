
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

def start(bot, update):
    update.message.reply_text(str(RU.welcome1.format(update.effective_chat.first_name)))
    price = requests.get('https://min-api.cryptocompare.com/data/price?fsym=RUB&tsyms=BTC').json()
    pricenum = float(price['BTC'])
    min_sum = pricenum * 1000
    update.message.reply_text(str(RU.PricenFee3.format(min_sum, pricenum, 1))) # TODO Комиссия
    logger.info("User %s start the conversation." % update.message.from_user.first_name)
    user = update.message.from_user
    db = SQLite()
    try:
        db.use_your_power(
            sql='INSERT OR IGNORE INTO members (tgID, uname, fname) VALUES (?,?,?)',
            data=(user.id, user.name, user.first_name))
    except Error:
        logger.warn('User "%s", error "%s"' % (user.id, error))
        return INPUT
    return INPUT


def cancel (bot,update):    # /cancel function
    user = update.message.from_user
    logger.info("User %s canceled the conversation."%user.first_name)
    update.message.reply_text(str(RU.bye1).format(user.first_name), reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def error (bot,update,error):       # if the bot slove error in update
    logger.warn('Update "%s" caused error "%s"'%(update,error))


def inp(bot, update):
    user = update.message.from_user
    global temp

    if  re.match(r'[A-Za-z0-9]{34,40}', update.message.text):
        reg = re.match(r'[A-Za-z0-9]{34,40}', update.message.text).group(0)
        result = requests.get('https://blockchain.info/rawaddr/'+reg).json()
        i = Member.Member(user.id)
        i.add_wall(reg)
        temp.append(i)
        print(reg)
        logger.info("User %s input wallet." % user.first_name)
    elif re.match(r'[0-9]{13}',update.message.text):
        reg = re.search(r'[0-9]{13}', update.message.text).group(0)
        temp[user.id].add_trID(reg)
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
                MessageHandler(Filters.all, inp),
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
