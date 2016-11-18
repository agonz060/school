#! /usr/bin/env python2
import socket
import sys
import time

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


while(1) :
	# Receive input from server (data,addr)
	data = s.recv(1024)
	print(data)
	
	userIn = raw_input()	
	
	reply = data + userIn
	
	# Repond to sender
	s.sendall(reply)
