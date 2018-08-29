#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import RU
import re
import time
import adm
import lbcAPI
import logging
import requests
import threading
from sqlite3 import Error
from SQLite import SQLite
#from telegram.ext import (Updater,CommandHandler,MessageHandler,Filters,RegexHandler)

db = SQLite()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
sql = 'SELECT val FROM variables WHERE name = (?)'
data = 'locBTC'
hmac = str(db.use_your_power(sql,(data,)).fetchall()[0][0]).split(' ')
conn = lbcAPI.hmac(hmac[0],hmac[1])
hookmask = r'^M\w{2}|^G\w{2}|^f\w{6}|^y\w{2}'


def start(bot, update):
    db = SQLite()
    e = conn.call('GET', '/api/wallet-balance/').json()
    comission = db.use_your_power('SELECT val FROM variables WHERE name = "comission"').fetchall()[0][0]
    update.message.reply_text(str(RU.welcome1.format(update.effective_chat.first_name)))
    pricenum = float(db.use_your_power('select val from variables where name = "price"').fetchall()[0][0])
    min_sum = round(1000.0/pricenum, 5)
    update.message.reply_text(str(RU.balance.format(e['data']['total']['sendable'])+RU.PricenFee3.format(min_sum, pricenum, comission)))
    logger.info("User %s start the conversation." % update.message.from_user.first_name)
    user = update.message.from_user
    callback = adm.stat(bot, update)
    try:
        db.use_your_power(
            sql='INSERT OR  IGNORE  INTO    members (tgID, uname, fname) VALUES (?,?,?)',
            data=(user.id, user.name, user.first_name))
    except Error:
        return  logger.warning('User "%s", error "%s"' % (user.id, error))


def admin(bot, update): # TODO change source for admins list
    update.message.reply_text(RU.admStart1.format(update.message.from_user.first_name))



def echo(bot, update):
    db = SQLite()
    techsup = db.use_your_power('SELECT val FROM variables WHERE name = "techsupp"').fetchall()[0][0]
    comission = float(db.use_your_power('SELECT val FROM variables WHERE name = "comission"').fetchall()[0][0])
    user = update.message.from_user
    text = update.message.text
    try: x = float(text)
    except Exception: pass
    try:
        try:
            z = db.use_your_power('select tgID from tempt where tgID = (?)', (user.id,)).fetchall()[0]
        except:
            a = db.use_your_power('select WallID, min(counter) from QIWI limit 1').fetchall()[0][0]
            e = db.use_your_power(
                sql = 'INSERT OR IGNORE INTO tempt (tgID, onQIWI) values (?, ?)',
                data=(user.id, a)).fetchall()
            db.use_your_power('update QIWI set counter = counter + 1 where WallID = (?)',(a,) )
    except Error:
        logger.warning('User "%s", error "%s"' % (user.id, Error))


    if re.match(r'[A-Za-z0-9]{32,40}', text):                                         # BTC Wallet
        wallet = re.match(r'[A-Za-z0-9]{34,40}', text).group(0)
        try: result = requests.get('https://blockchain.info/rawaddr/'+wallet).json()
        except: return update.message.reply_text(str(RU.wallNoExist1.format(wallet)+RU.techSupport1.format(techsup)))
        update.message.reply_text(str(RU.wallExist1.format(wallet)))
        sql = 'update tempt set wallet = (?)'
        data = (wallet,)
        e = db.use_your_power(sql, data).fetchall()
        val = db.use_your_power('select rub, btc, onQIWI from tempt where tgID = (?)',(user.id,)).fetchall()[0]
        update.message.reply_text(str(RU.payonQIWI2.format(val[2],val[0])+RU.ifChange))


    elif re.match(r'[0-9]{10,15}', text):                                                  # QIWI Transaction
        trID = re.search(r'[0-9]{10,15}', text).group(0)
        try:
            transactChecker = db.use_your_power('select trID from history where trID = (?)', (trID,)).fetchall()[0]
            update.message.reply_text(str(RU.transactWasUsed+RU.techSupport1.format(techsup)))
        except:
            val = db.use_your_power('select rub, btc, onQIWI from tempt where tgID = (?)', (user.id,)).fetchall()[0]
            QIWIkey = db.use_your_power('select token from QIWI where WallID = (?)', (val[2],)).fetchall()[0][0]
              #db.use_your_power('SELECT val FROM variables WHERE name = (?)', data=())
            url = 'https://edge.qiwi.com/payment-history/v2/transactions/{}?'.format(trID)
            headers = {'Accept': 'application/json',
                       'Authorization': 'Bearer {}'.format(QIWIkey)}
            try: qiwireq = requests.get(url, headers=headers).json()
            except Error as e:
                logger.warning('User "%s", error "%s"' % (user.id, e))
                return update.message.reply_text(RU.oopsError1.format(e))
            if qiwireq['errorCode'] == 0:
                rPrice = float(db.use_your_power('select val from variables where name = "price"').fetchall()[0][0])
                rub = qiwireq['total']['amount']
                cominr = float(comission)*rPrice
                if float(rub) < cominr: return update.message.reply_text(str(RU.trnsctCheckNoMon1.format(rub)))
                btc = round(float(rub)/float(rPrice),5) - float(comission)
                sql = 'update tempt set rub= (?), btc=(?),trID = (?)'
                data = (rub, btc, trID)
                update.message.reply_text(str(RU.trnsctCheckGet2.format(rub, btc)))
                e = db.use_your_power(sql, data).fetchall()
                sql = 'select * from tempt where tgID = (?)'
                data = (user.id,)
                monitor = db.use_your_power(sql, data).fetchall()
                if monitor[0][2] is not None and monitor[0][3] is not None and\
                        monitor[0][4] is not None and \
                        monitor[0][5] is not None and monitor[0][6] is not None:

                    try:
                        e = conn.call('POST', '/api/wallet-send/',
                                      params={'address': monitor[0][4],
                                              'amount': monitor[0][3]}).json()
                    except:
                        logger.info('Transaction returns:%s' % e)
                        return db.use_your_power('update tempt set status = (?)', (e['error']['errors'],))
                    if e['error']:
                        db.use_your_power('update tempt set status = (?)', (str(e['error']['errors']),))
                        update.message.reply_text(RU.oopsError1.format(str(e['error']['errors'])))
                    else:
                        db.use_your_power('update tempt set status = (?)', ('Ok',))
                        update.message.reply_text(RU.transactOk)
            else:
                return update.message.reply_text(RU.transactNotFound+RU.techSupport1.format(techsup))



    elif 0.0001<float(text)<100000:          # RUB to exchange
        update.message.reply_text(str(RU.inputVal))
        x = float(text)
        rPrice = float(db.use_your_power('select val from variables where name = "price"').fetchall()[0][0])
        if 1000<=x<=100000:
            btc = round(x/float(rPrice),5) - float(comission)
            rub = x
        elif 0.0001<=x<=10.0:
            rub = round(x * float(rPrice)+ float(comission)*float(rPrice),2)
            btc = x
        else: return update.message.reply_text(RU.incorrectnum)
        sql = 'update tempt set rub = (?), btc = (?)'
        data = (rub, btc)
        update.message.reply_text(str(RU.enteredData2.format(rub, round(btc,4))))
        e = db.use_your_power(sql, data).fetchall()
    else:
        return update.message.reply_text(str(RU.oops+'\n'+RU.techSupport1.format(techsup)))


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)

