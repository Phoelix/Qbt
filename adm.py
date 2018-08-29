import re
import RUadm
import SQLite
import logging
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

db = SQLite.SQLite()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

def QIWI(bot, update):
    db = SQLite.SQLite()
    b = RUadm.QIWIwalList
    a = db.use_your_power('select WallID from QIWI').fetchall()
    for i in a:
        for y in i:
            b += str(y)+'\n'
    return update.message.reply_text(str(RUadm.QIWIhelp+b))

def QIWIadd(bot, update):
    db = SQLite.SQLite()
    if re.match(r'^/QIWIadd$', update.message.text):
        return update.message.reply_text(RUadm.QIWIaddhelp)
    else:
        a = str(update.message.text).split(' ')
        if len(a) in range(2,3):
            try:
                headers = {'Accept': 'application/json',
                       'Authorization': 'Bearer {}'.format(str(a[1]))}
                b = requests.get('https://edge.qiwi.com/person-profile/v1/profile/current?authInfoEnabled=false&userInfoEnabled=false&contractInfoEnabled=true', headers=headers).json()
                WallID = b['contractInfo']['contractId']
            except: return update.message.reply_text(RUadm.QIWIwrongtoken)
            db.use_your_power('replace into QIWI(WallID, token) values(?,?)', (WallID,a[1]))
            return update.message.reply_text(RUadm.QIWIadded.format(WallID))

def QIWIdel(bot, update):
    db = SQLite.SQLite()
    a = db.use_your_power('select WallID from QIWI').fetchall()
    wlist = []
    for i in a:
        for y in i:
            wlist.append([InlineKeyboardButton(str(y), callback_data=str(y))])
    keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
                 InlineKeyboardButton("Option 2", callback_data='2')],

                [InlineKeyboardButton("Option 3", callback_data='3')]]

    reply_markup = InlineKeyboardMarkup(wlist)

    return update.message.reply_text(RUadm.QIWIdelhelp, reply_markup=reply_markup)


def LBTC(bot, update):
    db = SQLite.SQLite()
    if re.match(r'^/LBTC$', update.message.text):
        return update.message.reply_text(RUadm.LBTChelp)
    else:
        a = str(update.message.text).split(' ')
        if len(a) == 3:
            db.use_your_power('replace into variables(name, val) VALUES (?,?)',)


def com(bot, update):
    db = SQLite.SQLite()
    return update.message.reply_text(RUadm.comhelp)

def tech(bot, update):
    db = SQLite.SQLite()
    return update.message.reply_text(RUadm.techhelp)

def stat(update):
    update.split(' ')
    if len(update) == 5:
        u = update
        if u[1]

def info(bot, update):
    db = SQLite.SQLite()
    return  update.message.reply_text(RUadm.infohelp)

def infonow(bot, update):
    db = SQLite.SQLite()
    return  #update.message.reply_text('infonow')

def infohist(bot, update):
    db = SQLite.SQLite()
    return  update.message.reply_text(RUadm.infohisthelp)

def infomemb(bot, update):
    db = SQLite.SQLite()
    return  update.message.reply_text(RUadm.infomembhelp)

def button(bot, update):
    db = SQLite.SQLite()
    query = update.callback_query
    db.use_your_power('delete from QIWI where WallID = (?)', (query.data,))
    bot.edit_message_text(text=RUadm.QIWIdeleted.format(query.data),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)