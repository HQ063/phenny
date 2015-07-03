#!/usr/bin/env python
"""
log.py - Phenny Log Module
Copyright 2012, HQ063, hq063.com.ar
Licensed under GPL

"""

import os, re, time, random, sys, sqlite3
import web

sqliteCursor = None

def getCursor():
	global sqliteCursor
	if  sqliteCursor is None:
		conn = sqlite3.connect('log.db')
		conn.isolation_level = None
		c = conn.cursor()
		c.execute('CREATE TABLE IF NOT EXISTS messages(user varchar, channel varchar, event varchar, message varchar, datetime datetime)') 
		sqliteCursor = c
	return sqliteCursor

def printlog(phenny, to, log, printId = False):
	print >> sys.stderr, log
	for x in log:
		phenny.msg(to, ('['+str(x[3])+'] ' if printId else '') + x[2]+' '+x[0]+': '+x[1])

def showlog(phenny, input):
	printlog(phenny, input.nick, getCursor().execute('''SELECT user, message, datetime(datetime, '-3 hours') 
									FROM messages
									WHERE (channel = ? OR channel ='') 
									AND datetime > (SELECT MAX(datetime) FROM messages WHERE event IN ('PART', 'QUIT') AND user = ?) 
									ORDER BY datetime ASC''', (input.sender ,input.nick)))#
showlog.rule = r'.*'
showlog.event = 'JOIN'
showlog.priority = 'low'
showlog.thread = False

def log(phenny, input):
	message = input.group()
	if input.event == 'QUIT':
		message = 'has quit ('+input.group()+')' 
	elif input.event == 'NICK':
		message = 'is now ' + input.group()
	elif input.event == 'JOIN':
		input.sender =  input.group()
		message = 'has joined.'
	elif input.event == 'PART':
		message = 'has leave the channel.'
	elif input.event == 'MODE':
		message = 'has puts mode: ' + input.group()
	if input.sender is None:
		input.sender = ''
	if input.sender in phenny.channels or input.sender == '':
		getCursor().execute('INSERT INTO messages(user, channel, event, message, datetime) VALUES(?,?,?,?,datetime(\'now\'))', (input.nick, input.sender, input.event, message))
log.priority = 'low'
log.event = ['*', '!PING']
log.rule = r'.*'
log.thread = False

# def clearLog(phenny, input):
	# if(input.admin)
		# getCursor().execute('DELETE FROM messages')
	# phenny.say('Log deleted')
# clearLog.commands = ['clearLog']
# clearLog.priority = 'low'
# clearLog.thread = False

lastQuery = None
lastPage = 0
def searchLog(phenny, input):
	global lastQuery, lastPage
	query = '%'+input.group(2)+'%'
	if query == lastQuery:
		lastPage = lastPage + 1
	else:
		lastPage = 0
	lastQuery = query
	#pagina = 0#int(input.group(3)) if input.groups > 2 else 0
	if not query:
		return phenny.reply('.searchLog what?')
	printlog(phenny, input.sender, getCursor().execute('''SELECT user, message, datetime(datetime, '-3 hours'), _rowid_ FROM messages WHERE message not like '.searchLog%' and (channel = ? OR channel ='') AND message LIKE ? ORDER BY datetime DESC LIMIT '''+str(lastPage*10)+''', 10''', (input.sender, query)), True)
searchLog.commands = ['searchLog']
searchLog.priority = 'high'
searchLog.example = '.searchLog swhack'
searchLog.thread = False

def contextLog(phenny, input):
	id = input.group(2)
	if not id:
                return phenny.reply('.contextLog what?')
	printlog(phenny, input.sender, getCursor().execute('''select user, message, datetime(datetime, '-3 hours'), rowid from (select * from (select *,rowid from messages where rowid <= ? order by rowid desc limit 6) union select *,rowid from messages where rowid > ? order by rowid asc limit 11)''', (id, id)), True)
contextLog.commands = ['contextLog']
contextLog.priority = 'high'
contextLog.example = '.contextLog swhack'
contextLog.thread = False

if __name__ == '__main__': 
   print __doc__.strip()