def updater(interval):
    db = SQLite()
    try:
        req = requests.get(
        'https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=RUB').json()
        rub = req['RUB']
    except Error:
        logging.warning('Update price on cryptocompare fail %s' % str(req))
    try:
        db.use_your_power('update variables set val = (?) where name = "price"', (rub,))
    except Error as e:
        logging.warning('Update price on cryptocompare fail %s' % str(e))
    time.sleep(interval)


def main():
    admn = RU.Bot_Admins.split(' ')
    updater = Updater(RU.Telegram_API_token)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start",      start))
    dp.add_handler(CommandHandler("admin",      admin,          Filters.user(username=admn)))
    dp.add_handler(CommandHandler("QIWI",       adm.QIWI,       Filters.user(username=admn)))
    dp.add_handler(CommandHandler("QIWIadd",    adm.QIWIadd,    Filters.user(username=admn)))
    dp.add_handler(CommandHandler("QIWIdel",    adm.QIWIdel,    Filters.user(username=admn)))
    dp.add_handler(CommandHandler("LBTC",       adm.LBTC,       Filters.user(username=admn)))
    dp.add_handler(CommandHandler("lbtc",       adm.LBTC,       Filters.user(username=admn)))
    dp.add_handler(CommandHandler("com",        adm.com,        Filters.user(username=admn)))
    dp.add_handler(CommandHandler("tech",       adm.tech,       Filters.user(username=admn)))
    dp.add_handler(CommandHandler("info",       adm.info,       Filters.user(username=admn)))
    dp.add_handler(CommandHandler("infonow",    adm.infonow,    Filters.user(username=admn)))
    dp.add_handler(CommandHandler("infohist",   adm.infohist,   Filters.user(username=admn)))
    dp.add_handler(CommandHandler("infomemb",   adm.infomemb,   Filters.user(username=admn)))

    dp.add_handler(CallbackQueryHandler(adm.button))
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    t = threading.Thread(target=updater, args=(3600,))
    t.daemon = True
    t.start()
    main()