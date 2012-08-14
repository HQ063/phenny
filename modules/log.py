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

def printlog(phenny, to, log):
	print >> sys.stderr, log
	for x in log:
		phenny.msg(to, x[2]+' '+x[0]+': '+x[1])

def showlog(phenny, input):
	printlog(phenny, input.nick, getCursor().execute('''SELECT user, message, datetime(datetime, '-3 hours') 
									FROM messages
									WHERE (channel = ? OR channel ='') 
									AND datetime > (SELECT MAX(datetime) FROM messages WHERE event IN ('PART', 'QUIT') AND user = ?) 
									ORDER BY datetime ASC''', (input.group() ,input.nick)))#
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

if __name__ == '__main__': 
   print __doc__.strip()