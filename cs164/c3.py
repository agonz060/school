#! /usr/bin/env python2
import socket
import select
import sys
import time
import getpass

try :
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
except socket.error:
	print( 'Failed to create socket')
	sys.exit()

# Server address variables
port = 8888
ip = socket.gethostbyname('')
#ip = "10.0.0.4"

s.connect((ip,port))

pwMsg1 = "password:"
pwMsg2 = "Password:"
menuMsg = "Menu"
currentPass = "current"
newMsg = "new"
loggingOut = "logging out"
newMsgRecved = "New message received"
formatReply = '\n'

inputs = [ s ]
outputs = [ ]
userIn = ""
newMsgFlag = 0

while(1) :

	readable,writable,exceptional = select.select(inputs,outputs,inputs)

	for s in readable:
		data = s.recv(1024)

		if newMsgRecved in data:
			print('\n*** New message received ***\n')
			newMsgFlag = 1
		else :
			print(data)

		if loggingOut in data:
			s.close()
			break
		if menuMsg in data:
			#print('Menu detected')
			#print('data: ',data)
			userIn = raw_input()
			reply = data + formatReply + userIn
		elif currentPass in data or newMsg in data:
			#print('currentPass or newMsg detected')
			#print('data: ',data)
			userIn = getpass.getpass("")
			reply = data + formatReply + userIn
		elif pwMsg1 in data or pwMsg2 in data:
			#print('pwMsg1 or psMsg2 detected')
			#print('datat: ',data)
			pw = getpass.getpass("")
			reply = data + pw
		else:
			if newMsgFlag == 0 and not newMsgRecved in data:
				userIn = raw_input()	
				reply = data + userIn
	
		if newMsgFlag == 1:
			newMsgFlag = 0
		else: 	
			# Repond to sender
			s.sendall(reply)