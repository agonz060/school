#! /usr/bin/env python2
import socket
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
menuMsg = "Welcome"
currentPass = "current"
newMsg = "new"
loggingOut = "logging out"
formatReply = '\n'
while(1) :
	userIn = ""
	# Receive input from server (data,addr)
	data = s.recv(1024)
	print(data)

	if loggingOut in data:
		s.close()
		break
	if currentPass in data or newMsg in data:
		userIn = getpass.getpass("")
		reply = data + formatReply + userIn
	elif pwMsg1 in data or pwMsg2 in data:
		pw = getpass.getpass("")
		reply = data + pw
	elif menuMsg in data:
		userIn = raw_input()
		reply = data + formatReply + userIn
	else:
		userIn = raw_input()	
		reply = data + userIn
	
	# Repond to sender
	s.sendall(reply)