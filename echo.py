#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler
import RU
import re
import logging
import requests
from SQLite import SQLite
from sqlite3 import Error
#from telegram.ext import (Updater,CommandHandler,MessageHandler,Filters,RegexHandler)


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(bot, update):
    update.message.reply_text(str(RU.welcome1.format(update.effective_chat.first_name)))
    price = requests.get('https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=RUB').json()
    pricenum = float(price['RUB'])
    min_sum = 1000.0/pricenum
    update.message.reply_text(str(RU.PricenFee3.format(min_sum, pricenum, 1)))  # TODO Комиссия
    logger.info("User %s start the conversation." % update.message.from_user.first_name)
    user = update.message.from_user
    db = SQLite()
    try:
        db.use_your_power(
            sql='INSERT OR  IGNORE  INTO    members (tgID, uname, fname) VALUES (?,?,?)',
            data=(user.id, user.name, user.first_name))
    except Error:
        return  logger.warning('User "%s", error "%s"' % (user.id, error))
    try:
        db.use_your_power(
            sql='INSERT OR IGNORE INTO tempt (tgID) values (?)',
            data=(user.id,))
    except Error:
        logger.warning('User "%s", error "%s"' % (user.id, error))



def admin(bot, update):
    update.message.reply_text('Help!')


def echo(bot, update):
    user = update.message.from_user
    text = update.message.text
    try: x = float(text)
    except Exception: pass
    db = SQLite()
    techsup = db.use_your_power('SELECT val FROM variables WHERE name = "techsupp"').fetchall()[0][0]
    comission = db.use_your_power('SELECT val FROM variables WHERE name = "comission"').fetchall()[0][0]  # TODO commision


    if re.match(r'[A-Za-z0-9]{34,40}', text):                                         # BTC Wallet
        wallet = re.match(r'[A-Za-z0-9]{34,40}', text).group(0)
        try: result = requests.get('https://blockchain.info/rawaddr/'+wallet).json()
        except: return update.message.reply_text(str(RU.wallNoExist1.format(wallet)+RU.techSupport1.format(techsup)))
        update.message.reply_text(str(RU.wallExist1.format(wallet)))
        sql = 'replace into tempt(ID, tgID, RtoB, wallet, trID, status) values (?,?,?,?,?,?)'
        data = ('select id from tempt where tgID = {}'.format(user.id),
                user.id,
                'select RtoB from tempt where tgID = {}'.format(user.id),
                wallet,
                'select trID from tempt where tgID = {}'.format(user.id),
                'select status from tempt where tgID = {}'.format(user.id))


    elif re.match(r'[0-9]{13}', text):                                                  # QIWI Transaction
        trID = re.search(r'[0-9]{13}', text).group(0)
        sql = 'replace into tempt(ID, tgID, RtoB, wallet, trID, status) values (?,?,?,?,?,?)'
        data = ('select id from tempt where tgID = {}'.format(user.id),
                user.id,
                'select RtoB from tempt where tgID = {}'.format(user.id),
                'select wallet from tempt where tgID = {}'.format(user.id),
                trID,
                'select status from tempt where tgID = {}'.format(user.id))


    elif 0.0001<float(text)<100000:          # RUB to exchange TODO regexp to find value
        update.message.reply_text(str(RU.inputVal))
        x = float(text)
        req = requests.get(
            'https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=RUB').json()
        if 1000<x<100000:
            btc =x/float(req['RUB'])
            RtoB = "{0:.7f}".format(btc)
        elif 0.0001<x<10.0:
            rub = x * float(req['RUB'])
            RtoB = "{0:.2f}".format(rub)
        else: return update.message.reply_text(RU.incorrectnum)
        sql = 'replace into tempt(ID, tgID, RtoB, wallet, trID, status) values (?,?,?,?,?,?)'
        data = ('select id from tempt where tgID = {}'.format(user.id),
                user.id,
                RtoB,
                'select wallet from tempt where tgID = {}'.format(user.id),
                'select trID from tempt where tgID = {}'.format(user.id),
                'select status from tempt where tgID = {}'.format(user.id))

    else:
        update.message.reply_text(str(RU.oops+'\n'+RU.techSupport1.format()))

    db.use_your_power(sql, data)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    db = SQLite()
    sql = "SELECT val FROM variables WHERE name = (?)"
    admResult = db.use_your_power(sql, ('admin',)).fetchall()
    adm = admResult[0][0].split(' ')
    token = db.use_your_power(sql, ('token',)).fetchall()

    updater = Updater(token[0][0])
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", admin,Filters.user(username=adm)))
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()