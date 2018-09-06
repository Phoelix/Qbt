#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import core
import time
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
    if re.match(r'^/QIWIadd$|^/qiwiadd$', update.message.text):
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
    wlist.append([InlineKeyboardButton('<< Back >>', callback_data='back')])

    reply_markup = InlineKeyboardMarkup(wlist)

    return update.message.reply_text(RUadm.QIWIdelhelp, reply_markup=reply_markup)


def LBTC(bot, update):
    db = SQLite.SQLite()
    if re.match(r'^/LBTC$|^/lbtc$', update.message.text):
        return update.message.reply_text(RUadm.LBTChelp)
    else:
        a = str(update.message.text).split(' ')
        if len(a) == 3:
            data = '{} {}'.format(a[1], a[2])
            db.use_your_power('replace into variables(name, val) VALUES (?,?)',('locBTC',data))
            return update.message.reply_text(RUadm.LBTCadded)


def com(bot, update):
    db = SQLite.SQLite()
    if re.match(r'^/com$', update.message.text):
        c = db.use_your_power('select val from variables where name = "comission"').fetchall()[0][0]
        return update.message.reply_text(RUadm.comhelp.format(c))
    else:
        a = str(update.message.text).split(' ')
        db.use_your_power('replace into variables(name, val) VALUES (?,?)',('comission',a[1]))
        return update.message.reply_text(RUadm.comadded.format(a[1]))

def tech(bot, update):
    db = SQLite.SQLite()
    if re.match(r'^/tech$', update.message.text):
        c = db.use_your_power('select val from variables where name = "techsupp"').fetchall()[0][0]
        return update.message.reply_text(RUadm.techhelp.format(c))
    else:
        a = str(update.message.text).split(' ')
        db.use_your_power('replace into variables(name, val) VALUES (?,?)',('techsupp',a[1]))
        return update.message.reply_text(RUadm.techadded)


def stat(bot, update):
    db = SQLite.SQLite()
    u = update.message.text.split(' ')
    counter=0
    if len(u)==5:
        p=core.hookmask
        for i in u:
            if re.match(p,i):
                counter+=1
    if counter in range(4,5):
        res = db.use_your_power(core.sql,(core.data,)).fetchall()
        counter = 0
        keyboard = [[InlineKeyboardButton("Ok", callback_data='Ok')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(str(res), reply_markup=reply_markup)

def info(bot, update):
    db = SQLite.SQLite()
    return  update.message.reply_text(RUadm.infohelp)

def infonow(bot, update):
    db = SQLite.SQLite()
    a = db.use_your_power('select tgID, wallet, onQIWI from tempt').fetchall()
    b = []
    for i in a:
        b.append(' ||| '.join(str(v) for v in i))

    return  update.message.reply_text(RUadm.infonowhelp+'\n'.join(str(v) for v in b))

def infohist(bot, update):
    db = SQLite.SQLite()
    data = 10
    z = update.message.text.split(' ')
    if len(z) == 2:
        data = z[1]
    a = db.use_your_power('select tgID, wallet, btc, onQIWI, status from history ORDER BY ID DESC limit (?)', (data,)).fetchall()
    b = []
    for i in a:
        b.append(' || '.join(str(v) for v in i))
    return  update.message.reply_text(RUadm.infohisthelp+'\n\n'.join(str(v) for v in b))

def infomemb(bot, update):
    text = update.message.text.split(' ')
    if len(text) == 1:
        return update.message.reply_text(RUadm.infomembhelp)
    else:
        if re.match(r'^[0-9]{9}$',text[1]):
            data = text[1]
            a = db.use_your_power('select tgID, uname, fname from members where tgID = (?)', (data,)).fetchall()
        elif re.match(r'@*\w+',text[1]):
            data = text[1]
            a = db.use_your_power('select tgID, uname, fname from members where uname = (?)', (data,)).fetchall()
        b = []
        for i in a:
            b.append(' | '.join(str(v) for v in i))

        return update.message.reply_text(RUadm.infonowhelp + '\n'.join(str(v) for v in b))


def button(bot, update):
    db = SQLite.SQLite()
    query = update.callback_query
    if query.data == 'Ok':
        bot.edit_message_text(text=' and all of us',chat_id=query.message.chat_id,message_id=query.message.message_id)
    elif query.data == 'back':
        bot.edit_message_text(text=RUadm.QIWIhelp, chat_id=query.message.chat_id, message_id=query.message.message_id)
    else:
        db.use_your_power('delete from QIWI where WallID = (?)', (query.data,))
        bot.edit_message_text(text=RUadm.QIWIdeleted.format(query.data),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)