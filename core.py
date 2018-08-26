#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler
import RU
import re
import random
import lbcAPI
import logging
import requests
from sqlite3 import Error
from SQLite import SQLite
#from telegram.ext import (Updater,CommandHandler,MessageHandler,Filters,RegexHandler)

db = SQLite()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
sql = 'SELECT val FROM variables WHERE name = (?)'
hmack = db.use_your_power(sql,('locBTCk',)).fetchall()[0][0]
hmacs = db.use_your_power(sql, ('locBTCs',)).fetchall()[0][0]
conn = lbcAPI.hmac(hmack,hmacs)



def start(bot, update):
    db = SQLite()
    update.message.reply_text(str(RU.welcome1.format(update.effective_chat.first_name)))
    price = requests.get('https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=RUB').json()
    pricenum = float(price['RUB'])
    min_sum = 1000.0/pricenum
    update.message.reply_text(str(RU.PricenFee3.format(min_sum, pricenum, 1)))  # TODO Комиссия
    logger.info("User %s start the conversation." % update.message.from_user.first_name)
    user = update.message.from_user
    try:
        db.use_your_power(
            sql='INSERT OR  IGNORE  INTO    members (tgID, uname, fname) VALUES (?,?,?)',
            data=(user.id, user.name, user.first_name))
    except Error:
        return  logger.warning('User "%s", error "%s"' % (user.id, error))




def admin(bot, update):
    db = SQLite()
    update.message.reply_text('Help!')


def echo(bot, update):
    db = SQLite()
    user = update.message.from_user
    text = update.message.text
    try: x = float(text)
    except Exception: pass
    q = db.use_your_power('select count(*) from QIWI').fetchone()[0]
    try:
        a = db.use_your_power('select WallID from QIWI where ID = {}'.format(random.randint(1,q))).fetchall()[0][0]
        e = db.use_your_power(
            sql = 'INSERT OR IGNORE INTO tempt (tgID, onQIWI) values (?, ?)',
            data=(user.id, a)).fetchall()
    except Error:
        logger.warning('User "%s", error "%s"' % (user.id, error))
    techsup = db.use_your_power('SELECT val FROM variables WHERE name = "techsupp"').fetchall()[0][0]
    comission = db.use_your_power('SELECT val FROM variables WHERE name = "comission"').fetchall()[0][0]  # TODO commision


    if re.match(r'[A-Za-z0-9]{32,40}', text):                                         # BTC Wallet
        wallet = re.match(r'[A-Za-z0-9]{34,40}', text).group(0)
        try: result = requests.get('https://blockchain.info/rawaddr/'+wallet).json()
        except: return update.message.reply_text(str(RU.wallNoExist1.format(wallet)+RU.techSupport1.format(techsup)))
        update.message.reply_text(str(RU.wallExist1.format(wallet)))
        sql = 'update tempt set wallet = (?)'
        data = (wallet,)


    elif re.match(r'[0-9]{13}', text):                                                  # QIWI Transaction
        trID = re.search(r'[0-9]{13}', text).group(0)
        QIWIkey = 'ce003badcc56c2bd3d19b7dbaa3e3396'   #db.use_your_power('SELECT val FROM variables WHERE name = (?)', data=())
        url = 'https://edge.qiwi.com/payment-history/v2/transactions/'+trID
        qiwireq = requests.get(url, params={'Accept': 'application/json',
                                            'Authorization': 'Bearer {}'.format(QIWIkey)})
        print(qiwireq)
        sql = 'update tempt set trID = (?)'
        data = (trID,)


    elif 0.0001<float(text)<100000:          # RUB to exchange
        update.message.reply_text(str(RU.inputVal))
        x = float(text)
        req = requests.get(
            'https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=RUB').json()
        if 1000<x<100000:
            btc = round(x/float(req['RUB']),5)
            rub = x
        elif 0.0001<x<10.0:
            rub = round(x * float(req['RUB']),2)
            btc = x
        else: return update.message.reply_text(RU.incorrectnum)
        sql = 'update tempt set rub = (?), btc = (?)'
        data = (rub, btc)
    else:
        return update.message.reply_text(str(RU.oops+'\n'+RU.techSupport1.format(techsup)))

    e = db.use_your_power(sql, data).fetchall()
    sql = 'select * from tempt where tgID = (?)'
    data = (user.id,)
    monitor = db.use_your_power(sql, data).fetchall()
    print(e, monitor)
    if monitor[0][2] is not None and monitor[0][3] is not None and monitor[0][4] is not None and monitor[0][5] is not None and monitor[0][6] is not None:
        e = conn.call('POST', '/api/wallet-send/',
                  params={'address': monitor[0][4],
                          'amount': monitor[0][3]}).json()
        logger.info('Transaction returns:%s' % e)

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    db = SQLite()
    sql = "SELECT val FROM variables WHERE name = (?)"
    admResult = db.use_your_power(sql, ('admin',)).fetchall()
    adm = admResult[0][0].split(' ')

    updater = Updater(RU.Telegram_API_token)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", admin,Filters.user(username=adm)))
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()